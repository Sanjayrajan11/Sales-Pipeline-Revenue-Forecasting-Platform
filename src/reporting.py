"""Portfolio evidence generated from executed data, never fabricated business outcomes."""

import pandas as pd

from src.utils import ACTIVE, ROOT, inr

FIELD_NOTES = {
    "opportunity_id": "Unique sales opportunity key; opportunity table grain",
    "customer_id": "Customer master foreign key",
    "account_id": "Account key; one account per customer in this model",
    "customer_name": "Explicitly synthetic enterprise display name",
    "sales_rep_id": "Representative key / opportunity owner",
    "sales_team_id": "Regional commercial team key",
    "sales_rep_name": "Simulated representative display label",
    "team": "Regional commercial team name",
    "manager": "Simulated regional manager label",
    "territory": "Assigned sales region",
    "experience_years": "Representative experience in whole years",
    "hire_date": "Simulated rep employment start",
    "monthly_target": "Planning quota per rep-month in INR; scaled with dataset size",
    "annual_target": "Twelve times representative monthly quota, INR",
    "created_date": "Opportunity creation / first Lead entry date",
    "expected_close_date": "Immutable initial expected contract close date; may be overdue",
    "actual_close_date": "Observed terminal event date; null for Open/Stalled",
    "opportunity_amount": "Gross contract face value, INR",
    "discount_percentage": "Discount in percentage points, e.g. 10 means 10%",
    "net_deal_value": "Gross × (1 − discount/100), rounded to INR paisa",
    "sales_stage": "Current stage on opportunity, visited stage on history",
    "previous_stage": "Immediately preceding observed stage, or None at Lead",
    "stage_entry_date": "Start of current stage; terminal date on closed deals",
    "days_in_current_stage": "Snapshot-minus-entry for active deals; zero for terminal current stage",
    "total_opportunity_age_days": "Days from creation until snapshot or observed close",
    "lead_source": "Referral / Partner / Inbound / Outbound / Event",
    "industry": "Simulated account commercial industry",
    "customer_segment": "SMB / Mid-market / Enterprise",
    "company_size": "Simulated employee count; input to deal value",
    "region": "North / South / East / West India",
    "city": "City from geography master",
    "state": "State from geography master, consistent with city/region",
    "product_id": "Product catalogue key",
    "product": "Technology/service product label",
    "product_category": "Software or Services",
    "base_price": "Catalogue base price, INR",
    "contract_type": "Annual / Multi-year / Project; value is total booked contract value",
    "deal_type": "New business / Renewal / Expansion",
    "new_or_existing_customer": "Relationship at opportunity creation; immutable simulated attribute",
    "existing_customer": "Boolean previous-customer relationship; not based on future outcomes",
    "competitor_present": "Boolean known competitor indicator",
    "competitor_name": "Synthetic A/B/C competitor or None",
    "decision_makers_count": "Number of participants in buying decision",
    "engagement_score": "Generated 0–100 engagement index; drives probabilistic behavior",
    "meeting_count": "Observed Meeting activity count",
    "email_count": "Observed Email activity count",
    "call_count": "Observed Phone Call activity count",
    "demo_count": "Observed Product Demo activity count",
    "follow_up_count": "Observed Follow-up activity count",
    "proposal_sent": "Boolean stage-history evidence of reaching Proposal",
    "last_activity_date": "Latest observed activity event date for the deal",
    "next_follow_up_date": "Scheduled next action; may be null or overdue",
    "activity_gap_days": "Days from latest activity to snapshot or observed close",
    "sales_cycle_days": "Observed actual close minus creation in days; null on active deals",
    "deal_status": "Closed Won / Closed Lost / Open / Stalled",
    "lost_reason": "Terminal loss reason, empty string for non-lost deals",
    "win_probability": "Resolved-stage historical Beta(1,1) estimate; 1/0 on won/lost",
    "weighted_value": "Active net contract value × historical stage probability; zero if closed",
    "forecast_category": "Mutually exclusive Commit / Best Case / Pipeline / Closed Won / Excluded",
    "quarter": "Calendar creation quarter, 1–4",
    "month": "Calendar creation month, 1–12",
    "year": "Calendar creation year",
    "customer_since": "Date synthetic account was known to the business",
    "annual_revenue_band": "Simulated company annual-revenue size band, not project bookings",
    "customer_lifetime_value": "Sum of observed won net contracts in modeled history; not predictive CLV",
    "active_products": "Distinct products ever won in modeled history; not verified active subscriptions",
    "account_manager": "Authoritative account-owner representative key",
    "customer_health_score": "Generated 35–95 customer relationship attribute, separate from deal health",
    "activity_id": "Unique activity event key",
    "activity_date": "Observed interaction date within deal lifetime",
    "activity_type": "Email / Phone Call / Meeting / Product Demo / Proposal / Negotiation / Follow-up / Contract Review",
    "duration_minutes": "Simulated interaction duration in minutes",
    "outcome": "Engaged or No response",
    "transition_id": "Unique stage visit key",
    "stage_order": "Zero-based forward process order",
    "entry_date": "Observed stage entry date",
    "exit_date": "Observed exit or null if right-censored",
    "exit_to": "Next stage or terminal outcome; empty while pending",
    "duration_days": "Completed visit duration or censored elapsed duration",
    "contract_id": "Won contract key, one per won opportunity",
    "period": "Calendar month start / forecast period",
    "target": "Representative or aggregate monthly quota, INR",
    "risk_score": "Sum of triggered policy points, 0–100; not a loss probability",
    "risk_level": "Low / Medium / High / Critical; Closed is excluded from actioning",
    "risk_drivers": "Semicolon-separated triggered risk-rule names",
    "recommended_action": "Rule-linked operational actions; no CRM write-back is performed",
    "health_score": "Sum of eight equally weighted bounded components; null for closed deals",
    "health_category": "Healthy / Watch / At risk / Closed",
    "forecast_risk_value": "Weighted pipeline × risk score/100; prioritization exposure, not calibrated expected loss",
}


def markdown_table(frame: pd.DataFrame) -> str:
    """Produce compact Markdown without an extra formatting dependency."""
    header = "| " + " | ".join(map(str, frame.columns)) + " |\n"
    separator = "| " + " | ".join("---" for _ in frame.columns) + " |\n"
    body = "\n".join(
        "| " + " | ".join(str(v).replace("|", "/") for v in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    )
    return header + separator + body


def portfolio_results(
    tables: dict, cfg: dict, summary: dict, raw_counts: dict, quarantined: int
) -> None:
    """Write dictionary, factual results and role-specific resume variants after execution."""
    o = tables["opportunities"]
    active = o[o.deal_status.isin(ACTIVE)]
    f = tables["forecast"]
    e = tables["forecast_metrics"]
    selected = e[e.selected & e.split.eq("test")].iloc[0]
    core = [
        "customers",
        "accounts",
        "sales_reps",
        "sales_teams",
        "products",
        "regions",
        "industries",
        "lead_sources",
        "stages",
        "opportunities",
        "activities",
        "stage_history",
        "contracts",
        "targets",
        "forecast_periods",
        "lost_reasons",
        "competitors",
    ]
    dictionary = "# Data dictionary\n\nAll data is synthetic. Currency is INR. Empty closed dates are valid for active deals. SQLite stores booleans as 0/1 and dates as ISO text; Parquet preserves logical types.\n\n"
    for name in core:
        frame = tables[name]
        dictionary += f"## {name} — {len(frame):,} rows\n\n| Field | Pandas type | Definition / unit |\n| --- | --- | --- |\n"
        for col in frame:
            meaning = FIELD_NOTES.get(col)
            if meaning is None and col.startswith("health_"):
                meaning = f"{col.removeprefix('health_').replace('_', ' ').capitalize()} health contribution, 0–12.5 points; see BUSINESS_RULES.md"
            if meaning is None:
                raise ValueError(f"Missing dictionary definition: {name}.{col}")
            dictionary += f"| {col} | {frame[col].dtype} | {meaning} |\n"
        dictionary += "\n"
    dictionary += "## Analytical outputs\n\nDerived KPI, funnel, forecast, backtest, scenario, quality and recommendation tables are defined by KPI_DICTIONARY.md, METHODOLOGY.md and BUSINESS_RULES.md. Forecast errors are INR except WAPE/MAPE/bias_pct fractions. Scenario probabilities and adjustments use the units shown in the application. Each backtest row is one model × forecast origin; filter to the selected model before totaling.\n"
    (ROOT / "docs/DATA_DICTIONARY.md").write_text(dictionary, encoding="utf-8")
    quality = tables["data_quality"]
    raw_quality = quality[quality.phase.eq("raw")][
        ["check", "affected_records", "percentage"]
    ].copy()
    raw_quality["percentage"] = raw_quality.percentage.map(lambda x: f"{x:.3f}%")
    results = "# Executed project results\n\nCalculated from the generated dataset. All data is synthetic; no real-company or recovery result is claimed.\n\n"
    results += f"## Dataset and quality\n\nSnapshot: {cfg['as_of']}; seed: {cfg['seed']}. Generated {cfg['dataset_size']:,} distinct opportunities before defect injection. Raw extract: {raw_counts['opportunities']:,} rows. Clean: {len(o):,}; invalid financial records quarantined: {quarantined:,}. Customer duplicates removed: {raw_counts['customers'] - len(tables['customers']):,}.\n\n"
    results += (
        markdown_table(
            pd.DataFrame([{"Entity": name, "Rows": f"{len(tables[name]):,}"} for name in core])
        )
        + "\n\n"
    )
    results += (
        markdown_table(raw_quality)
        + "\n\nClean records pass every implemented quality check. Classes overlap and must not be added. See DATA_QUALITY_REPORT.md for repair provenance.\n\n"
    )
    results += "## KPI results\n\n"
    money = [
        "pipeline_value",
        "closed_won_revenue",
        "closed_lost_value",
        "open_pipeline",
        "weighted_pipeline",
        "average_deal_size",
        "median_deal_size",
        "ytd_target",
        "ytd_actual",
        "ytd_remaining_target",
    ]
    results += (
        markdown_table(
            pd.DataFrame([{"Metric": key, "Value (INR)": inr(summary[key])} for key in money])
        )
        + "\n\n"
    )
    results += f"Resolved-deal win rate: **{summary['win_rate']:.2%}**. Won cycle mean: {summary['average_sales_cycle']:.1f} days; median: {summary['median_sales_cycle']:.1f} days. Active stale share: {summary['stale_opportunity_rate']:.2%}. Top 5 / 10 / 20 face-value pipeline shares: {summary['top5_pipeline_share']:.2%} / {summary['top10_pipeline_share']:.2%} / {summary['top20_pipeline_share']:.2%}. YTD attainment: {summary['ytd_attainment']:.2%}.\n\n"
    results += (
        "## Pipeline diagnostics\n\n"
        + markdown_table(
            tables["funnel"][
                [
                    "stage",
                    "entered",
                    "exited",
                    "pending",
                    "conversion",
                    "drop_off",
                    "average_days_completed",
                ]
            ].round(4)
        )
        + "\n\n"
    )
    results += "## Forecast and evaluation\n\n"
    results += f"Selected by validation WAPE: **{selected.model}**. Held-out WAPE: **{selected.wape:.2%}**; MAE {inr(selected.mae)}; RMSE {inr(selected.rmse)}; signed bias {inr(selected.bias_inr)}. "
    results += (
        "The pipeline candidates were evaluated but did not beat the selected history-only baseline on validation. "
        if selected.model.endswith("+ 0% pipeline")
        else "A baseline/pipeline blend achieved the lowest validation WAPE. "
    )
    results += "Current weighted pipeline remains a separate cross-check.\n\n"
    forecast_view = f[
        ["period", "forecast", "lower", "upper", "pipeline_contribution", "target", "gap_to_target"]
    ].copy()
    forecast_view["period"] = forecast_view.period.dt.strftime("%Y-%m")
    for column in forecast_view.columns[1:]:
        forecast_view[column] = forecast_view[column].map(inr)
    results += markdown_table(forecast_view) + "\n\n"
    results += f"Next three months: forecast **{inr(f.head(3).forecast.sum())}**, target **{inr(f.head(3).target.sum())}**, gap **{inr(f.head(3).gap_to_target.sum())}**. Twelve-month forecast: {inr(f.forecast.sum())}. Range is indicative and long-horizon accuracy is not established by one-month backtests.\n\n"
    risk = (
        active.groupby("risk_level")
        .agg(
            deals=("opportunity_id", "size"),
            face_value=("net_deal_value", "sum"),
            weighted_value=("weighted_value", "sum"),
        )
        .reset_index()
    )
    for column in ["face_value", "weighted_value"]:
        risk[column] = risk[column].map(inr)
    results += (
        "## Deal risk\n\n"
        + markdown_table(risk)
        + "\n\nPolicy classifications are not loss probabilities. Closed opportunities are excluded.\n\n"
    )
    scenarios = tables["scenario_examples"].copy()
    for column in [
        "projected_revenue",
        "expected_pipeline",
        "target",
        "revenue_gap",
        "pipeline_required",
    ]:
        scenarios[column] = scenarios[column].map(inr)
    scenarios["target_attainment"] = scenarios.target_attainment.map(lambda x: f"{x:.2%}")
    results += (
        "## Scenario output\n\n"
        + markdown_table(scenarios)
        + "\n\nThe example changes win probability by +5 percentage points and remaining cycle by −10%. This is a conditional projection, not an observed improvement.\n\n"
    )
    results += "## Recommendations and evidence\n\n"
    for row in tables["recommendations"].itertuples():
        results += f"- **{row.problem}:** {row.evidence}. Impact: {row.business_impact}. Action: {row.recommendation}.\n"
    results += "\n## Use and verification\n\nRun `python run_pipeline.py`, `python -m pytest -q`, then `streamlit run app.py`. Open http://localhost:8501 in Chrome. The README covers setup and repository structure. docs/VALIDATION.md records the final executed tests/browser evidence. docs/INTERVIEW_GUIDE.md contains 66 explained questions; docs/TWO_MINUTE_EXPLANATION.md and docs/RESUME_BULLETS.md support portfolio presentation. Power BI is a guide/DAX deliverable, not an executed .pbix.\n"
    (ROOT / "RESULTS.md").write_text(results, encoding="utf-8")
    resume = "# Resume bullets — executed synthetic portfolio\n\nUse only if you can reproduce and explain the work. Do not describe the simulation as employment, a client engagement or realized business impact.\n\n"
    resume += f"## Business Analyst\n\n- Documented sales/revenue business requirements, eight stakeholder groups, 30 user stories and as-is/to-be process maps for a simulated Indian B2B company.\n- Defined 29 KPI measures and developed 42 SQL analyses over {len(o):,} validated sales opportunities to investigate stage conversion, pipeline health and quota gaps.\n- Built an interactive decision-support application with transparent risk explanations and seven-input scenario analysis; evaluated a bookings forecast at {selected.wape:.2%} held-out WAPE on synthetic data.\n\n"
    resume += f"## Data Analyst\n\n- Built a reproducible Python/Pandas and SQLite pipeline for {cfg['dataset_size']:,} generated opportunities and {len(tables['activities']):,} validated activity records, quarantining {quarantined:,} invalid financial records.\n- Developed 42 business SQL queries, funnel/cycle analyses, source-level statistical comparisons and time-ordered forecast evaluation; selected model achieved {selected.wape:.2%} held-out WAPE on simulated bookings.\n- Delivered a Streamlit/Plotly analytics application, executed analytical notebooks and a Power BI implementation guide with DAX measures.\n\n"
    resume += f"## BI Analyst\n\n- Designed an analytical sales data model and 29 documented KPI definitions linking pipeline, conversion, booked revenue, quota and forecast variance.\n- Implemented 42 SQLite business queries and 12 interactive Streamlit workspaces with filtering, record drill-down and CSV export over {len(o):,} validated opportunities.\n- Authored a Power BI star-schema implementation guide, export utility and DAX measures for revenue reporting; documented metric scope and reconciliation to executed Python outputs.\n"
    (ROOT / "docs/RESUME_BULLETS.md").write_text(resume, encoding="utf-8")
