# Agenda: 3 h 20 min

Conserva los bloques y las duraciones del temario aprobado.

| Inicio | Bloque | Min | Experiencia y entregable |
|---|---|---:|---|
| 00:00 | 0. Apertura | 15 | Encuesta, contrato de uso, E01 de 5 min |
| 00:15 | 1. Fundamentos para ingenieros | 25 | Contexto, restricciones, límites y verificación; prompt malo vs verificable |
| 00:40 | 2. Ecosistema Genie Code / VS Code + Copilot | 60 | Setup, modos disponibles, contexto; Lab 1 autopsia y refactor T-SQL |
| 01:40 | Pausa | 10 | Preparar el snapshot del Lab 2 |
| 01:50 | 3. SQL → Databricks | 50 | Medallón, Delta y producto de datos; Lab 2 migración y reconciliación |
| 02:40 | 4. DevOps mínimo viable | 25 | Branch, commit, PR, review; E06 gate de evidencia |
| 03:05 | 5. Cierre | 15 | Riesgos, buenas prácticas, preguntas y recursos |
| 03:20 | Fin | | |

## Bloque 0 — Reglas del War Room

Solo datos sintéticos; no credenciales ni código propietario. La IA puede
proponer y modificar; el equipo responde por la aceptación. Encuesta de manos:
¿quién usa Copilot?, ¿quién ha usado Genie Code?, ¿quién revisa la salida con tests?
Abre E01 y ejecuta `python3 -m scripts.demo prompt-trap`.

## Bloque 1 — Modelo mental útil

Un LLM produce propuestas condicionadas por el contexto; una respuesta convincente
no certifica equivalencia. El asistente puede usar herramientas, y ejecutarlas
produce observaciones que también deben interpretarse. Temperatura, contexto y
herramientas no sustituyen una especificación. Comparar `01_naive` con `04_verifiable`.

Delegar: explicación, documentación, tests propuestos y refactor acotado.
Revisar personalmente: reglas de negocio, supuestos, permisos, resultados y decisiones
de despliegue. No dedicar el bloque a una exposición extensa de transformers.

## Bloque 2 — Lab 1

15 min de modos/contexto; 10 min de lectura; 15 min de autopsia; 15 min de refactor;
5 min de puesta en común. Ver `labs/lab01/README.md`. Los grupos entregan un mapa
de etapas, reglas, riesgos y una propuesta justificada. No ejecutar T-SQL en Spark.

## Bloque 3 — Lab 2

5 min medallón/Delta; 5 min Bronze; 10 min generación/migración; 10 min primer diff;
15 min reparación y evidencia; 5 min Gold/retro. `reconcile.py` es el punto central.
E04 demuestra por qué conteos y sumas no bastan. E05 es extra si sobra tiempo;
si no, sustituye 5 minutos de discusión por el error de cast preparado.

## Bloque 4 — Production Gate

5 min mapa Git y Gitflow; 5 min diff/commit; 10 min revisión del PR mentiroso;
5 min corregir descripción con resultados observados. GitHub y Azure DevOps
se comparan como plataformas; el ejercicio práctico usa GitHub. CI verde no
implica rendimiento, seguridad ni equivalencia en un origen productivo.

## Bloque 5 — Cierre

Recapitular en 5 min; 8 min Q&A; 2 min recursos. Escalera de delegación:
explica → propone → modifica → ejecuta → valida → despliega. ¿Qué evidencia y
qué controles exigiría el equipo para subir cada nivel? No hay despliegue en este lab.
