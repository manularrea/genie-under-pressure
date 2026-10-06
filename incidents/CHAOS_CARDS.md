# Chaos Cards — decisiones adicionales

La facilitadora entrega **una** durante el lab. Cada card introduce información
nueva: no autoriza cambiar el contrato sin discutir el impacto.

| Card | Nuevo hecho | Pregunta |
|---|---|---|
| Dimensión duplicada | customer_id no es único en raw | ¿Cómo eliges una versión sin multiplicar filas? |
| Historia temporal | Negocio quiere el segmento vigente en event_ts | ¿Es un bug del contrato v1 o un nuevo requerimiento SCD? |
| Anulaciones | Finanzas requiere CANCELLED en histórico | ¿Dónde se filtran para métricas, sin perder historia? |
| Escala | El pipeline real procesa 4 TB | ¿Qué parte materializa datos en driver y qué debes medir? |
| Formato mixto | Una fuente manda 1.245,50; otra 1,245.50 | ¿Qué contrato de fuente permite parsear sin ambigüedad? |
| Snapshot cambiante | La fuente cambia durante el export | ¿Cómo garantizas un corte consistente antes de reconciliar? |
| IA segura de sí misma | Propone una API no comprobada | ¿Qué documentación y prueba mínima necesitas? |

No implementes soluciones de producción al azar. Registra supuesto, impacto,
responsable de decisión y validación adicional requerida.
