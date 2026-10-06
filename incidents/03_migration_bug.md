# INCIDENT E03 — Semantic Migration

**05:12.** El job migrado terminó correctamente. El reporte sale a las 06:00.

| Snapshot diario | Filas |
|---|---:|
| Contrato esperado | 1.007 |
| Candidato migrado | 834 |

Estas cifras se reproducen con los fixtures del repo; no son una medición de SQL Server.
Ejecuta `python3 -m scripts.run_lab --candidate labs/lab02/silver.sql` o START + reconcile.

Tu misión: localizar claves faltantes/sobrantes, explicar el origen, reparar con
un diff mínimo y volver a reconciliar. No dar por correcto el origen por autoridad:
el contrato y su ejecución deben contrastarse cuando haya un SQL Server disponible.
