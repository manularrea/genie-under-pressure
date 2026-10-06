"""Independent Python contract oracle; NOT a measured SQL Server execution."""
import hashlib
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal

COLUMNS = ["transaction_id", "account_id", "customer_id", "merchant_id", "merchant_name", "segment", "event_ts", "amount_minor", "currency", "status"]


def latest(rows, key):
    result = {}
    for row in rows:
        old = result.get(row[key])
        rank = (row["updated_at"], int(row["source_row"]))
        if old is None or rank > (old["updated_at"], int(old["source_row"])):
            result[row[key]] = row
    return result


def reference(tables, report_day="2026-09-30"):
    start = datetime.fromisoformat(report_day)
    end = start + timedelta(days=1)
    accounts = {r["account_id"]: r for r in tables["accounts"]}
    customers = latest(tables["customers"], "customer_id")
    merchants = latest(tables["merchants"], "merchant_id")
    output, quarantine = [], []
    for row in latest(tables["transactions"], "transaction_id").values():
        reasons = []
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", row["event_ts"]):
                raise ValueError("format")
            ts = datetime.fromisoformat(row["event_ts"])
        except ValueError:
            ts = None
            reasons.append("INVALID_TIMESTAMP")
        if not re.fullmatch(r"-?\d{1,16}\.\d{2}", row["amount"]):
            reasons.append("INVALID_AMOUNT")
        if row["account_id"] not in accounts:
            reasons.append("UNKNOWN_ACCOUNT")
        if row["currency"] not in ("COP", "USD"):
            reasons.append("INVALID_CURRENCY")
        if row["status"] not in ("POSTED", "CANCELLED"):
            reasons.append("INVALID_STATUS")
        if reasons:
            quarantine.append({"transaction_id": row["transaction_id"], "reasons": ";".join(reasons)})
            continue
        if not start <= ts < end:
            continue
        account = accounts[row["account_id"]]
        customer = customers[account["customer_id"]]
        merchant = merchants.get(row["merchant_id"])
        output.append(dict(zip(COLUMNS, [row["transaction_id"], row["account_id"], account["customer_id"], row["merchant_id"] or None, merchant["merchant_name"] if merchant else None, customer["segment"], row["event_ts"], int(Decimal(row["amount"]) * 100), row["currency"], row["status"]])))
    return sorted(output, key=lambda r: r["transaction_id"]), sorted(quarantine, key=lambda r: r["transaction_id"])


def fingerprint(rows):
    canonical = json.dumps(sorted(rows, key=lambda r: r["transaction_id"]), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def metrics(rows):
    totals, posted, hashes = {}, {}, {}
    for currency in sorted({r["currency"] for r in rows}):
        part = [r for r in rows if r["currency"] == currency]
        totals[currency] = sum(r["amount_minor"] for r in part)
        posted[currency] = sum(r["amount_minor"] for r in part if r["status"] == "POSTED")
        hashes[currency] = fingerprint(part)
    return {"rows": len(rows), "distinct_keys": len({r["transaction_id"] for r in rows}), "distinct_customers": len({r["customer_id"] for r in rows}), "cancelled_rows": sum(r["status"] == "CANCELLED" for r in rows), "null_merchant_rows": sum(r["merchant_name"] is None for r in rows), "amount_minor_by_currency": totals, "posted_minor_by_currency": posted, "partition_sha256": hashes, "row_sha256": fingerprint(rows)}
