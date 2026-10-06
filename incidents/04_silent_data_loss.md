# INCIDENT E04 — Silent Data Loss

**11:20.** Conteos y montos por moneda coinciden. Una transacción pertenece a otro
cliente. El control de totales marca verde.

```bash
python3 -m scripts.demo silent-loss
```

Resultado: mismo conteo=true, mismos montos=true, mismo contenido=false.
Este experimento cambia deliberadamente una clave de cliente en memoria.

Tu misión: explicar qué control falta, definir canonización para hashes y
comparar filas completas con multiplicidad. No basta un checksum de montos.
