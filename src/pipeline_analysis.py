"""Commercial group comparisons and loss-value Pareto analysis."""

import pandas as pd

from src.kpi_engine import kpis


def compare(o: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Keep multiple performance dimensions visible instead of a composite leaderboard."""
    rows = [{dimension: name, **kpis(group)} for name, group in o.groupby(dimension, observed=True)]
    return pd.DataFrame(rows)


def loss_pareto(o: pd.DataFrame, dimension: str = "lost_reason") -> pd.DataFrame:
    """Lost deal value is potential bookings, not realized revenue leakage."""
    rows = (
        o[o.deal_status.eq("Closed Lost")]
        .groupby(dimension)
        .agg(lost_count=("opportunity_id", "size"), lost_value=("net_deal_value", "sum"))
        .sort_values("lost_value", ascending=False)
        .reset_index()
    )
    rows["cumulative_share"] = (
        rows.lost_value.cumsum() / rows.lost_value.sum() if rows.lost_value.sum() else 0
    )
    return rows
