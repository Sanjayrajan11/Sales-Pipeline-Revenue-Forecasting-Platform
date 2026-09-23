"""Execute every documented query and reconcile core financial metrics independently."""

import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.database import DB
from src.utils import ROOT


def verify() -> int:
    """Fail on any SQL error; return the executed statement count."""
    count = 0
    with closing(sqlite3.connect(f"{DB.as_uri()}?mode=ro", uri=True)) as con:
        for file in sorted((ROOT / "sql").glob("*.sql")):
            sql = "\n".join(
                line for line in file.read_text().splitlines() if not line.lstrip().startswith("--")
            )
            for statement in sql.split(";"):
                if statement.strip():
                    con.execute(statement).fetchall()
                    count += 1
        won = con.execute(
            "SELECT SUM(net_deal_value) FROM opportunities WHERE deal_status='Closed Won'"
        ).fetchone()[0]
        expected = con.execute("SELECT closed_won_revenue FROM pipeline_kpis").fetchone()[0]
        if abs(won - expected) > max(0.01, abs(expected) * 1e-12):
            raise AssertionError("SQL and Python bookings do not reconcile.")
    print(f"{count} SQL statements executed; SQL/Python bookings reconcile.")
    return count


if __name__ == "__main__":
    verify()
