# Databricks notebook source
# MAGIC %md
# MAGIC # Genie Under Pressure — NovaBank
# MAGIC Datos 100 % sintéticos. Cómputo serverless; ejecución acotada.
# MAGIC Usa el mismo schema en todos los notebooks. No utilices un schema de producción.

# COMMAND ----------
import re
dbutils.widgets.text("catalog", spark.sql("SELECT current_catalog()").first()[0])
dbutils.widgets.text("schema", "genie_workshop_demo")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalog):
    raise ValueError("Select a catalog with a simple identifier for this workshop")
if not re.fullmatch(r"genie_workshop_[a-z0-9_]+", schema):
    raise ValueError("Use a personal schema beginning with genie_workshop_")
prefix = f"`{catalog}`.`{schema}`"

# COMMAND ----------
# MAGIC %md
# MAGIC ## Bootstrap — una ejecución por participante
# MAGIC Construye 20.014 filas en memoria para un fixture pequeño. No descarga paquetes ni datos.
# MAGIC Escribe únicamente tablas con nombres de este workshop en el schema seleccionado.
# MAGIC Reejecutar sobrescribe esas tablas. Elige un schema personal nuevo antes de comenzar.

# COMMAND ----------
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

tables = fixtures()
expected, expected_quarantine = reference(tables)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {prefix}")
for name, rows in tables.items():
    ddl = ", ".join(f"{col} STRING" for col in rows[0])
    spark.createDataFrame([tuple(r.values()) for r in rows], ddl).write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.bronze_{name}")
ddl = ", ".join(f"{col} {'BIGINT' if col == 'amount_minor' else 'STRING'}" for col in COLUMNS)
spark.createDataFrame([tuple(r[col] for col in COLUMNS) for r in expected], ddl).write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.expected_silver")
spark.createDataFrame([(r["transaction_id"], r["reasons"]) for r in expected_quarantine], "transaction_id STRING, reasons STRING").write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.expected_quarantine")
print({"raw_rows": len(tables["transactions"]), "expected_silver": len(expected), "quarantine": len(expected_quarantine)})
display(spark.table(f"{prefix}.bronze_transactions").limit(10))
