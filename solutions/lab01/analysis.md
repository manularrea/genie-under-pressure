# Autopsia resuelta

Etapas: rango diario → última transacción → últimas dimensiones → validación
de entrada → joins → snapshot Silver. El orden importa: primero dedup, luego día.

Reglas comprobadas por lectura: historial incluye anuladas; comercio opcional;
cuenta obligatoria; último snapshot dimensional; fecha final excluida; dinero con signo.

Comentario obsoleto: “only settled” contradice el filtro real. `@UnusedMode` no
afecta salida. Tablas temporales hacen visible el legado pero no son requisito
del comportamiento. Reemplazarlas por CTE no demuestra una mejora de rendimiento.

Riesgos: DECIMAL vs FLOAT; NULL vs cadena vacía; pérdida por INNER JOIN;
fan-out dimensional; parseo de fecha; cambio de zona; desempate lexicográfico;
WHERE de una tabla derecha que transforma un LEFT JOIN en filtro obligatorio.

`refactored.sql` conserva comportamiento para este fixture. T-SQL acepta más
formatos numéricos que el contrato raw estricto; el productor debe validarlo antes
de este procedimiento. Un contrato nuevo necesita nuevas pruebas y cuarentena.
Sin ejecutar SQL Server no afirmar equivalencia observada o mejora de desempeño.
