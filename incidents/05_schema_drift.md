# INCIDENT E05 — Schema Drift

**08:05.** La fuente LEGACY_US empieza a enviar `1,245.50` y `source_system`.
La ruta anterior esperaba un importe decimal sin separadores de miles.

En Databricks ejecuta la primera celda de `databricks/experiments/schema_drift.py`.
El CAST estricto falla de verdad. Local: `python3 -m scripts.demo schema-drift`.
Fixture: `data/corrupted/transactions_schema_drift.csv` (delta pequeño, no día completo).

Tu misión: diagnosticar, preguntar por formato/locale, poner en cuarentena y
proponer una normalización **específica de esa fuente**. `1.245,50` tiene otra
convención. Nunca quitar signos o convertir fallos a 0 para lograr éxito.
