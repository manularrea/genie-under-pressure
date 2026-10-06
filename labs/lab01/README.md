# Lab 1 — Legacy Autopsy

Abre `legacy/stored_procedures/sp_daily_customer_metrics.sql` o el notebook
`databricks/01_legacy/legacy_autopsy.py`. SQL Server no es requisito: el notebook
contiene el texto para que Genie tenga contexto; no ejecuta T-SQL en Spark.

1. Pide a Genie una explicación por etapas, entradas/salida y reglas confirmadas.
2. Compara con BUSINESS_CONTRACT. Señala comentarios obsoletos y supuestos.
3. Identifica cinco riesgos de migración: dinero, NULL, cardinalidad, tiempo y dedup.
4. Pide un refactor mínimo y documentación. No pedir “más rápido” sin plan de medición.
5. Propón pruebas con EDGE_CANCELLED, EDGE_NULL_MERCHANT, EDGE_DUP y EDGE_NEXT_DAY.

Entregable: nota Markdown y propuesta revisada de T-SQL. Sin SQL Server,
la equivalencia del refactor queda **pendiente de ejecución del origen**.
El siguiente lab sí ofrece una validación ejecutable con un oracle independiente.
