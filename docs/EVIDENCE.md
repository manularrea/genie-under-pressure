# Qué prueba este kit

La suite local comprueba: equivalencia completa de la solución SQLite con el
oracle Python; salidas versionadas; detección del candidato defectuoso; intervalo
temporal; dedup con empate; importes firmados; dimensiones; cuarentena; y el caso
de conteos/sumas iguales con identidad corrupta.

Durante la construcción se ejecutaron **8 pruebas locales (PASS)** y el SQL
de los notebooks en **Spark 3.5.3 / Java 17**, con fixture de 500 filas (PASS:
solución equivalente, START divergente y cuarentena equivalente).
La solución local completa también reconcilió las 1.007 filas del día.

Los resultados proceden de ejecuciones locales. El notebook de reconciliación
permite comprobar Spark/Delta **en el workspace del participante**. No se afirma
que un workspace Databricks o un motor SQL Server se hayan ejecutado por crear el repo.

## Spark opcional fuera de Databricks

Con Python compatible con PySpark 3.5, Java 17 y acceso a PyPI:

```bash
python3 -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-spark.txt
python -m scripts.check_spark
```

Este test ejecuta el SQL real de los notebooks, con fixture de 500 filas, y compara
la solución, el defecto sembrado y la cuarentena. No valida Delta, Unity Catalog,
serverless o permisos: esos se ensayan en Databricks. No es una dependencia de la clase.

## Performance

20.000 filas no permiten afirmar mejoras en producción. `collect()` es aceptable
en una prueba pequeña acotada como esta, pero no un patrón para materializar 4 TB
en el driver. Cuenta el volumen, revisa plan/joins/shuffle y mide con condiciones
equivalentes antes de prometer rapidez. Varios `withColumn` no implican por sí
solos un problema; Catalyst puede optimizarlos. Las UDF tampoco son siempre incorrectas.

## Hashes

Métricas y hashes por moneda son diagnósticos del fixture. La comparación real
de contenido se hace además por filas completas. Misma suma, mismo conteo o mismo
checksum numérico no prueban identidad. No comparar hashes de motores diferentes
sin definir normalización de NULL, timestamps, tipos, orden y duplicados.
