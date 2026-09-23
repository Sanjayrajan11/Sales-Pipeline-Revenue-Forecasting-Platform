"""Reproducible, censored B2B sales journeys; no outcome-derived forecasts."""

import numpy as np
import pandas as pd

from src.utils import STAGES

LOCATIONS = [
    ("Bengaluru", "Karnataka", "South"),
    ("Chennai", "Tamil Nadu", "South"),
    ("Mumbai", "Maharashtra", "West"),
    ("Pune", "Maharashtra", "West"),
    ("Delhi", "Delhi", "North"),
    ("Jaipur", "Rajasthan", "North"),
    ("Kolkata", "West Bengal", "East"),
    ("Bhubaneswar", "Odisha", "East"),
]
REASONS = [
    "Budget constraints",
    "Competitor selected",
    "No decision",
    "Timing",
    "Product mismatch",
    "Pricing",
    "Internal approval delay",
    "Customer priorities changed",
    "Poor engagement",
    "Procurement delay",
    "Duplicate opportunity",
    "Other",
]


def generate(size: int, seed: int, as_of: str, history_start: str) -> dict[str, pd.DataFrame]:
    """Generate opportunities plus relational dimensions, dated events and quotas.

    Size counts opportunities before deliberate duplicates, not all fact rows.
    Latent engagement affects activity, stage survival and duration. Journeys
    stop at the snapshot; future outcomes are never written to analytical data.
    """
    rng = np.random.default_rng(seed)
    snapshot = pd.Timestamp(as_of)
    n_customers, n_reps = max(100, size // 12), 48
    geography = pd.DataFrame(LOCATIONS, columns=["city", "state", "region"])
    customers = pd.DataFrame({"customer_id": np.arange(1, n_customers + 1)})
    customers["customer_name"] = [f"Synthetic Enterprise {i:05d}" for i in customers.customer_id]
    customers = customers.join(
        geography.iloc[rng.integers(0, 8, n_customers)].reset_index(drop=True)
    )
    customers["industry"] = rng.choice(
        ["IT Services", "Manufacturing", "Healthcare", "Retail", "BFSI"], n_customers
    )
    customers["customer_segment"] = rng.choice(
        ["SMB", "Mid-market", "Enterprise"], n_customers, p=[0.48, 0.36, 0.16]
    )
    scale = customers.customer_segment.map({"SMB": 1, "Mid-market": 3, "Enterprise": 9}).to_numpy()
    customers["company_size"] = (rng.integers(25, 150, n_customers) * scale).astype(int)
    customers["annual_revenue_band"] = np.select(
        [scale == 1, scale == 3], ["Below ₹10 crore", "₹10–100 crore"], default="Above ₹100 crore"
    )
    customers["existing_customer"] = rng.random(n_customers) < 0.36
    customers["customer_since"] = pd.Timestamp(history_start) - pd.to_timedelta(
        rng.integers(30, 1500, n_customers), unit="D"
    )
    customers["customer_health_score"] = rng.integers(35, 96, n_customers)
    reps = pd.DataFrame({"sales_rep_id": np.arange(1, n_reps + 1)})
    reps["sales_rep_name"] = [f"Rep {i:02d} (simulated)" for i in reps.sales_rep_id]
    reps["region"] = np.repeat(["South", "West", "North", "East"], 12)
    reps["team"] = reps.region + " Commercial"
    reps["sales_team_id"] = np.repeat(np.arange(1, 5), 12)
    reps["experience_years"] = rng.integers(1, 13, n_reps)
    reps["manager"] = reps.region + " Manager (simulated)"
    reps["territory"] = reps.region
    reps["hire_date"] = pd.Timestamp("2019-01-01") + pd.to_timedelta(
        rng.integers(0, 1000, n_reps), unit="D"
    )
    reps["monthly_target"] = (rng.uniform(1.1, 1.8, n_reps) * size * 88).round(0)
    reps["annual_target"] = reps.monthly_target * 12
    customers["account_manager"] = [
        int(rng.choice(reps.loc[reps.region == reg, "sales_rep_id"])) for reg in customers.region
    ]
    products = pd.DataFrame(
        {
            "product_id": [1, 2, 3, 4],
            "product": ["Cloud Enablement", "Workflow Suite", "Data Advisory", "Security Services"],
            "product_category": ["Services", "Software", "Services", "Services"],
            "base_price": [240000, 160000, 320000, 220000],
        }
    )
    o = pd.DataFrame(
        {
            "opportunity_id": np.arange(1, size + 1),
            "customer_id": rng.integers(1, n_customers + 1, size),
        }
    )
    o = o.merge(
        customers.drop(columns=["customer_since", "customer_name", "annual_revenue_band"]),
        on="customer_id",
        validate="many_to_one",
    )
    o["account_id"] = o.customer_id
    o["sales_rep_id"] = o.account_manager
    o["sales_team_id"] = o.sales_rep_id.map(reps.set_index("sales_rep_id").sales_team_id)
    dates = pd.date_range(history_start, snapshot)
    weights = (1 + 0.12 * np.sin(dates.month.to_numpy() * np.pi / 6)) * np.linspace(
        0.75, 1.3, len(dates)
    )
    o["created_date"] = pd.to_datetime(
        rng.choice(dates.to_numpy(), size, p=weights / weights.sum())
    )
    o["product_id"] = rng.integers(1, 5, size)
    o = (
        o.merge(products, on="product_id", validate="many_to_one")
        .sort_values("opportunity_id")
        .reset_index(drop=True)
    )
    o["lead_source"] = rng.choice(
        ["Referral", "Partner", "Inbound", "Outbound", "Event"],
        size,
        p=[0.17, 0.18, 0.28, 0.25, 0.12],
    )
    o["contract_type"] = rng.choice(["Annual", "Multi-year", "Project"], size, p=[0.5, 0.18, 0.32])
    o["deal_type"] = np.where(
        o.existing_customer, rng.choice(["Renewal", "Expansion"], size), "New business"
    )
    o["new_or_existing_customer"] = np.where(o.existing_customer, "Existing", "New")
    mult = o.customer_segment.map({"SMB": 1, "Mid-market": 2.8, "Enterprise": 7.5})
    o["opportunity_amount"] = (
        (
            o.base_price
            * mult
            * np.sqrt(o.company_size / (mult * 80))
            * np.where(o.contract_type == "Multi-year", 1.9, 1)
            * np.where(o.industry == "BFSI", 1.2, 1)
            * np.where(o.existing_customer, 1.08, 1)
            * rng.lognormal(0, 0.36, size)
        )
        .clip(25000, 45000000)
        .round(2)
    )
    o["discount_percentage"] = (
        (rng.beta(2, 9, size) * 40 + np.where(o.existing_customer, 2, 0)).clip(0, 45).round(2)
    )
    o["net_deal_value"] = (o.opportunity_amount * (1 - o.discount_percentage / 100)).round(2)
    o["competitor_present"] = rng.random(size) < 0.44
    o["competitor_name"] = np.where(
        o.competitor_present,
        rng.choice(["Competitor A", "Competitor B", "Competitor C"], size),
        "None",
    )
    o["decision_makers_count"] = (
        rng.integers(1, 5, size) + (o.customer_segment == "Enterprise").astype(int) * 2
    )
    o["engagement_score"] = (rng.beta(3, 2.5, size) * 100).round(1)
    rep_skill = rng.normal(0, 0.20, n_reps)
    quality = (
        (o.engagement_score - 50) / 50
        + o.existing_customer * 0.28
        - o.competitor_present * 0.28
        + o.lead_source.map(
            {"Referral": 0.35, "Partner": 0.2, "Inbound": 0.08, "Outbound": -0.2, "Event": -0.04}
        )
        + rep_skill[o.sales_rep_id.to_numpy() - 1]
        - np.log1p(o.net_deal_value / 1000000) * 0.09
        - (o.decision_makers_count - 2) * 0.035
        + o.discount_percentage * 0.004
        + 0.08 * np.sin(o.created_date.dt.month * np.pi / 6)
    )
    base_cycle = 70 + o.decision_makers_count * 7 + np.log1p(o.net_deal_value / 500000) * 12
    o["expected_close_date"] = o.created_date + pd.to_timedelta(
        (base_cycle * rng.lognormal(0, 0.22, size)).astype(int), unit="D"
    )
    o["sales_stage"] = "Lead"
    o["previous_stage"] = "None"
    o["stage_entry_date"] = o.created_date
    o["actual_close_date"] = pd.NaT
    o["deal_status"] = "Open"
    o["lost_reason"] = ""
    current = o.created_date.copy()
    active = np.ones(size, dtype=bool)
    histories = []
    for idx, stage in enumerate(STAGES):
        entered = active & (current <= snapshot).to_numpy()
        ix = np.flatnonzero(entered)
        if len(ix) == 0:
            break
        duration = np.maximum(
            2,
            (
                rng.lognormal(np.log([10, 14, 18, 13, 22, 17][idx]), 0.55, size)
                * (1.3 - o.engagement_score.to_numpy() / 180)
                * (1 + o.decision_makers_count.to_numpy() / 20)
            ),
        ).astype(int)
        departure = current + pd.to_timedelta(duration, unit="D")
        eligible = entered & (departure <= snapshot).to_numpy()
        probability = 1 / (
            1 + np.exp(-([1.2, 1.45, 1.55, 1.7, 1.2, 0.9][idx] + quality - duration / 200))
        )
        advance = rng.random(size) < probability
        next_stage = STAGES[idx + 1] if idx < 5 else "Closed Won"
        outcome = np.where(advance, next_stage, "Closed Lost")
        histories.append(
            pd.DataFrame(
                {
                    "opportunity_id": o.loc[ix, "opportunity_id"].to_numpy(),
                    "sales_stage": stage,
                    "stage_order": idx,
                    "entry_date": current.iloc[ix].to_numpy(),
                    "exit_date": departure.iloc[ix].where(eligible[ix]).to_numpy(),
                    "exit_to": np.where(eligible[ix], outcome[ix], ""),
                    "duration_days": np.where(
                        eligible[ix], duration[ix], (snapshot - current.iloc[ix]).dt.days
                    ),
                }
            )
        )
        o.loc[entered, "sales_stage"] = stage
        o.loc[entered, "previous_stage"] = STAGES[idx - 1] if idx else "None"
        o.loc[entered, "stage_entry_date"] = current[entered]
        lost = eligible & ~advance
        won = eligible & advance & (idx == 5)
        o.loc[lost | won, "actual_close_date"] = departure[lost | won]
        o.loc[lost, ["sales_stage", "deal_status"]] = "Closed Lost"
        o.loc[won, ["sales_stage", "deal_status"]] = "Closed Won"
        o.loc[lost | won, "previous_stage"] = stage
        o.loc[lost | won, "stage_entry_date"] = departure[lost | won]
        o.loc[lost, "lost_reason"] = rng.choice(
            REASONS,
            lost.sum(),
            p=[0.17, 0.15, 0.12, 0.07, 0.06, 0.10, 0.06, 0.07, 0.06, 0.06, 0.02, 0.06],
        )
        competitor_lost = lost & o.competitor_present.to_numpy() & (rng.random(size) < 0.28)
        o.loc[competitor_lost, "lost_reason"] = "Competitor selected"
        active = eligible & advance & (idx < 5)
        current = departure
    history = pd.concat(histories, ignore_index=True)
    history.insert(0, "transition_id", np.arange(1, len(history) + 1))
    terminal = o.actual_close_date.fillna(snapshot)
    counts = 1 + rng.poisson(1 + o.engagement_score / 25)
    oi = np.repeat(np.arange(size), counts)
    lifetime = (terminal - o.created_date).dt.days.to_numpy()
    activity_days = (rng.random(len(oi)) * (lifetime[oi] + 1)).astype(int)
    activities = pd.DataFrame(
        {
            "activity_id": np.arange(1, len(oi) + 1),
            "opportunity_id": oi + 1,
            "activity_date": o.created_date.to_numpy()[oi] + activity_days.astype("timedelta64[D]"),
            "activity_type": rng.choice(
                [
                    "Email",
                    "Phone Call",
                    "Meeting",
                    "Product Demo",
                    "Proposal",
                    "Negotiation",
                    "Follow-up",
                    "Contract Review",
                ],
                len(oi),
                p=[0.28, 0.22, 0.14, 0.07, 0.05, 0.05, 0.15, 0.04],
            ),
            "duration_minutes": rng.integers(5, 61, len(oi)),
            "outcome": np.where(
                rng.random(len(oi)) < o.engagement_score.to_numpy()[oi] / 100,
                "Engaged",
                "No response",
            ),
            "sales_rep_id": o.sales_rep_id.to_numpy()[oi],
            "customer_id": o.customer_id.to_numpy()[oi],
        }
    )
    # Stage-specific activities cannot occur before a stage was actually reached.
    activity_rng = np.random.default_rng(seed + 301)
    observed_stage = np.zeros(len(activities), dtype=int)
    for idx, stage in enumerate(STAGES[1:], 1):
        entries = history[history.sales_stage.eq(stage)].set_index("opportunity_id").entry_date
        reached = activities.opportunity_id.map(entries)
        observed_stage[(activities.activity_date >= reached).to_numpy()] = idx
    activities["activity_type"] = activity_rng.choice(
        ["Email", "Phone Call", "Meeting", "Follow-up"], len(activities), p=[0.36, 0.27, 0.17, 0.20]
    )
    for minimum, label, rate in [
        (3, "Product Demo", 0.18),
        (4, "Proposal", 0.14),
        (5, "Negotiation", 0.20),
        (5, "Contract Review", 0.14),
    ]:
        eligible_activity = (observed_stage >= minimum) & (
            activity_rng.random(len(activities)) < rate
        )
        activities.loc[eligible_activity, "activity_type"] = label
    o["last_activity_date"] = o.opportunity_id.map(
        activities.groupby("opportunity_id").activity_date.max()
    )
    o["activity_gap_days"] = (terminal - o.last_activity_date).dt.days
    open_mask = o.deal_status == "Open"
    o.loc[open_mask & (o.activity_gap_days > 30), "deal_status"] = "Stalled"
    o["next_follow_up_date"] = (
        o.last_activity_date + pd.to_timedelta(rng.integers(3, 18, size), unit="D")
    ).where(open_mask & (rng.random(size) > 0.16))
    o["sales_cycle_days"] = (o.actual_close_date - o.created_date).dt.days
    o["total_opportunity_age_days"] = (terminal - o.created_date).dt.days
    o["days_in_current_stage"] = (terminal - o.stage_entry_date).dt.days
    o["quarter"] = o.created_date.dt.quarter
    o["month"] = o.created_date.dt.month
    o["year"] = o.created_date.dt.year
    won = o[o.deal_status == "Closed Won"]
    customers["customer_lifetime_value"] = customers.customer_id.map(
        won.groupby("customer_id").net_deal_value.sum()
    ).fillna(0)
    customers["active_products"] = (
        customers.customer_id.map(won.groupby("customer_id").product.nunique())
        .fillna(0)
        .astype(int)
    )
    contracts = won[
        ["opportunity_id", "customer_id", "contract_type", "net_deal_value", "actual_close_date"]
    ].copy()
    contracts.insert(0, "contract_id", np.arange(1, len(contracts) + 1))
    targets = pd.MultiIndex.from_product(
        [
            pd.date_range(
                pd.Timestamp(history_start).replace(day=1),
                snapshot + pd.DateOffset(months=12),
                freq="MS",
            ),
            reps.sales_rep_id,
        ],
        names=["period", "sales_rep_id"],
    ).to_frame(index=False)
    targets["target"] = targets.sales_rep_id.map(reps.set_index("sales_rep_id").monthly_target)
    targets["region"] = targets.sales_rep_id.map(reps.set_index("sales_rep_id").region)
    return {
        "opportunities": o.drop(columns=["base_price", "account_manager"]),
        "customers": customers,
        "accounts": customers[["customer_id", "account_manager"]]
        .rename(columns={"customer_id": "account_id"})
        .assign(customer_id=customers.customer_id),
        "sales_reps": reps,
        "sales_teams": reps[["sales_team_id", "team", "region", "manager"]].drop_duplicates(),
        "products": products,
        "regions": geography,
        "industries": pd.DataFrame({"industry": customers.industry.unique()}),
        "lead_sources": pd.DataFrame({"lead_source": o.lead_source.unique()}),
        "stages": pd.DataFrame({"sales_stage": STAGES, "stage_order": range(6)}),
        "activities": activities,
        "stage_history": history,
        "targets": targets,
        "forecast_periods": targets[["period"]].drop_duplicates(),
        "lost_reasons": pd.DataFrame({"lost_reason": REASONS}),
        "competitors": pd.DataFrame(
            {"competitor_name": ["None", "Competitor A", "Competitor B", "Competitor C"]}
        ),
        "contracts": contracts,
    }


def introduce_issues(tables: dict[str, pd.DataFrame], seed: int) -> dict[str, pd.DataFrame]:
    """Inject disjoint defects; never persist an uncorrupted opportunity oracle."""
    result = {name: frame.copy() for name, frame in tables.items()}
    rng = np.random.default_rng(seed + 7)
    o = result["opportunities"]
    batches = np.array_split(rng.permutation(len(o))[: max(10, len(o) // 20)], 10)
    for ids, col, value in zip(
        batches,
        [
            "sales_rep_id",
            "industry",
            "sales_stage",
            "discount_percentage",
            "opportunity_amount",
            "region",
            "created_date",
            "sales_cycle_days",
            "net_deal_value",
            "actual_close_date",
        ],
        [
            np.nan,
            None,
            "Bad stage",
            -5,
            -100,
            "Unknown",
            pd.Timestamp("2030-01-01"),
            -9,
            -200,
            pd.NaT,
        ],
    ):
        o.loc[ids, col] = value
    result["opportunities"] = pd.concat(
        [o, o.sample(frac=0.006, random_state=seed)], ignore_index=True
    )
    result["customers"] = pd.concat(
        [result["customers"], result["customers"].sample(frac=0.01, random_state=seed)],
        ignore_index=True,
    )
    return result
