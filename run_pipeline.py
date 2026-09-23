"""One command generates, cleans, verifies and publishes the analytical application data."""

import argparse
import json
import logging
import sqlite3
import sys
import time

import pandas as pd

from database.database import publish
from src.data_cleaning import clean
from src.data_generation import generate, introduce_issues
from src.feature_engineering import enrich
from src.forecast import forecast
from src.funnel_analysis import funnel
from src.kpi_engine import kpis, target_analysis
from src.recommendations import recommendations
from src.reporting import portfolio_results
from src.risk_engine import score
from src.scenario_engine import scenario
from src.statistics import statistical_analysis
from src.utils import ROOT, config, inr
from src.validation import validate

LOG = logging.getLogger("pipeline")


def run(force: bool = False) -> dict:
    """Reuse matching raw files; fail safely with a repair command for corrupt input."""
    started = time.perf_counter()
    cfg = config()
    for directory in ["data/raw", "data/processed", "data/sample", "reports", "screenshots"]:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "data/raw/manifest.json"
    if not force and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["config"] != cfg:
            raise ValueError(
                "Configuration changed. Run python run_pipeline.py --regenerate to rebuild."
            )
        LOG.info("Loading previously generated raw tables")
        tables = {
            name: pd.read_parquet(ROOT / f"data/raw/{name}.parquet") for name in manifest["tables"]
        }
    else:
        LOG.info("Generating %s opportunities with seed %s", cfg["dataset_size"], cfg["seed"])
        tables = introduce_issues(
            generate(cfg["dataset_size"], cfg["seed"], cfg["as_of"], cfg["history_start"]),
            cfg["seed"],
        )
        for name, frame in tables.items():
            frame.to_parquet(ROOT / f"data/raw/{name}.parquet", index=False)
        manifest_path.write_text(json.dumps({"config": cfg, "tables": list(tables)}, indent=2))
    raw_counts = {name: len(frame) for name, frame in tables.items()}
    tables, quality_report, quarantine = clean(tables, cfg["as_of"])
    LOG.info("Cleaned data: %s quarantined opportunities", len(quarantine))
    validate(tables, cfg["as_of"])
    tables = enrich(tables, cfg["as_of"])
    tables["opportunities"] = score(tables["opportunities"], cfg["as_of"], cfg["stage_limits"])
    o, h = tables["opportunities"], tables["stage_history"]
    summary = kpis(o)
    tables["funnel"] = funnel(o, h)
    tables["recommendations"] = recommendations(o, h, cfg["as_of"], tables["targets"])
    LOG.info("Running rolling-origin forecast and regional evaluations")
    f, evaluation, backtest, actuals = forecast(o, h, tables["targets"], cfg)
    tables.update(forecast=f, forecast_metrics=evaluation, backtest=backtest, actuals=actuals)
    regional = []
    for region, group in o.groupby("region"):
        _, regional_metrics, regional_bt, _ = forecast(
            group,
            h[h.opportunity_id.isin(group.opportunity_id)],
            tables["targets"][tables["targets"].region.eq(region)],
            cfg,
        )
        selected = regional_metrics.loc[regional_metrics.selected, "model"].iloc[0]
        regional.append(regional_bt.assign(region=region, selected=regional_bt.model.eq(selected)))
    tables["regional_backtest"] = pd.concat(regional, ignore_index=True)
    intervals, statistics_text = statistical_analysis(o)
    tables["source_statistics"] = intervals
    tables["data_quality"] = quality_report
    target = f.head(3).target.sum()
    scenarios = pd.DataFrame(
        [
            {"scenario": "Baseline", **scenario(o, target, cfg["as_of"])},
            {
                "scenario": "+5pp win, 10% faster cycle",
                **scenario(o, target, cfg["as_of"], win_adjust=0.05, cycle_adjust=-0.1),
            },
        ]
    )
    tables["scenario_examples"] = scenarios
    # Calendar analysis has its own prefixes, preserving all-time cohort KPIs.
    summary = {
        **kpis(o),
        **{
            f"ytd_{k}": v
            for k, v in target_analysis(
                o,
                tables["targets"],
                pd.Timestamp(cfg["as_of"]).replace(month=1, day=1),
                pd.Timestamp(cfg["as_of"]),
            ).items()
        },
    }
    tables["pipeline_kpis"] = pd.DataFrame([summary])
    LOG.info("Publishing SQLite warehouse and executing every business SQL query")
    publish(tables)
    for name, frame in tables.items():
        frame.to_parquet(ROOT / f"data/processed/{name}.parquet", index=False)
    quarantine.to_csv(ROOT / "data/processed/quarantine.csv", index=False)
    for name in [
        "forecast",
        "forecast_metrics",
        "backtest",
        "regional_backtest",
        "pipeline_kpis",
        "funnel",
        "recommendations",
        "source_statistics",
        "scenario_examples",
    ]:
        tables[name].to_csv(ROOT / f"reports/{name}.csv", index=False)
    quality_report.to_csv(ROOT / "reports/data_quality_report.csv", index=False)
    o.head(1000).to_csv(ROOT / "data/sample/opportunities.csv", index=False)
    qtext = "# Data quality report\n\nAll percentages are records affected divided by raw/clean opportunity rows; classes overlap.\n\n"
    qtext += "```text\n" + quality_report.to_string(index=False) + "\n```\n\n"
    qtext += f"Raw opportunities: {raw_counts['opportunities']:,}. Clean: {len(o):,}. Quarantined: {len(quarantine):,}. "
    qtext += f"Customer duplicate rows removed: {raw_counts['customers'] - len(tables['customers']):,}.\n\n"
    qtext += "Duplicate IDs retain the first occurrence (injected duplicates are exact). Customer master restores geography and industry; account ownership restores missing representatives. Stage-event evidence restores chronology and stage/status. Financial identities are recomputed. Invalid gross amounts/discounts are quarantined, never invented. Dependent fact rows are excluded consistently. Optional nulls (open close dates, missing future actions) remain legitimate. Source provenance is defined in docs/METHODOLOGY.md.\n"
    (ROOT / "DATA_QUALITY_REPORT.md").write_text(qtext, encoding="utf-8")
    (ROOT / "reports/statistical_analysis.md").write_text(statistics_text, encoding="utf-8")
    selected = evaluation[evaluation.selected & evaluation.split.eq("test")].iloc[0]
    (ROOT / "reports/forecast_evaluation.md").write_text(
        "# Forecast evaluation\n\nCalculated from the generated dataset.\n\n"
        f"Selected on validation WAPE: {selected.model}. Held-out six-month WAPE: {selected.wape:.2%}; MAE: {inr(selected.mae)}; RMSE: {inr(selected.rmse)}; bias: {inr(selected.bias_inr)}.\n\n"
        "See forecast_metrics.csv for every candidate and backtest.csv for every origin. Validation is the first six of the final twelve complete historical months; test is the later six. Each origin uses only earlier closed outcomes and stage entries. WAPE gives an aggregate business-scale error; MAPE excludes zero actual months and is reported with their count. "
        "The future horizon is twelve months; only one-month forecasts are backtested. Range width uses the validation 80th percentile absolute error and square-root horizon scaling; it is indicative, not a calibrated confidence guarantee. "
        "Future variance is undefined until actuals exist. Closed-won future contribution is zero because these are future complete months. "
        "Pipeline blends are genuine candidates, but a history-only model may win; current pipeline remains a separately reported commercial cross-check. Revenue means booked net contract value, not recognized accounting revenue or collected cash.\n",
        encoding="utf-8",
    )
    insights = "# Business insights\n\nCalculated from the generated dataset. Exposure is not an estimated recovery.\n\n"
    for row in tables["recommendations"].itertuples():
        insights += f"## {row.problem}\n\nObservation: {row.problem}.\n\nEvidence: {row.evidence}.\n\nBusiness impact: {row.business_impact}.\n\nRecommendation: {row.recommendation}. Owner: {row.owner}; priority: {row.priority}.\n\n"
    insights += f"## Forecast and concentration\n\nObservation: compare the next three months with the configured target.\n\nEvidence: forecast {inr(f.head(3).forecast.sum())}; target {inr(target)}; gap {inr(target - f.head(3).forecast.sum())}. Top ten open deals represent {summary['top10_pipeline_share']:.2%} of current face-value pipeline.\n\nBusiness impact: gap is a planning requirement, not proof that revenue will be lost.\n\nRecommendation: reconcile the model with dated close plans and capacity before altering quota.\n"
    (ROOT / "reports/business_insights.md").write_text(insights, encoding="utf-8")
    manifest = {
        "config": cfg,
        "raw_rows": raw_counts,
        "clean_rows": {name: len(frame) for name, frame in tables.items()},
        "quarantined": len(quarantine),
        "selected_model": selected.model,
        "test_wape": selected.wape,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "sql_queries": 42,
        "kpis": summary,
        "forecast_next3": float(f.head(3).forecast.sum()),
    }
    (ROOT / "reports/run_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=float), encoding="utf-8"
    )
    portfolio_results(tables, cfg, summary, raw_counts, len(quarantine))
    required = [
        "database/sales.db",
        "reports/forecast.csv",
        "reports/pipeline_kpis.csv",
        "DATA_QUALITY_REPORT.md",
        "reports/business_insights.md",
        "data/processed/opportunities.parquet",
    ]
    if not all((ROOT / p).exists() and (ROOT / p).stat().st_size > 0 for p in required):
        raise RuntimeError("Required artifact missing or empty.")
    LOG.info("Validated and published in %.1f seconds", time.perf_counter() - started)
    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Replace raw synthetic data using current configuration",
    )
    try:
        run(parser.parse_args().regenerate)
    except (ValueError, OSError, KeyError, sqlite3.Error, pd.errors.ParserError) as exc:
        LOG.error(
            "Pipeline did not publish a valid new run: %s. Check config/data; to replace corrupt synthetic input use --regenerate.",
            exc,
        )
        sys.exit(1)
