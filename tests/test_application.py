"""Real Streamlit AppTest navigation, scenario/filter behavior and warehouse checks."""

import sqlite3
from contextlib import closing

import pytest
from streamlit.testing.v1 import AppTest

from database.database import DB, detail_events, read_table
from src.utils import ROOT

PAGES = [
    "Command Center",
    "Pipeline Flow",
    "Revenue Outlook",
    "Opportunity Desk",
    "Opportunity Detail",
    "Sales Performance",
    "Funnel Diagnostics",
    "Customer & Market",
    "Scenario Lab",
    "Action Queue",
    "Data Explorer",
    "Methodology",
]


@pytest.fixture(scope="module")
def app():
    if not DB.exists():
        pytest.skip("Run python run_pipeline.py to enable full application integration tests.")
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=90).run()


@pytest.mark.parametrize("page", PAGES)
def test_page_loads(app, page):
    app.selectbox(key="workspace").select(page).run()
    assert not app.exception, [x.message for x in app.exception]
    assert not app.error, [x.value for x in app.error]
    assert app.title[0].value == page
    assert all("bound method" not in heading.value for heading in app.subheader)


def test_scenario_widget_changes_revenue(app):
    app.selectbox(key="workspace").select("Scenario Lab").run()
    before = app.metric[0].value
    app.slider[0].set_value(10).run()
    assert not app.exception and not app.error
    assert app.metric[0].value != before
    app.slider[0].set_value(0).run()


def test_empty_search_state(app):
    app.selectbox(key="workspace").select("Data Explorer").run()
    app.text_input(key="search_Data Explorer").set_value("no-such-record-xyz").run()
    assert any("No records match" in x.value for x in app.info)
    assert not app.exception and not app.error
    app.text_input(key="search_Data Explorer").set_value("").run()


def test_global_region_filter(app):
    app.selectbox(key="workspace").select("Command Center").run()
    before = app.metric[0].value
    app.multiselect(key="regions").set_value(["North"]).run()
    assert app.metric[0].value != before
    assert not app.exception and not app.error
    app.multiselect(key="regions").set_value([]).run()


def test_unallocated_quota_warning(app):
    app.multiselect(key="products").set_value(["Data Advisory"]).run()
    assert any("not allocated" in x.value for x in app.info)
    assert not app.exception and not app.error
    app.multiselect(key="products").set_value([]).run()


def test_detail_indexed_lookup():
    if not DB.exists():
        pytest.skip("Pipeline required")
    visits, activities = detail_events(1)
    assert visits.opportunity_id.eq(1).all()
    assert activities.opportunity_id.eq(1).all()


def test_all_sql_and_reconciliation():
    if not DB.exists():
        pytest.skip("Pipeline required")
    from scripts.validate_sql import verify

    assert verify() == 42


def test_database_integrity():
    if not DB.exists():
        pytest.skip("Pipeline required")
    with closing(sqlite3.connect(DB)) as con:
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert len(read_table("opportunities")) > 0


def test_missing_database_recovery_message(monkeypatch, tmp_path):
    import database.database as warehouse

    monkeypatch.setattr(warehouse, 'DB', tmp_path / 'missing.db')
    isolated = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=90).run()
    assert not isolated.exception
    assert any('Run the pipeline' in message.value for message in isolated.warning)


def test_invalid_opportunity_has_useful_message(app):
    app.selectbox(key='workspace').select('Opportunity Detail').run()
    original = app.number_input(key='detail_id').value
    app.number_input(key='detail_id').set_value(99999999).run()
    assert not app.exception and not app.error
    assert any('outside the selected scope' in message.value for message in app.warning)
    app.number_input(key='detail_id').set_value(original).run()
