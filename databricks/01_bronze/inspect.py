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
# MAGIC ## Bronze conserva el raw
# MAGIC No infiere tipos ni borra duplicados. Silver aplica el contrato.

# COMMAND ----------
display(spark.sql(f"DESCRIBE TABLE {prefix}.bronze_transactions"))
display(spark.sql(f"SELECT transaction_id, count(*) copies FROM {prefix}.bronze_transactions GROUP BY transaction_id HAVING count(*) > 1"))
display(spark.table(f"{prefix}.bronze_transactions").filter("transaction_id LIKE 'EDGE_%'"))
