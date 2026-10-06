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
# MAGIC ## Reconciliación de filas completas (incluye multiplicidad y NULL)
# MAGIC El oracle es independiente; no representa un resultado observado de SQL Server.
# MAGIC Una comparación por hashes entre motores exige canonización; aquí usamos `exceptAll`.

# COMMAND ----------
COLUMNS = ["transaction_id", "account_id", "customer_id", "merchant_id", "merchant_name", "segment", "event_ts", "amount_minor", "currency", "status"]
actual = spark.table(f"{prefix}.silver").select(*COLUMNS)
expected = spark.table(f"{prefix}.expected_silver").select(*COLUMNS)
missing = expected.exceptAll(actual)
extra = actual.exceptAll(expected)
display(actual.groupBy("currency", "status").sum("amount_minor"))
display(missing.limit(30))
display(extra.limit(30))
q = spark.table(f"{prefix}.quarantine").select("transaction_id", "reasons")
eq = spark.table(f"{prefix}.expected_quarantine").select("transaction_id", "reasons")
report = {"actual_rows": actual.count(), "expected_rows": expected.count(), "missing_or_changed": missing.count(), "extra_or_changed": extra.count(), "quarantine_diff": q.exceptAll(eq).count() + eq.exceptAll(q).count()}
print(report)
assert report["missing_or_changed"] == report["extra_or_changed"] == report["quarantine_diff"] == 0, "MIGRATION FAILED: inspect the diff, do not change expected tables"
print("PASS: full daily snapshot and quarantine agree with the contract")
