"""Compare an actual SQL Server CSV export with the checked contract snapshot."""
import argparse
import csv
import json
import sys
from src.local_engine import read_tables
from src.reference import COLUMNS, reference, metrics

parser = argparse.ArgumentParser()
parser.add_argument("csv", help="UTF-8 CSV with headers; empty SQL NULL fields")
args = parser.parse_args()
with open(args.csv, encoding="utf-8-sig", newline="") as handle:
    actual = list(csv.DictReader(handle))
for row in actual:
    if set(row) != set(COLUMNS):
        raise ValueError("CSV columns must exactly match the stored procedure result")
    row["amount_minor"] = int(row["amount_minor"])
    for col in ("merchant_id", "merchant_name"):
        row[col] = row[col] or None
actual.sort(key=lambda r: r["transaction_id"])
expected, _ = reference(read_tables())
print(json.dumps({"passed": actual == expected, "expected": metrics(expected), "sql_server_export": metrics(actual)}, indent=2))
sys.exit(0 if actual == expected else 1)
