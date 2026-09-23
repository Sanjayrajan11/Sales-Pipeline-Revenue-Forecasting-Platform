"""Cohort KPIs are distinct from calendar-booking target comparisons."""

import pandas as pd

from src.utils import ACTIVE, ratio


def kpis(o: pd.DataFrame) -> dict:
    """Calculate metrics over exactly the supplied opportunity cohort."""
    won = o[o.deal_status == "Closed Won"]
    lost = o[o.deal_status == "Closed Lost"]
    opened = o[o.deal_status.isin(ACTIVE)]
    return {
        "opportunities": len(o),
        "pipeline_value": o.net_deal_value.sum(),
        "closed_won_revenue": won.net_deal_value.sum(),
        "closed_lost_value": lost.net_deal_value.sum(),
        "open_pipeline": opened.net_deal_value.sum(),
        "weighted_pipeline": opened.weighted_value.sum(),
        "win_rate": ratio(len(won), len(won) + len(lost)),
        "lead_to_win_rate": ratio(len(won), len(o)),
        "average_deal_size": won.net_deal_value.mean(),
        "median_deal_size": won.net_deal_value.median(),
        "average_sales_cycle": won.sales_cycle_days.mean(),
        "median_sales_cycle": won.sales_cycle_days.median(),
        "cycle_p25": won.sales_cycle_days.quantile(0.25),
        "cycle_p75": won.sales_cycle_days.quantile(0.75),
        "cycle_p90": won.sales_cycle_days.quantile(0.9),
        "opportunity_aging": opened.total_opportunity_age_days.mean(),
        "stale_opportunity_rate": ratio((opened.activity_gap_days > 21).sum(), len(opened)),
        "stalled_rate": ratio((o.deal_status == "Stalled").sum(), len(opened)),
        "average_discount": o.discount_percentage.mean(),
        "revenue_per_rep": ratio(won.net_deal_value.sum(), o.sales_rep_id.nunique()),
        "revenue_per_customer": ratio(won.net_deal_value.sum(), o.customer_id.nunique()),
        "top5_pipeline_share": ratio(
            opened.nlargest(5, "net_deal_value").net_deal_value.sum(), opened.net_deal_value.sum()
        ),
        "top10_pipeline_share": ratio(
            opened.nlargest(10, "net_deal_value").net_deal_value.sum(), opened.net_deal_value.sum()
        ),
        "top20_pipeline_share": ratio(
            opened.nlargest(20, "net_deal_value").net_deal_value.sum(), opened.net_deal_value.sum()
        ),
        "top10_revenue_share": ratio(
            won.nlargest(10, "net_deal_value").net_deal_value.sum(), won.net_deal_value.sum()
        ),
        "deal_velocity": ratio(
            len(opened) * ratio(len(won), len(won) + len(lost)) * won.net_deal_value.mean(),
            won.sales_cycle_days.mean(),
        ),
    }


def target_analysis(
    o: pd.DataFrame, targets: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp
) -> dict:
    """Align numerator and quota to a calendar period; coverage uses remaining target."""
    target = targets.loc[targets.period.between(start, end), "target"].sum()
    actual = o.loc[
        o.deal_status.eq("Closed Won") & o.actual_close_date.between(start, end), "net_deal_value"
    ].sum()
    active = o[o.deal_status.isin(ACTIVE) & o.expected_close_date.between(start, end)]
    remaining = max(0, target - actual)
    return {
        "target": target,
        "actual": actual,
        "variance": actual - target,
        "variance_pct": ratio(actual - target, target),
        "attainment": ratio(actual, target),
        "remaining_target": remaining,
        "open_pipeline": active.net_deal_value.sum(),
        "weighted_pipeline": active.weighted_value.sum(),
        "pipeline_coverage": ratio(active.net_deal_value.sum(), remaining),
        "weighted_coverage": ratio(active.weighted_value.sum(), remaining),
        "required_pipeline": ratio(remaining, kpis(o)["win_rate"]),
    }
