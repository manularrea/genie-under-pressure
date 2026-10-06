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
# MAGIC ## Gold — producto de datos diario
# MAGIC Solo después de que reconcile.py termine con PASS. Nunca sumes monedas diferentes.

# COMMAND ----------
actual = spark.table(f"{prefix}.silver")
expected = spark.table(f"{prefix}.expected_silver")
assert actual.exceptAll(expected).limit(1).count() == 0 and expected.exceptAll(actual).limit(1).count() == 0, "Run reconciliation before Gold"
spark.sql(f"""CREATE OR REPLACE TABLE {prefix}.gold_customer_daily USING DELTA AS
SELECT customer_id, currency, substr(event_ts, 1, 10) report_day,
  count(*) historical_transactions,
  sum(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) cancelled_transactions,
  sum(CASE WHEN status = 'POSTED' THEN amount_minor ELSE 0 END) posted_amount_minor
FROM {prefix}.silver GROUP BY customer_id, currency, substr(event_ts, 1, 10)""")
display(spark.table(f"{prefix}.gold_customer_daily").orderBy("customer_id", "currency"))
