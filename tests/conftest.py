"""Small deterministic integration fixture, separate from the full portfolio data."""

import pytest

from src.data_cleaning import clean
from src.data_generation import generate, introduce_issues
from src.feature_engineering import enrich
from src.risk_engine import score


@pytest.fixture(scope="session")
def raw():
    return generate(1200, 17, "2026-08-31", "2023-01-01")


@pytest.fixture(scope="session")
def dirty(raw):
    return introduce_issues(raw, 17)


@pytest.fixture(scope="session")
def clean_tables(dirty):
    tables, _, _ = clean(dirty, "2026-08-31")
    tables = enrich(tables, "2026-08-31")
    tables["opportunities"] = score(tables["opportunities"], "2026-08-31", [14, 18, 21, 18, 28, 21])
    return tables
