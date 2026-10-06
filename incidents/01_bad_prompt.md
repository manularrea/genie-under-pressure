# INCIDENT E01 — Prompt Trap

**16:42.** Hay diez minutos para revisar una optimización. El comercio es opcional,
pero la propuesta usa INNER JOIN porque “simplifica el plan”.

```bash
python3 -m scripts.demo prompt-trap
```

Pregunta a Genie primero `Optimize this query`; luego usa `prompts/03_constrained.md`.
Compara propuestas contra el contrato. No se exige que la IA falle: el defecto
preparado permite mostrar exactamente qué regla se pierde.

Tu misión: conservar todas las transacciones válidas, justificar el join y
proponer una prueba para comercios NULL/desconocidos. No modificar expected.
