# Preserve NovaBank daily snapshot semantics

The candidate dropped cancelled transactions and records with missing merchants,
and included the next day's midnight. Restore cancellation history, the optional
merchant join and the half-open day window.

Validation to record after execution:

```bash
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
python3 -m unittest discover -s tests -v
```

Attach the observed reconciliation. The prepared solution returns 1,007 daily
records and the three expected quarantine records. Full rows must agree, including
keys, signed minor amounts and NULLs. If the candidate has not been run, do not
claim these results for the PR.

SQL Server execution, Databricks workspace execution and production-scale
performance are separate evidence; do not infer them from the local fallback.
