# Ruta opcional: contraste con SQL Server real

No requiere SQL Server para dictar el workshop. Los resultados expected son del
oracle de contrato Python. Esta ruta permite reemplazar una suposición por una
comparación observada del motor origen, usando exclusivamente los datos sintéticos.

1. Crea una base nueva y desechable en una instancia SQL Server 2017+ autorizada.
   No usar una base de clientes. Selecciónala explícitamente en SSMS/Azure Data Studio.
2. Ejecuta `schema/create_tables.sql`.
3. Desde la raíz del repo: `python3 -m scripts.export_sqlserver`.
4. Ejecuta `artifacts/load_synthetic.sql` en esa base. No reejecutar sin recrear
   el fixture: se duplicarían filas y claves.
5. Ejecuta `stored_procedures/sp_daily_customer_metrics.sql` y después:

```sql
EXEC dbo.sp_daily_customer_metrics @ReportDate = '2026-09-30';
```

6. Exporta solo ese resultado a CSV UTF-8 **con encabezados**; NULL como campo
   vacío, event_ts ISO 19 caracteres y amount_minor entero. No usar la salida
   tabulada/CSV con separadores de miles del cliente SQL.
7. Guarda como `artifacts/sqlserver_silver.csv` y compara:

```bash
python3 -m scripts.compare_source artifacts/sqlserver_silver.csv
```

Si diverge, inspecciona exportación, formatos y semántica; no modifiques expected
sin investigar. Para el refactor opcional ejecuta `solutions/lab01/refactored.sql`,
exporta el resultado de `_refactored` y aplica el mismo comparador.

Registra versión, configuración, procedimiento ejecutado y resultado antes de
decir “validado contra SQL Server”. Este repo no incluye una conexión productiva.
