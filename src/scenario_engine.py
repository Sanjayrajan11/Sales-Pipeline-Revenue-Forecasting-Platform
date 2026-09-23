"""A sensitivity model for an explicitly selected open-pipeline horizon."""

import numpy as np
import pandas as pd

from src.utils import ACTIVE, ratio


def scenario(
    o: pd.DataFrame,
    target: float,
    as_of: str,
    win_adjust: float = 0,
    deal_adjust: float = 0,
    conversion_adjust: float = 0,
    cycle_adjust: float = 0,
    additional: int = 0,
    target_adjust: float = 0,
    discount_adjust: float = 0,
    horizon_days: int = 90,
) -> dict:
    """Percentage-point probability/discount changes, relative size/cycle/target changes.

    Win adjustment shifts probability; conversion adjusts executable deal share.
    They are separate assumptions, not additive estimates of causal impact.
    New opportunities use current cohort mean size/probability and a 90-day cycle.
    """
    values = [
        win_adjust,
        deal_adjust,
        conversion_adjust,
        cycle_adjust,
        target_adjust,
        discount_adjust,
        target,
        additional,
        horizon_days,
    ]
    if (
        not all(np.isfinite(values))
        or additional < 0
        or additional != int(additional)
        or target < 0
        or horizon_days <= 0
        or horizon_days != int(horizon_days)
        or cycle_adjust <= -1
        or deal_adjust <= -1
        or target_adjust <= -1
    ):
        raise ValueError(
            "Scenario inputs must be finite with non-negative counts and valid relative changes."
        )
    deals = o[o.deal_status.isin(ACTIVE)].copy()
    now = pd.Timestamp(as_of)
    remaining = (deals.expected_close_date - now).dt.days.clip(lower=1) * (1 + cycle_adjust)
    eligible = deals[remaining <= horizon_days]
    probability = (eligible.win_probability + win_adjust).clip(0, 1)
    executable = np.clip(1 + conversion_adjust, 0, 2)
    probability = (probability * executable).clip(0, 1)
    discounts = (eligible.discount_percentage + discount_adjust * 100).clip(0, 100)
    amount = eligible.opportunity_amount * (1 + deal_adjust) * (1 - discounts / 100)
    new_p = float(np.clip((deals.win_probability.mean() if len(deals) else 0) + win_adjust, 0, 1))
    new_p = min(1, new_p * executable)
    new_size = float(deals.opportunity_amount.mean()) if len(deals) else 0
    new_discount = float(deals.discount_percentage.mean()) if len(deals) else 0
    new_value = (
        new_size
        * (1 + deal_adjust)
        * (1 - np.clip(new_discount + discount_adjust * 100, 0, 100) / 100)
    )
    eligible_new = additional if 90 * (1 + cycle_adjust) <= horizon_days else 0
    revenue = float((amount * probability).sum() + eligible_new * new_value * new_p)
    wins = float(probability.sum() + eligible_new * new_p)
    pipe = float(amount.sum() + eligible_new * new_value)
    adjusted_target = target * (1 + target_adjust)
    effective_rate = ratio(revenue, pipe)
    return {
        "projected_revenue": revenue,
        "projected_won_deals": wins,
        "expected_pipeline": pipe,
        "target": adjusted_target,
        "target_attainment": ratio(revenue, adjusted_target),
        "revenue_gap": adjusted_target - revenue,
        "pipeline_required": ratio(max(0, adjusted_target - revenue), effective_rate),
        "eligible_existing_deals": len(eligible),
        "eligible_additional_deals": eligible_new,
    }
