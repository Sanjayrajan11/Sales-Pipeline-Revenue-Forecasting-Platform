"""Export portable CSVs for the documented Power BI star model."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.database import read_table
from src.utils import ROOT, config


def export() -> None:
    """Keep selected-model backtest rows only to avoid double counting predictions."""
    destination = ROOT / "data/processed/powerbi"
    destination.mkdir(parents=True, exist_ok=True)
    names = {
        "opportunities": "FactOpportunities",
        "activities": "FactActivities",
        "stage_history": "FactStageVisits",
        "targets": "FactTargets",
        "forecast": "FactForecast",
        "customers": "DimCustomer",
        "sales_reps": "DimSalesRep",
        "products": "DimProduct",
        "industries": "DimIndustry",
        "stages": "DimStage",
        "lost_reasons": "DimLostReason",
    }
    for table, name in names.items():
        frame = read_table(table)
        if table == "stages":
            frame = pd.concat(
                [
                    frame,
                    pd.DataFrame(
                        {"sales_stage": ["Closed Won", "Closed Lost"], "stage_order": [6, 7]}
                    ),
                ],
                ignore_index=True,
            )
        frame.to_csv(destination / f"{name}.csv", index=False, encoding="utf-8-sig")
    read_table("regions")[["region"]].drop_duplicates().to_csv(
        destination / "DimRegion.csv", index=False
    )
    o = read_table("opportunities")
    o[["opportunity_id"]].to_csv(destination / "DimOpportunity.csv", index=False)
    selected = read_table("forecast").iloc[0].model
    b = read_table("backtest")
    b[b.model.eq(selected)].to_csv(destination / "FactBacktest.csv", index=False)
    cfg = config()
    dates = pd.DataFrame(
        {
            "Date": pd.date_range(
                cfg["history_start"], pd.Timestamp(cfg["as_of"]) + pd.DateOffset(years=2)
            )
        }
    )
    dates["Year"], dates["Month"], dates["Quarter"] = (
        dates.Date.dt.year,
        dates.Date.dt.month,
        dates.Date.dt.quarter,
    )
    dates.to_csv(destination / "DimDate.csv", index=False)
    print(f"Exported {len(list(destination.glob('*.csv')))} Power BI model files.")


if __name__ == "__main__":
    export()
