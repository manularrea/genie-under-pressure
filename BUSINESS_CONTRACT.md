# Contrato NovaBank v1

Este contrato define el comportamiento que debe conservarse. El oracle independiente
está en `src/reference.py`. Cambiarlo es cambiar el problema, no reparar la migración.

## Snapshot de entrada

Los CSV son un snapshot estático sintético de exportación. `updated_at` y `source_row`
son metadatos válidos de ordenamiento. El ejercicio no implementa streaming, CDC,
retención, SCD temporal ni consistencia entre tablas cambiantes.

1. Deduplicar por `transaction_id` **antes** de filtrar el día. Gana el mayor
   `updated_at`; empates se resuelven por `source_row` numérico mayor.
2. Para customers y merchants gana el mismo orden por su clave. La dimensión es
   la última del snapshot, no un join temporal a la fecha de la transacción.
3. Accounts tiene clave única y customer válido. Una transacción con account
   desconocido va a cuarentena; el fixture incluye un caso.
4. Los campos raw obligatorios son cadenas no nulas; `merchant_id=''` representa
   NULL. Los formatos nuevos requieren otro contrato de ingesta. No inferir tipos.

## Tiempo, estados y dinero

- Día del reporte: **2026-09-30**; intervalo **[2026-09-30 00:00:00, 2026-10-01 00:00:00)**.
- Timestamps locales de negocio ya expresados en **America/Bogota**, sin offset;
  formato `YYYY-MM-DDTHH:MM:SS`, calendario válido. Spark usa TIMESTAMP_NTZ.
  No convertirlos implícitamente a UTC ni cambiar el timezone para corregir conteos.
- `POSTED` y `CANCELLED` permanecen en el histórico Silver.
- Gold suma solo POSTED, y agrupa por **cliente, día y moneda**. No sumar COP y USD.
- Dinero: signo opcional `-`, de 1 a 16 dígitos enteros, exactamente dos decimales,
  punto decimal y sin separador de miles. Convertir a unidades menores enteras
  (`amount_minor`); `-12.34` se convierte en `-1234`. No usar FLOAT para el dinero.
- Reembolsos/importes negativos se conservan. No sustituir por valor absoluto.

## NULL, joins y cuarentena

Comercios nulos o desconocidos conservan la transacción y producen `merchant_name=NULL`.
El comercio es opcional: LEFT JOIN. Nunca usar una igualdad ordinaria entre valores
NULL para reconciliar; la ruta Spark usa `exceptAll` y conserva multiplicidad.

Fechas inválidas, importes inválidos, cuentas desconocidas, monedas o estados
fuera del contrato van a cuarentena tras deduplicar, **antes de filtrar el día**.
Cada registro tiene motivos; no convertir errores a cero ni descartarlos sin evidencia.
La cuarentena del fixture contiene tres registros.

## Aprobación

Todas las columnas y la multiplicidad deben coincidir con el snapshot esperado:
transaction_id, account_id, customer_id, merchant_id, merchant_name, segment,
event_ts, amount_minor, currency, status.

Conteos, claves, NULL, sumas por moneda y partición ayudan a diagnosticar; la
reconciliación completa decide. Los hashes son SHA-256 del JSON canónico definido
en `reference.py`; **no** SQL Server CHECKSUM, BINARY_CHECKSUM ni hashes nativos
comparables sin canonización. No son evidencia suficiente de consistencia en vivo.
