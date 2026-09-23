"""Measurable data-quality checks, with record-level rather than cell denominators."""

import pandas as pd

from src.utils import STAGES


def quality(frame: pd.DataFrame) -> pd.DataFrame:
    """Profile key-field completeness and independently overlapping defect classes."""
    required = ["opportunity_id", "customer_id", "sales_rep_id", "industry", "created_date"]
    closed = frame.deal_status.isin(["Closed Won", "Closed Lost"])
    checks = {
        "missing_key_fields": frame[required].isna().any(axis=1),
        "duplicate_opportunity": frame.opportunity_id.duplicated(),
        "invalid_record": (~frame.sales_stage.isin(STAGES + ["Closed Won", "Closed Lost"]))
        | (~frame.discount_percentage.between(0, 60))
        | (frame.opportunity_amount <= 0),
        "amount_outlier": ~frame.opportunity_amount.between(1000, 50000000),
        "date_inconsistency": (frame.expected_close_date < frame.created_date)
        | (closed & frame.actual_close_date.isna())
        | (frame.actual_close_date < frame.created_date)
        | (frame.sales_cycle_days < 0),
        "missing_industry": frame.industry.isna(),
        "missing_rep": frame.sales_rep_id.isna(),
    }
    return pd.DataFrame(
        [
            {
                "check": name,
                "affected_records": int(mask.sum()),
                "total_records": len(frame),
                "percentage": 100 * mask.mean() if len(frame) else 0,
            }
            for name, mask in checks.items()
        ]
    )


def validate(tables: dict[str, pd.DataFrame], as_of: str) -> None:
    """Fail before publishing data with broken keys, chronology or financial identities."""
    o = tables["opportunities"]
    if o.empty:
        raise ValueError("No valid opportunities remain after cleaning.")
    if o.opportunity_id.duplicated().any():
        raise ValueError("Duplicate opportunity IDs.")
    if not o.customer_id.isin(tables["customers"].customer_id).all():
        raise ValueError("Orphan customer key.")
    if not o.sales_rep_id.isin(tables["sales_reps"].sales_rep_id).all():
        raise ValueError("Orphan sales representative key.")
    if (quality(o).affected_records > 0).any():
        raise ValueError("Unresolved quality checks.")
    if (
        (
            o.net_deal_value - (o.opportunity_amount * (1 - o.discount_percentage / 100)).round(2)
        ).abs()
        > 0.011
    ).any():
        raise ValueError("Net values do not reconcile.")
    for name in ["activities", "stage_history", "contracts"]:
        if not tables[name].opportunity_id.isin(o.opportunity_id).all():
            raise ValueError(f"Orphan opportunity in {name}.")
    if (o.created_date > pd.Timestamp(as_of)).any():
        raise ValueError("Future opportunity in snapshot.")
    h = tables["stage_history"]
    if ((h.exit_date < h.entry_date) | (h.entry_date > pd.Timestamp(as_of))).any():
        raise ValueError("Invalid stage chronology.")
    a = tables["activities"].merge(
        o[["opportunity_id", "created_date", "actual_close_date"]], on="opportunity_id"
    )
    if (
        (a.activity_date < a.created_date)
        | (a.activity_date > a.actual_close_date.fillna(pd.Timestamp(as_of)))
    ).any():
        raise ValueError("Activity outside observed opportunity life.")
