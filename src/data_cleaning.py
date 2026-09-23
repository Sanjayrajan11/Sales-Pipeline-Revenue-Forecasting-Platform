"""Repair using independent relational evidence; quarantine unresolvable financial data."""

import pandas as pd

from src.utils import STAGES
from src.validation import quality


def clean(tables: dict[str, pd.DataFrame], as_of: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Return clean tables, audit summary, and quarantined opportunities with reasons."""
    result = {key: frame.copy() for key, frame in tables.items()}
    raw = result["opportunities"]
    before = quality(raw).assign(phase="raw")
    customers = result["customers"].drop_duplicates("customer_id").copy()
    o = raw.drop_duplicates("opportunity_id").copy()
    customer_lookup = customers.set_index("customer_id")
    for col in ["industry", "region", "city", "state"]:
        o[col] = o.customer_id.map(customer_lookup[col])
    rep = o.customer_id.map(customer_lookup.account_manager)
    o["sales_rep_id"] = o.sales_rep_id.where(
        o.sales_rep_id.isin(result["sales_reps"].sales_rep_id), rep
    ).astype(int)
    history = result["stage_history"]
    ordered = history.sort_values(["opportunity_id", "entry_date"])
    first = ordered.groupby("opportunity_id").first()
    last = ordered.groupby("opportunity_id").tail(1).set_index("opportunity_id")
    o["created_date"] = o.opportunity_id.map(first.entry_date)
    terminal = last.exit_to.isin(["Closed Won", "Closed Lost"])
    current_stage = last.sales_stage.where(~terminal, last.exit_to)
    o["sales_stage"] = o.opportunity_id.map(current_stage)
    o["actual_close_date"] = o.opportunity_id.map(last.exit_date.where(terminal))
    o["stage_entry_date"] = o.opportunity_id.map(last.entry_date.where(~terminal, last.exit_date))
    prev = last.sales_stage.map(
        {stage: STAGES[i - 1] if i else "None" for i, stage in enumerate(STAGES)}
    )
    o["previous_stage"] = o.opportunity_id.map(prev.where(~terminal, last.sales_stage))
    o["deal_status"] = o.sales_stage.where(
        o.sales_stage.isin(["Closed Won", "Closed Lost"]), "Open"
    )
    end = o.actual_close_date.fillna(pd.Timestamp(as_of))
    o["sales_cycle_days"] = (o.actual_close_date - o.created_date).dt.days
    o["total_opportunity_age_days"] = (end - o.created_date).dt.days
    o["days_in_current_stage"] = (end - o.stage_entry_date).dt.days
    o["last_activity_date"] = o.opportunity_id.map(
        result["activities"].groupby("opportunity_id").activity_date.max()
    )
    o["activity_gap_days"] = (end - o.last_activity_date).dt.days
    o.loc[(o.deal_status == "Open") & (o.activity_gap_days > 30), "deal_status"] = "Stalled"
    o["net_deal_value"] = (o.opportunity_amount * (1 - o.discount_percentage / 100)).round(2)
    o["quarter"], o["month"], o["year"] = (
        o.created_date.dt.quarter,
        o.created_date.dt.month,
        o.created_date.dt.year,
    )
    bad = (
        ~o.opportunity_amount.between(1000, 50000000)
        | ~o.discount_percentage.between(0, 60)
        | ~o.customer_id.isin(customers.customer_id)
    )
    quarantine = o.loc[bad].copy()
    quarantine["quarantine_reason"] = (
        "Invalid financial value or unknown customer; no reliable repair source"
    )
    o = o.loc[~bad].reset_index(drop=True)
    result["opportunities"] = o
    result["customers"] = customers
    for name in ["activities", "stage_history", "contracts"]:
        result[name] = result[name][result[name].opportunity_id.isin(o.opportunity_id)].copy()
    won = o[o.deal_status == "Closed Won"]
    result["customers"]["customer_lifetime_value"] = customers.customer_id.map(
        won.groupby("customer_id").net_deal_value.sum()
    ).fillna(0)
    result["customers"]["active_products"] = (
        customers.customer_id.map(won.groupby("customer_id").product.nunique())
        .fillna(0)
        .astype(int)
    )
    contract_values = o.set_index("opportunity_id").net_deal_value
    result["contracts"]["net_deal_value"] = result["contracts"].opportunity_id.map(contract_values)
    return (
        result,
        pd.concat([before, quality(o).assign(phase="clean")], ignore_index=True),
        quarantine,
    )
