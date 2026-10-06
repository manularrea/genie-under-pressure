# PR ficticio para revisión — NO usar como descripción verdadera

## Migrates daily transactions to Spark

- [x] Preserves existing behavior
- [x] Handles cancellations and NULLs
- [x] Tested against SQL Server
- [x] Improves performance by 40%

Candidate: `labs/lab02/silver.sql` / `databricks/02_silver/silver_START.py`.

Estas afirmaciones son parte del incidente. El candidato conserva solo POSTED,
usa join obligatorio al comercio y un límite superior inclusivo. No existen
mediciones de SQL Server ni benchmarks que respalden esta descripción.

Tu tarea: pedir cambios con evidencia y redactar una descripción honesta.
