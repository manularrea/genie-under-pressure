"""Synthetic NovaBank fixtures. No random source, secrets or customer data."""
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

REPORT_DAY = "2026-09-30"
FIELDS = ["transaction_id", "account_id", "merchant_id", "event_ts", "amount", "currency", "status", "updated_at", "source_row"]


def fixtures(size=20000):
    if size < 100 or size > 100000:
        raise ValueError("Use 100..100000 rows for this teaching fixture")
    accounts = [{"account_id": f"A{i:04}", "customer_id": f"C{i % 80:03}"} for i in range(200)]
    customers = [{"customer_id": f"C{i:03}", "segment": "RETAIL", "updated_at": "2026-09-01T00:00:00", "source_row": str(i)} for i in range(80)]
    customers.append({"customer_id": "C001", "segment": "PREMIUM", "updated_at": "2026-09-29T00:00:00", "source_row": "80"})
    merchants = [{"merchant_id": f"M{i:03}", "merchant_name": f"Synthetic merchant {i:03}", "updated_at": "2026-09-01T00:00:00", "source_row": str(i)} for i in range(40)]
    merchants.append({"merchant_id": "M001", "merchant_name": "Synthetic merchant 001 renamed", "updated_at": "2026-09-29T00:00:00", "source_row": "40"})
    transactions = []
    for i in range(size):
        day = datetime(2026, 9, 11) + timedelta(days=i % 20, seconds=(i * 7919) % 86400)
        minor = ((i * 137) % 250000) + 1
        if i % 17 == 0:
            minor = -minor
        transactions.append(dict(zip(FIELDS, [f"T{i:06}", f"A{i % 200:04}", "" if i % 31 == 0 else f"M{i % 40:03}", day.isoformat(), f"{minor / 100:.2f}", "USD" if i % 3 == 0 else "COP", "CANCELLED" if i % 7 == 0 else "POSTED", "2026-09-30T23:59:59", str(i)])))
    edge_values = [
        ("EDGE_MIDNIGHT", "M001", "2026-09-30T00:00:00", "12.34", "COP", "POSTED"),
        ("EDGE_END", "M001", "2026-09-30T23:59:59", "-12.34", "COP", "POSTED"),
        ("EDGE_NEXT_DAY", "M001", "2026-10-01T00:00:00", "99.00", "COP", "POSTED"),
        ("EDGE_PREV_DAY", "M001", "2026-09-29T23:59:59", "99.00", "COP", "POSTED"),
        ("EDGE_NULL_MERCHANT", "", "2026-09-30T10:00:00", "10.01", "USD", "POSTED"),
        ("EDGE_UNKNOWN_MERCHANT", "M999", "2026-09-30T10:01:00", "10.02", "USD", "POSTED"),
        ("EDGE_CANCELLED", "M002", "2026-09-30T10:02:00", "25.00", "COP", "CANCELLED"),
        ("EDGE_BAD_DATE", "M001", "2026-09-31T10:00:00", "1.00", "COP", "POSTED"),
        ("EDGE_BAD_AMOUNT", "M001", "2026-09-30T10:00:00", "oops", "COP", "POSTED"),
        ("EDGE_BAD_ACCOUNT", "M001", "2026-09-30T10:00:00", "1.00", "COP", "POSTED"),
        ("EDGE_DUP", "M001", "2026-09-30T10:00:00", "100.00", "COP", "POSTED"),
        ("EDGE_TIE", "M001", "2026-09-30T11:00:00", "30.00", "COP", "POSTED"),
    ]
    for offset, (key, merchant, ts, amount, currency, status) in enumerate(edge_values):
        transactions.append(dict(zip(FIELDS, [key, "A0001", merchant, ts, amount, currency, status, "2026-09-30T23:59:59", str(size + offset)])))
    transactions[-3]["account_id"] = "A9999"
    for key, amount, status, update in [("EDGE_DUP", "75.00", "CANCELLED", "2026-10-01T00:00:01"), ("EDGE_TIE", "31.00", "POSTED", "2026-09-30T23:59:59")]:
        prior = next(row for row in transactions if row["transaction_id"] == key)
        transactions.append({**prior, "amount": amount, "status": status, "updated_at": update, "source_row": str(len(transactions))})
    return {"transactions": transactions, "accounts": accounts, "customers": customers, "merchants": merchants}


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate(root=Path("."), size=20000):
    tables = fixtures(size)
    for name, rows in tables.items():
        write_csv(root / "data/raw" / f"{name}.csv", rows)
    seed = dict(tables["transactions"][0], transaction_id="DRIFT001", event_ts="2026-09-30T12:00:00", amount="1,245.50", source_system="LEGACY_US")
    write_csv(root / "data/corrupted/transactions_schema_drift.csv", [seed])
    write_csv(root / "data/corrupted/transactions_bad_dates.csv", [row for row in tables["transactions"] if row["transaction_id"] == "EDGE_BAD_DATE"])
    write_csv(root / "data/corrupted/transactions_duplicates.csv", [row for row in tables["transactions"] if row["transaction_id"] in ("EDGE_DUP", "EDGE_TIE")])
    return tables


if __name__ == "__main__":
    generate()
