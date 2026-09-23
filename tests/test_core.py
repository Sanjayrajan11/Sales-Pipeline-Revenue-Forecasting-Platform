"""Business invariants, numerical expectations and adversarial boundary cases."""

import numpy as np
import pandas as pd
import pytest

from src.data_cleaning import clean
from src.data_generation import generate
from src.feature_engineering import stage_probabilities
from src.forecast import baseline, forecast, metrics, monthly_actual, snapshot_pipeline
from src.funnel_analysis import funnel
from src.kpi_engine import kpis, target_analysis
from src.recommendations import recommendations
from src.risk_engine import score
from src.scenario_engine import scenario
from src.utils import inr, ratio
from src.validation import quality, validate


def test_generation_reproducible():
    a = generate(100, 9, "2026-08-31", "2023-01-01")
    b = generate(100, 9, "2026-08-31", "2023-01-01")
    pd.testing.assert_frame_equal(a["opportunities"], b["opportunities"])


def test_generation_size_and_keys(raw):
    assert len(raw["opportunities"]) == 1200
    assert raw["opportunities"].opportunity_id.is_unique
    assert raw["activities"].opportunity_id.isin(raw["opportunities"].opportunity_id).all()


def test_advanced_activities_require_observed_stage(raw):
    for kind, stage in [
        ("Product Demo", "Demo"),
        ("Proposal", "Proposal"),
        ("Contract Review", "Negotiation"),
    ]:
        activities = raw["activities"][raw["activities"].activity_type.eq(kind)]
        reached = (
            raw["stage_history"][raw["stage_history"].sales_stage.eq(stage)]
            .set_index("opportunity_id")
            .entry_date
        )
        assert (activities.activity_date >= activities.opportunity_id.map(reached)).all()


def test_segment_value_relationship(raw):
    medians = raw["opportunities"].groupby("customer_segment").opportunity_amount.median()
    assert medians.Enterprise > medians.SMB * 3


def test_censoring(raw):
    h = raw["stage_history"]
    assert (h.entry_date <= pd.Timestamp("2026-08-31")).all()
    assert (h.exit_date.dropna() <= pd.Timestamp("2026-08-31")).all()
    assert h.exit_date.isna().any()


def test_early_dropout(raw):
    lost = raw["stage_history"].query("exit_to == 'Closed Lost'")
    assert lost.stage_order.min() == 0
    assert lost.stage_order.nunique() > 2


def test_cleaning_removes_duplicates(dirty):
    tables, audit, _ = clean(dirty, "2026-08-31")
    assert tables["opportunities"].opportunity_id.is_unique
    assert tables["customers"].customer_id.is_unique
    assert (
        audit.query("phase == 'raw' and check == 'duplicate_opportunity'").affected_records.iloc[0]
        > 0
    )


def test_invalid_financials_quarantined(dirty):
    tables, _, q = clean(dirty, "2026-08-31")
    assert len(q) > 0
    assert not q.opportunity_id.isin(tables["opportunities"].opportunity_id).any()
    assert not tables["activities"].opportunity_id.isin(q.opportunity_id).any()


def test_quality_after_repairs(clean_tables):
    validate(clean_tables, "2026-08-31")
    assert quality(clean_tables["opportunities"]).affected_records.sum() == 0


def test_validation_rejects_orphans(clean_tables):
    tables = {k: v.copy() for k, v in clean_tables.items()}
    tables["opportunities"].loc[0, "customer_id"] = -99
    with pytest.raises(ValueError, match="Orphan customer"):
        validate(tables, "2026-08-31")


def test_money_identity(clean_tables):
    o = clean_tables["opportunities"]
    np.testing.assert_allclose(
        o.net_deal_value, (o.opportunity_amount * (1 - o.discount_percentage / 100)).round(2)
    )


def test_cycle_from_dates(clean_tables):
    o = clean_tables["opportunities"]
    np.testing.assert_allclose(
        o.sales_cycle_days, (o.actual_close_date - o.created_date).dt.days, equal_nan=True
    )


def test_kpi_partition(clean_tables):
    k = kpis(clean_tables["opportunities"])
    assert k["pipeline_value"] == pytest.approx(
        k["closed_won_revenue"] + k["closed_lost_value"] + k["open_pipeline"]
    )
    assert k["weighted_pipeline"] <= k["open_pipeline"]


def test_win_rate_resolved_only(clean_tables):
    o = clean_tables["opportunities"].iloc[:4].copy()
    o["deal_status"] = ["Closed Won", "Closed Lost", "Open", "Stalled"]
    assert kpis(o)["win_rate"] == 0.5
    assert kpis(o)["lead_to_win_rate"] == 0.25


def test_empty_denominator():
    assert np.isnan(ratio(100, 0))


def test_inr_grouping():
    assert inr(12345678) == "₹1,23,45,678"
    assert inr(-250000) == "-₹2,50,000"
    assert inr(np.nan) == "N/A"


def test_funnel_counts_and_censoring(clean_tables):
    f = funnel(clean_tables["opportunities"], clean_tables["stage_history"])
    assert (f.entered == f.advanced + f.lost + f.pending).all()
    expected = f.advanced / f.exited.replace(0, np.nan)
    np.testing.assert_allclose(f.conversion, expected, equal_nan=True)


def test_funnel_cohort_filter(clean_tables):
    o = clean_tables["opportunities"].head(10)
    f = funnel(o, clean_tables["stage_history"])
    assert f.iloc[0].entered == 10


def test_stage_probability_no_future_leak(clean_tables):
    o = clean_tables["opportunities"].copy()
    cutoff = pd.Timestamp("2025-01-01")
    a = stage_probabilities(o, clean_tables["stage_history"], cutoff)
    o.loc[o.actual_close_date > cutoff, "deal_status"] = "Closed Won"
    b = stage_probabilities(o, clean_tables["stage_history"], cutoff)
    pd.testing.assert_series_equal(a, b)


def test_snapshot_ignores_future_stage_and_outcomes(clean_tables):
    o = clean_tables["opportunities"].copy()
    cutoff = pd.Timestamp("2025-01-31")
    months = pd.date_range("2025-02-01", periods=3, freq="MS")
    a = snapshot_pipeline(o, clean_tables["stage_history"], cutoff, months)
    o["sales_stage"] = "Closed Won"
    o.loc[o.actual_close_date > cutoff, "deal_status"] = "Closed Won"
    b = snapshot_pipeline(o, clean_tables["stage_history"], cutoff, months)
    np.testing.assert_allclose(a, b)


def test_forecast_metrics_exact():
    result = metrics(np.array([100, 200]), np.array([110, 180]))
    assert result["mae"] == 15
    assert result["rmse"] == pytest.approx(np.sqrt(250))
    assert result["wape"] == 0.1
    assert result["bias_inr"] == -5


def test_mape_zero_actual_handled():
    result = metrics(np.array([0, 100]), np.array([10, 110]))
    assert result["mape"] == 0.1
    assert result["zero_actual_months"] == 1


def test_baselines_exact():
    s = pd.Series([10.0, 20.0, 30.0])
    assert baseline(s, "MA3")[0] == 20
    assert baseline(s, "SES")[0] == pytest.approx(18.1)
    with pytest.raises(ValueError):
        baseline(s.iloc[:1], "MA3")


def test_forecast_split_and_reconciliation(clean_tables):
    cfg = {"as_of": "2026-08-31", "history_start": "2023-01-01", "forecast_months": 12}
    f, e, b, _ = forecast(
        clean_tables["opportunities"], clean_tables["stage_history"], clean_tables["targets"], cfg
    )
    assert len(f) == 12
    assert b[b.split.eq("validation")].period.max() < b[b.split.eq("test")].period.min()
    winner = e[e.split.eq("validation")].sort_values(["wape", "mae"]).iloc[0].model
    assert f.iloc[0].model == winner
    np.testing.assert_allclose(f.forecast, f.baseline_component + f.weighted_pipeline_component)
    assert (f.lower <= f.forecast).all() and (f.upper >= f.forecast).all()


def test_monthly_calendar_fills_zeros(clean_tables):
    s = monthly_actual(clean_tables["opportunities"].iloc[:0], "2025-01-01", "2025-03-31")
    assert len(s) == 3 and s.sum() == 0


def test_partial_month_forecast_calendar_and_seasonal_alignment(clean_tables):
    cfg = {'as_of': '2026-08-15', 'history_start': '2023-01-01', 'forecast_months': 12}
    o, h = clean_tables['opportunities'], clean_tables['stage_history']
    result, _, _, actuals = forecast(o, h, clean_tables['targets'], cfg)
    assert actuals.period.max() == pd.Timestamp('2026-07-01')
    assert result.period.min() == pd.Timestamp('2026-09-01')
    method = result.model.iloc[0].split(' + ')[0]
    expected = baseline(actuals.actual, method, 13)[1:]
    np.testing.assert_allclose(result.historical_baseline, expected)


def test_risk_bounds_and_closed_exclusion(clean_tables):
    o = clean_tables["opportunities"]
    assert o.risk_score.between(0, 100).all()
    assert o.loc[o.deal_status.str.startswith("Closed"), "risk_score"].eq(0).all()
    assert o.health_score.dropna().between(0, 100).all()


def test_risk_monotonic_for_activity(clean_tables):
    o = clean_tables["opportunities"].query("deal_status == 'Open'").head(1).copy()
    o["activity_gap_days"] = 0
    a = score(o, "2026-08-31", [14, 18, 21, 18, 28, 21])
    o["activity_gap_days"] = 50
    b = score(o, "2026-08-31", [14, 18, 21, 18, 28, 21])
    assert b.risk_score.iloc[0] - a.risk_score.iloc[0] == 15
    assert "No recent activity" in b.risk_drivers.iloc[0]


def test_health_components_sum(clean_tables):
    o = clean_tables["opportunities"].query("deal_status in ['Open', 'Stalled']")
    columns = [
        c for c in o if c.startswith("health_") and c not in ["health_score", "health_category"]
    ]
    np.testing.assert_allclose(o.health_score, o[columns].sum(axis=1).round(1))


def test_scenario_baseline_exact(clean_tables):
    o = clean_tables["opportunities"]
    active = o[
        o.deal_status.isin(["Open", "Stalled"])
        & (o.expected_close_date <= pd.Timestamp("2026-11-29"))
    ]
    s = scenario(o, 1000000, "2026-08-31")
    expected = (
        active.opportunity_amount * (1 - active.discount_percentage / 100) * active.win_probability
    ).sum()
    assert s["projected_revenue"] == pytest.approx(expected)


def test_scenario_win_monotonic(clean_tables):
    o = clean_tables["opportunities"]
    assert (
        scenario(o, 1000000, "2026-08-31", win_adjust=0.1)["projected_revenue"]
        >= scenario(o, 1000000, "2026-08-31")["projected_revenue"]
    )


def test_scenario_discount_decreases_bookings(clean_tables):
    o = clean_tables["opportunities"]
    assert (
        scenario(o, 1000000, "2026-08-31", discount_adjust=0.1)["projected_revenue"]
        <= scenario(o, 1000000, "2026-08-31")["projected_revenue"]
    )


def test_scenario_target_not_revenue(clean_tables):
    o = clean_tables["opportunities"]
    a, b = scenario(o, 100, "2026-08-31"), scenario(o, 100, "2026-08-31", target_adjust=0.1)
    assert a["projected_revenue"] == b["projected_revenue"]
    assert b["target"] == pytest.approx(110)


def test_scenario_invalid_input(clean_tables):
    with pytest.raises(ValueError):
        scenario(clean_tables["opportunities"], 1, "2026-08-31", cycle_adjust=-1)


def test_target_period_alignment(clean_tables):
    o = clean_tables["opportunities"]
    t = clean_tables["targets"]
    x = target_analysis(o, t, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-31"))
    assert x["target"] == t[t.period.eq(pd.Timestamp("2026-01-01"))].target.sum()
    assert (
        x["actual"]
        == o[
            o.actual_close_date.between("2026-01-01", "2026-01-31") & o.deal_status.eq("Closed Won")
        ].net_deal_value.sum()
    )


def test_recommendation_evidence_reconciles(clean_tables):
    o = clean_tables["opportunities"]
    r = recommendations(o, clean_tables["stage_history"], "2026-08-31")
    stale = o[o.deal_status.isin(["Open", "Stalled"]) & (o.activity_gap_days > 21)]
    if len(stale):
        assert r[r.problem.eq("Stale opportunities")].exposure_inr.iloc[0] == pytest.approx(
            stale.net_deal_value.sum()
        )
    assert r.recommendation.str.len().min() > 10
