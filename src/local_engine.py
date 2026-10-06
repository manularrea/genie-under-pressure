"""Offline lab engine: SQLite implements the pipeline, Python is the oracle."""
import csv
import re
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from src.reference import COLUMNS

ROOT = Path(__file__).resolve().parents[1]


def minor(value):
    if value is None or not re.fullmatch(r"-?\d{1,16}\.\d{2}", value):
        return None
    return int(Decimal(value) * 100)


def valid_ts(value):
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
            return None
        return datetime.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        return None


def connect(tables):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.create_function("amount_minor", 1, minor, deterministic=True)
    db.create_function("valid_ts", 1, valid_ts, deterministic=True)
    for name, rows in tables.items():
        columns = list(rows[0])
        db.execute(f"CREATE TABLE {name} ({', '.join(c + ' TEXT' for c in columns)})")
        db.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' for _ in columns)})", [tuple(r[c] for c in columns) for r in rows])
    return db


def pipeline(tables, sql_path=None, report_day="2026-09-30"):
    db = connect(tables)
    sql = Path(sql_path or ROOT / "solutions/lab02/silver.sql").read_text()
    try:
        rows = [dict(r) for r in db.execute(sql, {"report_day": report_day})]
        return sorted(rows, key=lambda r: r["transaction_id"])
    finally:
        db.close()


def read_tables():
    return {name: list(csv.DictReader((ROOT / f"data/raw/{name}.csv").open())) for name in ("transactions", "accounts", "customers", "merchants")}
