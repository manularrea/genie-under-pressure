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
# MAGIC ## Migración — START: propuesta para revisar
# MAGIC Ejecuta bootstrap antes. El resultado es un snapshot diario, no un feed incremental.
# MAGIC No cambies la salida esperada. Después ejecuta `reconcile.py`.

# COMMAND ----------
"""Spark SQL shared by generated Databricks notebooks and optional runtime test."""
import re


def queries(prefix, report_day="2026-09-30", flawed=False):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report_day):
        raise ValueError("report_day must be YYYY-MM-DD")
    statements = []
    columns = {
        "transactions": "transaction_id, account_id, merchant_id, event_ts, amount, currency, status, updated_at, source_row",
        "merchants": "merchant_id, merchant_name, updated_at, source_row",
        "customers": "customer_id, segment, updated_at, source_row",
    }
    for table, key in [("transactions", "transaction_id"), ("merchants", "merchant_id"), ("customers", "customer_id")]:
        statements.append(f"""CREATE OR REPLACE TEMP VIEW latest_{table} AS
        SELECT {columns[table]} FROM (
          SELECT *, ROW_NUMBER() OVER (PARTITION BY {key} ORDER BY updated_at DESC, CAST(source_row AS BIGINT) DESC) rn
          FROM {prefix}.bronze_{table}
        ) WHERE rn = 1""")
    statements.append(r"""CREATE OR REPLACE TEMP VIEW checked_tx AS
    SELECT t.*,
      try_cast(t.event_ts AS TIMESTAMP_NTZ) AS event_time,
      CASE WHEN t.amount RLIKE '^-?[0-9]{1,16}[.][0-9]{2}$'
        THEN cast(try_cast(t.amount AS DECIMAL(18,2)) * 100 AS BIGINT) END AS amount_minor,
      concat_ws(';',
        CASE WHEN NOT (t.event_ts RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}$') OR try_cast(t.event_ts AS TIMESTAMP_NTZ) IS NULL THEN 'INVALID_TIMESTAMP' END,
        CASE WHEN NOT (t.amount RLIKE '^-?[0-9]{1,16}[.][0-9]{2}$') OR try_cast(t.amount AS DECIMAL(18,2)) IS NULL THEN 'INVALID_AMOUNT' END,
        CASE WHEN a.account_id IS NULL THEN 'UNKNOWN_ACCOUNT' END,
        CASE WHEN t.currency NOT IN ('COP', 'USD') THEN 'INVALID_CURRENCY' END,
        CASE WHEN t.status NOT IN ('POSTED', 'CANCELLED') THEN 'INVALID_STATUS' END
      ) AS reasons
    FROM latest_transactions t LEFT JOIN __PREFIX__.bronze_accounts a ON t.account_id = a.account_id""".replace("__PREFIX__", prefix))
    statements.append("CREATE OR REPLACE TEMP VIEW quarantine_out AS SELECT transaction_id, reasons FROM checked_tx WHERE reasons <> ''")
    join_type = "JOIN" if flawed else "LEFT JOIN"
    boundary = "<=" if flawed else "<"
    status = "t.status = 'POSTED'" if flawed else "t.status IN ('POSTED', 'CANCELLED')"
    statements.append(f"""CREATE OR REPLACE TEMP VIEW silver_out AS
    SELECT t.transaction_id, t.account_id, a.customer_id,
      nullif(t.merchant_id, '') merchant_id, m.merchant_name, c.segment,
      date_format(t.event_time, "yyyy-MM-dd'T'HH:mm:ss") event_ts,
      t.amount_minor, t.currency, t.status
    FROM checked_tx t
    JOIN {prefix}.bronze_accounts a ON t.account_id = a.account_id
    JOIN latest_customers c ON a.customer_id = c.customer_id
    {join_type} latest_merchants m ON t.merchant_id = m.merchant_id
    WHERE t.reasons = '' AND {status}
      AND t.event_time >= CAST('{report_day}' AS TIMESTAMP_NTZ)
      AND t.event_time {boundary} CAST('{report_day}' AS TIMESTAMP_NTZ) + INTERVAL 1 DAY""")
    return statements

for statement in queries(prefix, flawed=True):
    spark.sql(statement)
spark.table("quarantine_out").write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.quarantine")
spark.table("silver_out").write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.silver")
display(spark.table(f"{prefix}.silver").limit(20))
