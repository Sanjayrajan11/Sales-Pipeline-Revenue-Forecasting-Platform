"""Observed activity summaries and historical, stage-conditioned win estimates."""

import numpy as np
import pandas as pd

from src.utils import ACTIVE, STAGES


def stage_probabilities(o: pd.DataFrame, h: pd.DataFrame, cutoff: pd.Timestamp) -> pd.Series:
    """Estimate P(eventual win | reached stage, resolved by cutoff), with Beta(1,1).

    This is a resolved-deal estimate, subject to survivor bias. Open outcomes
    never enter training. Re-estimate independently for each backtest cutoff.
    """
    resolved = o[o.actual_close_date.notna() & (o.actual_close_date <= cutoff)][
        ["opportunity_id", "deal_status"]
    ]
    joined = h[h.entry_date <= cutoff].merge(resolved, on="opportunity_id")
    joined["won"] = joined.deal_status.eq("Closed Won").astype(int)
    g = joined.groupby("sales_stage").won.agg(["sum", "count"])
    return ((g["sum"] + 1) / (g["count"] + 2)).reindex(STAGES).fillna(0.5)


def enrich(tables: dict, as_of: str) -> dict:
    """Add reproducible analytical features without overriding source events."""
    o = tables["opportunities"].copy()
    a = tables["activities"]
    counts = pd.crosstab(a.opportunity_id, a.activity_type)
    for name, kind in [
        ("meeting_count", "Meeting"),
        ("email_count", "Email"),
        ("call_count", "Phone Call"),
        ("demo_count", "Product Demo"),
        ("follow_up_count", "Follow-up"),
    ]:
        o[name] = (
            o.opportunity_id.map(counts.get(kind, pd.Series(dtype=float))).fillna(0).astype(int)
        )
    o["proposal_sent"] = o.opportunity_id.isin(
        tables["stage_history"].loc[
            tables["stage_history"].sales_stage.eq("Proposal"), "opportunity_id"
        ]
    )
    p = stage_probabilities(o, tables["stage_history"], pd.Timestamp(as_of))
    o["win_probability"] = o.sales_stage.map(p).fillna(o.deal_status.eq("Closed Won").astype(float))
    o["weighted_value"] = np.where(
        o.deal_status.isin(ACTIVE), o.net_deal_value * o.win_probability, 0
    )
    o["forecast_category"] = np.select(
        [
            o.deal_status.eq("Closed Won"),
            ~o.deal_status.isin(ACTIVE),
            (o.win_probability >= 0.65) & (o.activity_gap_days <= 14) & (o.engagement_score >= 60),
            o.win_probability >= 0.4,
        ],
        ["Closed Won", "Excluded", "Commit", "Best Case"],
        default="Pipeline",
    )
    tables["opportunities"] = o
    return tables
