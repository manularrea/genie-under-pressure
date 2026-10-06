# Lab 2 — Semantic Migration

## Databricks

1. Ejecuta bootstrap en tu schema personal. Inspecciona Bronze.
2. Entrega el procedimiento y el contrato a Genie. Pide primero riesgos y supuestos.
3. Ejecuta `silver_START.py`, luego `reconcile.py`. Resultado inicial: 834 vs 1.007.
4. Usa los registros faltantes/sobrantes para localizar la divergencia. No cambies expected.
5. Corrige el notebook y reejecuta. Reconcile debe terminar con PASS, cuarentena incluida.
6. Solo entonces ejecuta Gold y documenta el grano cliente/día/moneda.

## Respaldo local / gate del PR

```bash
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
# Modifica el SQL; aplica los cambios equivalentes al notebook.
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
python3 -m unittest discover -s tests -v
```

SQLite es un respaldo didáctico, no un emulador de Spark/SQL Server. La comparación
independiente identifica deriva semántica. Para validar Spark real usa los notebooks
o `scripts/check_spark.py` con el runtime opcional.

Entrega el diff y `artifacts/reconciliation.json`. Un PASS local no demuestra
rendimiento ni validación del motor Databricks; registra el entorno utilizado.
