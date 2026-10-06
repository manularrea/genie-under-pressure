import argparse
import json
import sys
from pathlib import Path
from src.local_engine import pipeline, read_tables
from src.reference import reference, metrics

parser = argparse.ArgumentParser(description="Reconcile a candidate with the independent contract")
parser.add_argument("--candidate", default="labs/lab02/silver.sql")
parser.add_argument("--output", default="artifacts/reconciliation.json")
args = parser.parse_args()
tables = read_tables()
expected, quarantine = reference(tables)
actual = pipeline(tables, args.candidate)
e = {r["transaction_id"]: r for r in expected}
a = {r["transaction_id"]: r for r in actual}
report = {"candidate": args.candidate, "passed": actual == expected, "expected": metrics(expected), "actual": metrics(actual), "missing_keys": sorted(e.keys() - a.keys()), "extra_keys": sorted(a.keys() - e.keys()), "changed_keys": sorted(k for k in e.keys() & a.keys() if e[k] != a[k]), "quarantine_rows": len(quarantine)}
path = Path(args.output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
sys.exit(0 if report["passed"] else 1)
