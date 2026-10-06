"""Optional actual Spark runtime test. Requires PySpark 3.5+ and Java."""
from pyspark.sql import SparkSession
from src.fixtures import fixtures
from src.reference import reference, COLUMNS
from src.spark_queries import queries

spark = (SparkSession.builder.master("local[2]").appName("genie-contract-test")
         .config("spark.driver.bindAddress", "127.0.0.1")
         .config("spark.driver.host", "127.0.0.1")
         .config("spark.sql.shuffle.partitions", "4").getOrCreate())
try:
    spark.sql("CREATE DATABASE IF NOT EXISTS genie_test")
    tables = fixtures(500)
    for name, rows in tables.items():
        schema = ", ".join(f"{col} STRING" for col in rows[0])
        spark.createDataFrame([tuple(r.values()) for r in rows], schema).createOrReplaceTempView(f"bronze_{name}")
    # Temp views are unqualified; replace the qualified bronze references.
    for flawed in (False, True):
        for statement in queries("genie_test", flawed=flawed):
            spark.sql(statement.replace("genie_test.bronze_", "bronze_"))
        actual = sorted([r.asDict() for r in spark.table("silver_out").select(*COLUMNS).collect()], key=lambda r: r["transaction_id"])
        expected, quarantine = reference(tables)
        assert (actual == expected) is (not flawed), "Spark equivalence mismatch"
        actual_q = sorted([r.asDict() for r in spark.table("quarantine_out").collect()], key=lambda r: r["transaction_id"])
        assert actual_q == quarantine
    print("Spark runtime contract: PASS (solution matches; START fails)")
finally:
    spark.stop()
