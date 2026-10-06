# Guía de facilitación

## Antes de entrar

Ensaya SETUP completo. Mantén abierto el contrato, el procedimiento, el START,
el informe de reconciliación y la solución. Descarga el repo en tu equipo.
El taller dura 200 minutos; si dispones de tres horas exactas hay que acordar
una reducción de 20 minutos, no acelerar todos los labs silenciosamente.

No declares que Genie es infalible ni que siempre fallará. La respuesta viva es
variable; el defecto preparado y la evidencia sí son reproducibles.

## Apertura: una decisión real

Di: «Tenemos un pipeline que terminó correctamente. El código es legible.
Antes de aprobarlo, ¿qué necesitarían comprobar?»

Ejecuta E01. «El comercio es opcional. Cambiar el join elimina transacciones
válidas. La restricción era parte del problema, aunque el prompt no la mencionara.»

Separa lo observado de la narrativa ficticia: el incidente es ficticio, el
resultado del fixture sí se ejecuta. Nunca mostrar 10.284 vs 10.231 como si fueran
mediciones de este repo: los valores de este kit son **1.007 vs 834**.

## Lab 1: arqueología asistida

«Antes de pedir optimización, reconstruyamos lo que este procedimiento promete.»
Entrega el contrato y pide que clasifiquen hallazgos como confirmados, inferidos
o desconocidos. Si la IA interpreta el comentario “only settled” como regla,
señala el filtro real y pide contraste. No todos los comentarios son autoridad.

Pregunta por el desempate numérico, el LEFT JOIN, el intervalo abierto al final
y el manejo de CANCELLED. La solución no es quitar estas reglas para hacer menos código.
La versión refactorizada de `solutions/lab01/` sirve de referencia de revisión;
su equivalencia en SQL Server requiere ejecutar y exportar el origen opcional.

## Lab 2: el pipeline verde con resultado incorrecto

Corre bootstrap antes de comenzar. Ejecuta START y reconcile. «Correr sin errores
demuestra ejecución, no equivalencia. ¿Dónde desaparecieron los registros?»

Pide diagnóstico antes del cambio. Si detectan las tres fallas demasiado rápido,
lanza una Chaos Card sobre dimensión histórica o escala: deben distinguir un
nuevo requerimiento de un bug contra el contrato actual.

Después del arreglo, exige la comparación completa. «No editen expected_silver.
El contrato se revisa con negocio; no se ajusta para que el código gane.»

E04 local: mismo conteo y monto, cliente cambiado. «¿Un checksum de la suma habría
visto esto?» La canonización es necesaria para hashes entre motores. El notebook
compara filas y multiplicidad con `exceptAll`, no promete hashes mágicamente portables.

## E05: error concreto

Ejecuta únicamente la celda del CAST estricto de `schema_drift.py`; debe fallar.
Pide diagnóstico, formato de fuente y plan para cuarentena. Reemplazar todas las
comas sin contrato no es una corrección general. La siguiente celda acepta solo
el formato US acordado y deja otras entradas como NULL para ser tratadas.
No usar Run all si quieres detenerte para discusión en el error.

## E06: del notebook al PR

Lee `labs/lab03/lying_pr.md` antes de mostrar los tests. «¿Qué afirmaciones de esta
descripción están respaldadas por una ejecución?» Busca la condición CANCELLED
en el diff y contrasta con el contrato. Genera una descripción revisada con hechos:
comando, entorno, resultado, límite. No marcar casillas por cortesía.

Si un participante crea PR desde START, la CI del candidato falla hasta corregirlo.
La CI de main valida el kit y detecta intencionalmente el START; no certifica
una migración productiva. No necesitas publicar un PR falso para dictar la demo.

## Si falla la plataforma

Anuncia: «Continuamos con el mismo contrato y datos en el respaldo local.»
Ejecuta `scripts.run_lab` y revisa el JSON. Usa las soluciones preparadas si
la IA o el cómputo están limitados. No cambies permisos ni contrates servicios en vivo.

## Cierre

«La salida útil de hoy no es un notebook bonito: es un cambio con evidencia.»
Cada grupo explica una regla que casi perdió y cómo su verificación lo detecta.
Pide un límite de delegación que aplicarían mañana en su trabajo.

Rúbrica: 40 % equivalencia/evidencia, 25 % reglas y supuestos, 20 % diff acotado,
15 % revisión clara. La rapidez de prompting no es una métrica de aceptación.
