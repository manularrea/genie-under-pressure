# Datos 100 % sintéticos

Generador determinista: `src/fixtures.py`. Sin Faker, APIs, descargas ni información
de clientes. 20.000 transacciones base y 14 casos/actualizaciones adicionales.

- `raw/`: snapshot completo de cuatro tablas; tipos explícitos de cadena.
- `corrupted/`: fixtures pequeños específicos, no un segundo día completo.
- `expected/`: Silver, cuarentena y métricas del oracle Python independiente.

Esperado del día 2026-09-30: 1.007 filas, 145 anuladas, 34 comercios sin nombre,
3 registros en cuarentena. La serie es deliberadamente pequeña y estructurada;
no representa una distribución bancaria real ni sirve para benchmarks comerciales.

Facilitadora, solo para rediseñar fixtures:

```bash
python3 -m scripts.generate_data
python3 -m scripts.build_notebooks
python3 -m unittest discover -s tests -v
```

Participantes: no regeneren expected para hacer pasar el lab.
