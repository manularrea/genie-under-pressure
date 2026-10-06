"""Regenerate fixtures and independent expected outputs explicitly."""
import argparse
import json
from pathlib import Path
from src.fixtures import generate, write_csv
from src.reference import reference, metrics

parser = argparse.ArgumentParser()
parser.add_argument("--rows", type=int, default=20000)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
tables = generate(root, args.rows)
rows, quarantine = reference(tables)
write_csv(root / "data/expected/silver.csv", rows)
write_csv(root / "data/expected/quarantine.csv", quarantine)
(root / "data/expected/expected_metrics.json").write_text(json.dumps({"provenance": "Independent Python business-contract oracle, not a SQL Server run", "report_day": "2026-09-30", "raw_rows": len(tables["transactions"]), "quarantine_rows": len(quarantine), **metrics(rows)}, indent=2) + "\n")
print(f"Generated {len(tables['transactions'])} raw / {len(rows)} silver / {len(quarantine)} quarantine rows")
