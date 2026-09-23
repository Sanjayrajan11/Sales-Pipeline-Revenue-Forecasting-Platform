"""Shared configuration, currency formatting and safe arithmetic."""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["Lead", "Qualified", "Discovery", "Demo", "Proposal", "Negotiation"]
ACTIVE = ["Open", "Stalled"]


def config() -> dict:
    """Read portable config and optional environment overrides."""
    result = yaml.safe_load((ROOT / "config/config.yaml").read_text())
    result["dataset_size"] = int(os.getenv("DATASET_SIZE", result["dataset_size"]))
    result["seed"] = int(os.getenv("SEED", result["seed"]))
    if not 100 <= result["dataset_size"] <= 1000000:
        raise ValueError("DATASET_SIZE must be between 100 and 1,000,000.")
    return result


def ratio(numerator: float, denominator: float) -> float:
    """Undefined ratios are NaN, never misleading zero or infinity."""
    return float(numerator / denominator) if denominator else float("nan")


def inr(value: float) -> str:
    """Format rupees using Indian digit grouping."""
    if pd.isna(value) or not np.isfinite(value):
        return "N/A"
    sign = "-" if value < 0 else ""
    digits = str(round(abs(value)))
    tail, head = digits[-3:], digits[:-3]
    parts = []
    while head:
        parts.insert(0, head[-2:])
        head = head[:-2]
    return sign + "₹" + ",".join(parts + [tail])


def csv_bytes(frame: pd.DataFrame) -> bytes:
    """UTF-8 BOM supports Indian currency in spreadsheet viewers."""
    return frame.to_csv(index=False).encode("utf-8-sig")
