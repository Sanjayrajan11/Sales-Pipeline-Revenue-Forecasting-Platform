"""Rolling-origin bookings forecast with reconstructed point-in-time pipeline."""

import numpy as np
import pandas as pd

from src.feature_engineering import stage_probabilities
from src.utils import ratio


def monthly_actual(o: pd.DataFrame, start: str, end: str) -> pd.Series:
    """Include zero-booking months and exclude incomplete months at the caller."""
    won = o[o.deal_status.eq("Closed Won")].copy()
    won["period"] = won.actual_close_date.dt.to_period("M").dt.to_timestamp()
    months = pd.date_range(
        pd.Timestamp(start).replace(day=1), pd.Timestamp(end).replace(day=1), freq="MS"
    )
    return won.groupby("period").net_deal_value.sum().reindex(months, fill_value=0).astype(float)


def baseline(history: pd.Series, method: str, horizon: int = 1) -> np.ndarray:
    """Explainable MA3, SES(alpha=.3), and seasonal-naive baselines."""
    values = history.to_numpy(dtype=float)
    if len(values) < 3:
        raise ValueError("Forecast requires at least three complete historical months.")
    if method == "MA3":
        return np.repeat(values[-3:].mean(), horizon)
    if method == "SES":
        level = values[0]
        for value in values[1:]:
            level = 0.3 * value + 0.7 * level
        return np.repeat(level, horizon)
    if method == "Seasonal naive":
        return (
            np.resize(values[-12:], horizon)
            if len(values) >= 12
            else np.repeat(values.mean(), horizon)
        )
    raise ValueError(f"Unknown forecast method: {method}")


def snapshot_pipeline(
    o: pd.DataFrame, h: pd.DataFrame, cutoff: pd.Timestamp, months: pd.DatetimeIndex
) -> np.ndarray:
    """Reconstruct only deals/stages observable at cutoff; overdue dates roll forward.

    Expected close date and initial deal amount are immutable simulated CRM
    fields. No final stage, activity, risk score or post-cutoff outcomes enter.
    """
    opened = o[
        (o.created_date <= cutoff) & (o.actual_close_date.isna() | (o.actual_close_date > cutoff))
    ].copy()
    if opened.empty:
        return np.zeros(len(months))
    visits = (
        h[h.entry_date <= cutoff]
        .sort_values(["opportunity_id", "entry_date"])
        .groupby("opportunity_id")
        .tail(1)
        .set_index("opportunity_id")
    )
    p = stage_probabilities(o, h, cutoff)
    opened["probability"] = opened.opportunity_id.map(visits.sales_stage).map(p).fillna(0.5)
    opened["period"] = (
        opened.expected_close_date.dt.to_period("M").dt.to_timestamp().clip(lower=months[0])
    )
    opened["contribution"] = opened.net_deal_value * opened.probability
    return opened.groupby("period").contribution.sum().reindex(months, fill_value=0).to_numpy()


def metrics(actual: np.ndarray, predicted: np.ndarray) -> dict:
    """Report currency errors, aggregate WAPE and signed bias; MAPE omits zero actuals."""
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    error = predicted - actual
    nonzero = actual != 0
    return {
        "mae": float(np.abs(error).mean()),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "wape": ratio(np.abs(error).sum(), np.abs(actual).sum()),
        "mape": float(np.mean(np.abs(error[nonzero] / actual[nonzero])))
        if nonzero.any()
        else np.nan,
        "bias_inr": float(error.mean()),
        "bias_pct": ratio(error.sum(), actual.sum()),
        "zero_actual_months": int((~nonzero).sum()),
    }


def forecast(
    o: pd.DataFrame, h: pd.DataFrame, targets: pd.DataFrame, cfg: dict
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Select on six validation origins and evaluate on six untouched test origins.

    Candidates are baseline or convex baseline/pipeline blends. Intervals use
    validation absolute errors only and widen with sqrt(horizon); indicative,
    not calibrated probability intervals. Bookings are not accounting revenue.
    """
    as_of = pd.Timestamp(cfg["as_of"])
    last_complete = as_of if as_of.is_month_end else as_of.replace(day=1) - pd.Timedelta(days=1)
    series = monthly_actual(o, cfg["history_start"], str(last_complete.date()))
    if len(series) < 24:
        raise ValueError(
            "Backtesting requires 24 complete months, including 12 evaluation origins."
        )
    predictions = []
    for i in range(len(series) - 12, len(series)):
        month = series.index[i]
        cutoff = month - pd.Timedelta(days=1)
        pipe = snapshot_pipeline(o, h, cutoff, pd.DatetimeIndex([month]))[0]
        for method in ["MA3", "SES", "Seasonal naive"]:
            base = baseline(series.iloc[:i], method)[0]
            for weight in [0.0, 0.25, 0.5]:
                predictions.append(
                    {
                        "period": month,
                        "cutoff": cutoff,
                        "split": "validation" if i < len(series) - 6 else "test",
                        "model": f"{method} + {weight:.0%} pipeline",
                        "method": method,
                        "pipeline_weight": weight,
                        "actual": series.iloc[i],
                        "forecast": (1 - weight) * base + weight * pipe,
                        "pipeline": pipe,
                    }
                )
    backtest = pd.DataFrame(predictions)
    evaluation = pd.DataFrame(
        [
            {"model": model, "split": split, **metrics(g.actual.to_numpy(), g.forecast.to_numpy())}
            for (model, split), g in backtest.groupby(["model", "split"])
        ]
    )
    selected = (
        evaluation[evaluation.split.eq("validation")].sort_values(["wape", "mae"]).iloc[0].model
    )
    evaluation["selected"] = evaluation.model.eq(selected)
    specification = backtest[backtest.model.eq(selected)].iloc[0]
    # A partial snapshot month is not a complete future booking period. Skip it
    # in both the calendar and baseline horizon so seasonal values stay aligned.
    skipped_months = int(not as_of.is_month_end)
    months = pd.date_range(
        as_of + pd.offsets.MonthBegin(1), periods=cfg["forecast_months"], freq="MS"
    )
    pipeline = snapshot_pipeline(o, h, as_of, months)
    base = baseline(series, specification.method, len(months) + skipped_months)[skipped_months:]
    projected = (
        base * (1 - specification.pipeline_weight) + pipeline * specification.pipeline_weight
    )
    calibration = backtest[backtest.model.eq(selected) & backtest.split.eq("validation")]
    width = np.quantile(np.abs(calibration.forecast - calibration.actual), 0.8) * np.sqrt(
        np.arange(1 + skipped_months, len(months) + 1 + skipped_months)
    )
    result = pd.DataFrame(
        {
            "period": months,
            "forecast": projected,
            "lower": np.maximum(0, projected - width),
            "upper": projected + width,
            "historical_baseline": base,
            "pipeline_contribution": pipeline,
            "weighted_pipeline_component": pipeline * specification.pipeline_weight,
            "baseline_component": base * (1 - specification.pipeline_weight),
            "closed_won_contribution": np.zeros(len(months)),
            "model": selected,
            "confidence_indicator": "Indicative range; 6 calibration origins, uncalibrated long horizon",
        }
    )
    result["target"] = result.period.map(targets.groupby("period").target.sum()).fillna(0)
    result["gap_to_target"] = result.target - result.forecast
    result["expected_attainment"] = result.forecast / result.target.replace(0, np.nan)
    result["forecast_variance"] = np.nan  # Future actuals do not yet exist.
    actuals = series.rename("actual").rename_axis("period").reset_index()
    actuals["target"] = actuals.period.map(targets.groupby("period").target.sum()).fillna(0)
    return result, evaluation, backtest, actuals
