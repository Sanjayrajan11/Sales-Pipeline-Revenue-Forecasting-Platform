"""Atomic SQLite publication and read-only query execution."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from src.utils import ROOT

DB = ROOT / "database" / "sales.db"


def publish(tables: dict[str, pd.DataFrame], path: Path = DB) -> None:
    """Build in a sibling file; publish only after integrity and SQL checks pass."""
    temp = path.with_suffix(".building.db")
    with closing(sqlite3.connect(temp)) as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="replace", index=False, chunksize=10000)
        connection.executescript((ROOT / "database/schema.sql").read_text())
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed.")
        for file in sorted((ROOT / "sql").glob("*.sql")):
            sql = "\n".join(
                line for line in file.read_text().splitlines() if not line.lstrip().startswith("--")
            )
            for statement in sql.split(";"):
                if statement.strip():
                    connection.execute(statement).fetchall()
        connection.commit()
    os.replace(temp, path)


def read_table(name: str, path: Path = DB) -> pd.DataFrame:
    """Restrict identifiers to an existing table, open database read-only."""
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as con:
        names = {
            row[0]
            for row in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
        }
        if name not in names:
            raise ValueError("Unknown analytical table.")
        frame = pd.read_sql_query(f'SELECT * FROM "{name}"', con)
    for col in frame.columns:
        if col.endswith("_date") or col in ["period", "cutoff"]:
            frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frame


def detail_events(opportunity_id: int, path: Path = DB) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parameterised indexed drill-down avoids loading all activity records into UI."""
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as con:
        frames = tuple(
            pd.read_sql_query(
                f"SELECT * FROM {name} WHERE opportunity_id = ? ORDER BY {order}",
                con,
                params=[int(opportunity_id)],
            )
            for name, order in [("stage_history", "entry_date"), ("activities", "activity_date")]
        )
    return frames
