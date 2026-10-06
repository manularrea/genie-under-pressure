"""Build self-contained Databricks source notebooks without external downloads."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path, text):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


header = '''# Databricks notebook source
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
'''

fixture_code = (ROOT / "src/fixtures.py").read_text().split('if __name__ == "__main__":')[0]
reference_code = (ROOT / "src/reference.py").read_text()
query_code = (ROOT / "src/spark_queries.py").read_text()

bootstrap = header + '''
# COMMAND ----------
# MAGIC %md
# MAGIC ## Bootstrap — una ejecución por participante
# MAGIC Construye 20.014 filas en memoria para un fixture pequeño. No descarga paquetes ni datos.
# MAGIC Escribe únicamente tablas con nombres de este workshop en el schema seleccionado.
# MAGIC Reejecutar sobrescribe esas tablas. Elige un schema personal nuevo antes de comenzar.

# COMMAND ----------
''' + fixture_code + '\n' + reference_code + '''
tables = fixtures()
expected, expected_quarantine = reference(tables)
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {prefix}")
for name, rows in tables.items():
    ddl = ", ".join(f"{col} STRING" for col in rows[0])
    spark.createDataFrame([tuple(r.values()) for r in rows], ddl).write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.bronze_{name}")
ddl = ", ".join(f"{col} {'BIGINT' if col == 'amount_minor' else 'STRING'}" for col in COLUMNS)
spark.createDataFrame([tuple(r[col] for col in COLUMNS) for r in expected], ddl).write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.expected_silver")
spark.createDataFrame([(r["transaction_id"], r["reasons"]) for r in expected_quarantine], "transaction_id STRING, reasons STRING").write.format("delta").mode("overwrite").saveAsTable(f"{prefix}.expected_quarantine")
print({"raw_rows": len(tables["transactions"]), "expected_silver": len(expected), "quarantine": len(expected_quarantine)})
display(spark.table(f"{prefix}.bronze_transactions").limit(10))
'''
write("databricks/00_setup/bootstrap.py", bootstrap)

for path, flawed in [("databricks/02_silver/silver_START.py", True), ("solutions/lab02/silver_SOLUTION.py", False)]:
    body = header + '''
# COMMAND ----------
# MAGIC %md
# MAGIC ## Migración — ''' + ("START: propuesta para revisar" if flawed else "SOLUTION: contrato preservado") + '''
# MAGIC Ejecuta bootstrap antes. El resultado es un snapshot diario, no un feed incremental.
# MAGIC No cambies la salida esperada. Después ejecuta `reconcile.py`.

# COMMAND ----------
''' + query_code + '\n' + f'''for statement in queries(prefix, flawed={flawed}):
    spark.sql(statement)
spark.table("quarantine_out").write.format("delta").mode("overwrite").saveAsTable(f"{{prefix}}.quarantine")
spark.table("silver_out").write.format("delta").mode("overwrite").saveAsTable(f"{{prefix}}.silver")
display(spark.table(f"{{prefix}}.silver").limit(20))
'''
    write(path, body)

write("databricks/03_validation/reconcile.py", header + '''
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
''')

write("databricks/04_gold/customer_daily.py", header + '''
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
''')

write("databricks/experiments/schema_drift.py", '''# Databricks notebook source
# MAGIC %md
# MAGIC # E05: formato de importe inesperado
# MAGIC Ejecuta la celda estricta sola: fallará deliberadamente.
# MAGIC Usa Genie para diagnosticar. No normalices formatos ambiguos sin contrato de la fuente.

# COMMAND ----------
spark.sql("SELECT CAST('1,245.50' AS DECIMAL(18,2)) AS amount").show()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Después de confirmar el contrato de la fuente LEGACY_US
# MAGIC Miles con coma, decimal con punto, exactamente dos decimales. Otras entradas van a cuarentena.
# MAGIC Esta regla es específica de LEGACY_US y no sustituye el parser de todas las fuentes.

# COMMAND ----------
rows = [('DRIFT001', '1,245.50'), ('DRIFT002', '1.245,50'), ('DRIFT003', 'garbage')]
spark.createDataFrame(rows, 'transaction_id STRING, amount STRING').createOrReplaceTempView('drift_input')
display(spark.sql(r"""SELECT *, CASE WHEN amount RLIKE '^-?([0-9]{1,3}(,[0-9]{3})+|[0-9]+)[.][0-9]{2}$'
THEN try_cast(replace(amount, ',', '') AS DECIMAL(18,2)) END AS normalized_amount FROM drift_input"""))
''')

write("databricks/01_bronze/inspect.py", header + '''
# COMMAND ----------
# MAGIC %md
# MAGIC ## Bronze conserva el raw
# MAGIC No infiere tipos ni borra duplicados. Silver aplica el contrato.

# COMMAND ----------
display(spark.sql(f"DESCRIBE TABLE {prefix}.bronze_transactions"))
display(spark.sql(f"SELECT transaction_id, count(*) copies FROM {prefix}.bronze_transactions GROUP BY transaction_id HAVING count(*) > 1"))
display(spark.table(f"{prefix}.bronze_transactions").filter("transaction_id LIKE 'EDGE_%'"))
''')

write("databricks/01_legacy/legacy_autopsy.py", '''# Databricks notebook source
# MAGIC %md
# MAGIC # Lab 1: autopsia de T-SQL
# MAGIC El procedimiento siguiente es contexto de lectura para Genie Code.
# MAGIC No se ejecuta T-SQL en Spark. Pega el contrato en el chat y pide reglas/supuestos.

# COMMAND ----------
legacy_tsql = ''' + repr((ROOT / "legacy/stored_procedures/sp_daily_customer_metrics.sql").read_text()) + '''
print(legacy_tsql)

# COMMAND ----------
# MAGIC %md
# MAGIC Entrega: etapas, reglas confirmadas, comentarios obsoletos, riesgos y refactor mínimo.
# MAGIC La ejecución en SQL Server es opcional y tiene su comparador en legacy/README.md.
''')

print("Built 8 self-contained notebook files")
