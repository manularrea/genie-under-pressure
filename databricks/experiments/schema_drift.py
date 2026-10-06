# Databricks notebook source
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
