"""Explicit policy-based risk and independent health components."""

import numpy as np
import pandas as pd

from src.utils import ACTIVE, STAGES

RISK_RULES = [
    ("Old opportunity", 10, "Review qualification and realistic close date"),
    ("No recent activity", 15, "Contact the customer and log the response"),
    ("Close date pressure", 10, "Confirm procurement milestones"),
    ("Low engagement", 10, "Re-engage the decision maker"),
    ("Stage stagnation", 15, "Review the stage exit criteria"),
    ("Competitor present", 5, "Clarify differentiation and buying criteria"),
    ("Large deal exposure", 10, "Arrange executive sponsorship"),
    ("High discount", 5, "Review commercial approval"),
    ("No future follow-up", 10, "Schedule a dated next action"),
    ("Long cycle", 10, "Reassess the mutual close plan"),
]


def score(o: pd.DataFrame, as_of: str, stage_limits: list[int]) -> pd.DataFrame:
    """Score only active deals; closed deals get no operational risk rating."""
    o = o.copy()
    active = o.deal_status.isin(ACTIVE)
    now = pd.Timestamp(as_of)
    limits = o.sales_stage.map(dict(zip(STAGES, stage_limits))).fillna(1)
    closed_cycles = o.loc[o.deal_status.eq("Closed Won"), "sales_cycle_days"]
    cycle_p90 = closed_cycles.quantile(0.9) if len(closed_cycles) else 180
    size_p90 = o.net_deal_value.quantile(0.9)
    days_to_close = (o.expected_close_date - now).dt.days
    masks = [
        o.total_opportunity_age_days > 120,
        o.activity_gap_days > 21,
        days_to_close <= 7,
        o.engagement_score < 40,
        o.days_in_current_stage > limits * 1.5,
        o.competitor_present.astype(bool),
        o.net_deal_value > size_p90,
        o.discount_percentage > 25,
        o.next_follow_up_date.isna() | (o.next_follow_up_date < now),
        o.total_opportunity_age_days > cycle_p90,
    ]
    points = np.column_stack([m.fillna(False).to_numpy() for m in masks])
    o["risk_score"] = (points @ np.array([r[1] for r in RISK_RULES])) * active
    o["risk_level"] = np.select(
        [~active, o.risk_score >= 65, o.risk_score >= 45, o.risk_score >= 25],
        ["Closed", "Critical", "High", "Medium"],
        default="Low",
    )
    o["risk_drivers"] = [
        "; ".join(rule[0] for rule, flag in zip(RISK_RULES, row) if flag)
        if act
        else "Closed opportunity"
        for row, act in zip(points, active)
    ]
    o["recommended_action"] = [
        "; ".join(rule[2] for rule, flag in zip(RISK_RULES, row) if flag)
        if act
        else "No open-deal action"
        for row, act in zip(points, active)
    ]
    # Eight inspectable, bounded components, all equally weighted.
    components = {
        "stage_progression": o.sales_stage.map(
            {s: (i + 1) / 6 for i, s in enumerate(STAGES)}
        ).fillna(0),
        "recency": (1 - o.activity_gap_days / 30).clip(0, 1),
        "age": (1 - o.total_opportunity_age_days / 180).clip(0, 1),
        "engagement": o.engagement_score / 100,
        "close_plan": (days_to_close >= 0).astype(float),
        "historical_conversion": o.win_probability,
        "size_balance": (size_p90 / o.net_deal_value).clip(0, 1),
        "next_action": (o.next_follow_up_date >= now).astype(float),
    }
    for name, values in components.items():
        o[f"health_{name}"] = (values * 12.5).where(active)
    o["health_score"] = (
        o[[f"health_{name}" for name in components]].sum(axis=1).where(active).round(1)
    )
    o["health_category"] = np.select(
        [~active, o.health_score >= 70, o.health_score >= 45],
        ["Closed", "Healthy", "Watch"],
        default="At risk",
    )
    o["forecast_risk_value"] = o.weighted_value * o.risk_score / 100
    return o
