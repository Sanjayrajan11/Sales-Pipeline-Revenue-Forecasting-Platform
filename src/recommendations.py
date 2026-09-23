"""Evidence-linked actions; exposure is never presented as recovered revenue."""

import pandas as pd

from src.funnel_analysis import funnel
from src.pipeline_analysis import compare, loss_pareto
from src.utils import ACTIVE, inr


def recommendations(
    o: pd.DataFrame, h: pd.DataFrame, as_of: str, targets: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Generate actual observations, exposures, owners and proposed next steps."""
    opened = o[o.deal_status.isin(ACTIVE)]
    now = pd.Timestamp(as_of)
    rows = []
    masks = [
        (
            "Stale opportunities",
            opened.activity_gap_days > 21,
            "High",
            "Contact the customer within two business days",
        ),
        (
            "High-value risky deals",
            (opened.risk_score >= 45) & (opened.net_deal_value >= o.net_deal_value.quantile(0.9)),
            "Critical",
            "Arrange manager and commercial review",
        ),
        (
            "Expected close approaching or overdue",
            opened.expected_close_date <= now + pd.Timedelta(days=7),
            "High",
            "Validate procurement milestones and update the close plan",
        ),
        (
            "No scheduled future action",
            opened.next_follow_up_date.isna() | (opened.next_follow_up_date < now),
            "High",
            "Schedule a specific follow-up date",
        ),
        (
            "Low engagement",
            opened.engagement_score < 40,
            "Medium",
            "Identify an active customer sponsor",
        ),
    ]
    for problem, mask, priority, action in masks:
        subset = opened[mask]
        if len(subset):
            rows.append(
                {
                    "problem": problem,
                    "evidence": f"{len(subset):,} of {len(opened):,} open/stalled deals",
                    "business_impact": f"{inr(subset.net_deal_value.sum())} potential bookings exposed; not recoverable revenue",
                    "exposure_inr": subset.net_deal_value.sum(),
                    "recommendation": action,
                    "priority": priority,
                    "owner": "Sales Manager",
                }
            )
    for dimension in ["lead_source", "region", "product"]:
        g = compare(o, dimension).dropna(subset=["win_rate"])
        if not g.empty:
            worst = g.sort_values("win_rate").iloc[0]
            rows.append(
                {
                    "problem": f"Lower observed conversion: {worst[dimension]}",
                    "evidence": f"{worst.win_rate:.1%} resolved-deal win rate; {int(worst.opportunities):,} total opportunities",
                    "business_impact": f"{inr(worst.open_pipeline)} current pipeline in this cohort",
                    "exposure_inr": worst.open_pipeline,
                    "recommendation": f"Review {dimension} qualification and deal mix before changing investment",
                    "priority": "Medium",
                    "owner": "Revenue Operations",
                }
            )
    f = funnel(o, h).dropna(subset=["drop_off"])
    if not f.empty:
        row = f.sort_values("drop_off", ascending=False).iloc[0]
        rows.append(
            {
                "problem": f"Stage bottleneck: {row.stage}",
                "evidence": f"{row.drop_off:.1%} lost among {int(row.exited):,} observed exits; {int(row.pending):,} visits still pending",
                "business_impact": "Qualification or commercial process may constrain conversion; no causal effect estimated",
                "exposure_inr": 0,
                "recommendation": "Review a sample of lost deals and validate stage exit criteria",
                "priority": "High",
                "owner": "Sales Director",
            }
        )
    pareto = loss_pareto(o)
    if not pareto.empty:
        row = pareto.iloc[0]
        rows.append(
            {
                "problem": f"Largest lost-value reason: {row.lost_reason}",
                "evidence": f"{int(row.lost_count):,} lost deals; {row.cumulative_share:.1%} of lost value",
                "business_impact": f"{inr(row.lost_value)} historical potential bookings lost",
                "exposure_inr": row.lost_value,
                "recommendation": "Audit reason coding and run a targeted loss review",
                "priority": "Medium",
                "owner": "Commercial Lead",
            }
        )
    if not opened.empty:
        top = opened.nlargest(10, "weighted_value")
        share = (
            top.weighted_value.sum() / opened.weighted_value.sum()
            if opened.weighted_value.sum()
            else 0
        )
        rows.append(
            {
                "problem": "Largest forecast contributors",
                "evidence": f"Top ten deals contribute {share:.2%} of weighted active pipeline",
                "business_impact": f"{inr(top.weighted_value.sum())} weighted bookings depend on these close plans",
                "exposure_inr": top.weighted_value.sum(),
                "recommendation": "Review the top-ten deal plans and executive sponsorship weekly",
                "priority": "High" if share > 0.2 else "Medium",
                "owner": "Sales Director",
            }
        )
    # Compare resolved-deal conversion in successive 90-day windows, preserving counts.
    resolved = o[o.actual_close_date.between(now - pd.Timedelta(days=179), now)].copy()
    resolved["window"] = (resolved.actual_close_date > now - pd.Timedelta(days=90)).map(
        {True: "recent", False: "prior"}
    )
    resolved["won"] = resolved.deal_status.eq("Closed Won").astype(int)
    for product, group in resolved.groupby("product"):
        windows = group.groupby("window").won.agg(["mean", "count"])
        if {"recent", "prior"}.issubset(windows.index) and windows["count"].min() >= 30:
            recent, prior = windows.loc["recent"], windows.loc["prior"]
            if recent["mean"] < prior["mean"]:
                rows.append(
                    {
                        "problem": f"Declining resolved conversion: {product}",
                        "evidence": f"Recent 90 days {recent['mean']:.1%} ({int(recent['count'])} resolved) versus prior 90 days {prior['mean']:.1%} ({int(prior['count'])} resolved)",
                        "business_impact": "Mix or timing changes may explain the decline; causal effect is not established",
                        "exposure_inr": 0,
                        "recommendation": "Review source, segment and discount mix before changing product investment",
                        "priority": "Medium",
                        "owner": "Product / Commercial Analyst",
                    }
                )
    if targets is not None and not targets.empty:
        start = now.replace(month=1, day=1)
        quotas = targets[targets.period.between(start, now)].groupby("region").target.sum()
        actual = (
            o[o.deal_status.eq("Closed Won") & o.actual_close_date.between(start, now)]
            .groupby("region")
            .net_deal_value.sum()
        )
        for region, quota in quotas.items():
            booked = actual.get(region, 0)
            if booked < quota:
                rows.append(
                    {
                        "problem": f"Region below elapsed-month target: {region}",
                        "evidence": f"{inr(booked)} booked versus {inr(quota)} YTD target; {booked / quota:.1%} attainment",
                        "business_impact": f"{inr(quota - booked)} booking shortfall",
                        "exposure_inr": quota - booked,
                        "recommendation": "Reconcile close timing, capacity and qualification with the regional manager",
                        "priority": "High",
                        "owner": "Regional Sales Manager",
                    }
                )
    return pd.DataFrame(rows)
