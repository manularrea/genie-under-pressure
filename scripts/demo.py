"""Deterministic teaching failures, independent of any LLM output."""
import argparse
from src.local_engine import pipeline, read_tables
from src.reference import reference, metrics

parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=["prompt-trap", "silent-loss", "schema-drift", "lying-pr"])
args = parser.parse_args()
tables = read_tables()
expected, _ = reference(tables)
if args.experiment == "prompt-trap":
    actual = [r for r in expected if r["merchant_name"] is not None]
    print(f"LEFT JOIN -> INNER JOIN: {len(expected)} -> {len(actual)}; omitted merchant is not an invalid transaction.")
elif args.experiment == "silent-loss":
    actual = [dict(r) for r in expected]
    # Identity corruption leaves row count and currency amounts unchanged.
    actual[0]["customer_id"] = "C999"
    a, e = metrics(actual), metrics(expected)
    print("Equal count:", a["rows"] == e["rows"], "Equal currency totals:", a["amount_minor_by_currency"] == e["amount_minor_by_currency"], "Equal content:", a["row_sha256"] == e["row_sha256"])
elif args.experiment == "schema-drift":
    from decimal import Decimal, InvalidOperation
    try:
        Decimal("1,245.50")
    except InvalidOperation:
        print("Strict baseline parser rejects 1,245.50. Quarantine first; normalize only with a source-specific approved US-format contract.")
else:
    actual = pipeline(tables, "labs/lab02/silver_START.sql")
    print(f"PR claims equivalence; evidence says {len(expected)} expected vs {len(actual)} actual. Request changes.")
