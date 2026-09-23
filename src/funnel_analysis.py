"""Transition-based funnel denominators explicitly exclude still-open stage visits."""

import pandas as pd

from src.utils import STAGES, ratio


def funnel(o: pd.DataFrame, h: pd.DataFrame) -> pd.DataFrame:
    """One visit per opportunity per stage; conversion conditions on observed exits."""
    h = h[h.opportunity_id.isin(o.opportunity_id)]
    lookup = o.set_index("opportunity_id")
    rows = []
    for i, stage in enumerate(STAGES):
        visits = h[h.sales_stage == stage]
        exits = visits[visits.exit_date.notna()]
        advanced = exits.exit_to.ne("Closed Lost").sum()
        ids = visits.opportunity_id
        rows.append(
            {
                "stage": stage,
                "stage_order": i,
                "entered": len(visits),
                "exited": len(exits),
                "pending": len(visits) - len(exits),
                "advanced": int(advanced),
                "lost": int(exits.exit_to.eq("Closed Lost").sum()),
                "conversion": ratio(advanced, len(exits)),
                "drop_off": ratio(exits.exit_to.eq("Closed Lost").sum(), len(exits)),
                "average_days_completed": exits.duration_days.mean(),
                "median_days_completed": exits.duration_days.median(),
                "current_average_age": visits.loc[visits.exit_date.isna(), "duration_days"].mean(),
                "stage_value": lookup.loc[ids, "net_deal_value"].sum(),
                "won_value": lookup.loc[ids]
                .loc[lambda x: x.deal_status.eq("Closed Won"), "net_deal_value"]
                .sum(),
                "stage_to_win": ratio(
                    lookup.loc[ids, "deal_status"].eq("Closed Won").sum(), len(ids)
                ),
            }
        )
    return pd.DataFrame(rows)
