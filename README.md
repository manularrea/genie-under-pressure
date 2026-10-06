# Genie Under Pressure

### AI writes. Engineers verify.

Un workshop práctico de ingeniería de datos asistida por **Databricks Genie Code**:
arqueología de T-SQL, migración a Spark SQL, Delta, reconciliación y revisión de PR.
Todo ocurre en **NovaBank**, un banco ficticio con datos íntegramente sintéticos.

El pipeline termina sin errores. El reporte cambia. **¿Lo aprobarías?**

| Ruta | Necesitas | Lo que ejecutas |
|---|---|---|
| Databricks | Workspace compatible, notebooks serverless y acceso a Genie Code | Bronze → Silver → validación → Gold en Delta |
| Respaldo local | Python 3.10+ y Git | SQLite, oracle independiente y fallos reproducibles; sin paquetes adicionales |
| Origen real opcional | SQL Server 2017+ en una base desechable | Procedimiento T-SQL y comparación de su exportación |

**No necesitas SQL Server ni Copilot para la ruta principal.** Genie Code es el asistente
de desarrollo de Databricks; las experiencias conversacionales de negocio de Genie
no son el objeto de estos labs.

## Primer ensayo: 3 comandos

```bash
git clone https://github.com/manularrea/genie-under-pressure.git
cd genie-under-pressure
python3 -m unittest discover -s tests -v
```

Ahora reproduce la migración defectuosa:

```bash
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
```

**Este comando debe terminar con código 1.** El fixture tiene 20.014 filas raw;
el snapshot correcto tiene **1.007 filas** y el candidato inicial entrega **834**.
Hay **3 registros en cuarentena**. El informe se guarda en `artifacts/reconciliation.json`.

Comprueba la solución:

```bash
python3 -m scripts.run_lab --candidate solutions/lab02/silver.sql
```

Debe terminar con código 0, sin claves faltantes, sobrantes ni modificadas.
Los resultados esperados vienen de un **oracle Python del contrato de negocio**,
no de una ejecución de SQL Server inventada. [Cómo contrastar el origen](legacy/README.md).

## Los seis experimentos

| # | Incidente | Evidencia |
|---|---|---|
| E01 | [Prompt Trap](incidents/01_bad_prompt.md) | Un INNER JOIN elimina transacciones válidas |
| E02 | [Legacy Autopsy](incidents/02_legacy_sql.md) | Reglas escondidas en un stored procedure |
| E03 | [Semantic Migration](incidents/03_migration_bug.md) | 1.007 esperadas frente a 834 del candidato |
| E04 | [Silent Data Loss](incidents/04_silent_data_loss.md) | Conteos y sumas iguales con clientes incorrectos |
| E05 | [Schema Drift](incidents/05_schema_drift.md) | Un importe con separadores rompe el parser |
| E06 | [Lying PR](incidents/06_bad_pull_request.md) | Descripción convincente; evidencia insuficiente |

Los defectos sembrados son deterministas. **No asumimos que Genie siempre se equivoca**:
si genera una respuesta correcta en vivo, ejecuta el candidato defectuoso preparado
y compara ambas propuestas. [Prompts progresivos](prompts/README.md).

## Dictar el workshop

- [SETUP.md](SETUP.md): preparación local y Databricks, sin credenciales en Git.
- [WORKSHOP.md](WORKSHOP.md): agenda aprobada de **200 minutos**, incluida la pausa.
- [FACILITATOR_GUIDE.md](FACILITATOR_GUIDE.md): tiempos, diálogos, decisiones y respaldo.
- [BUSINESS_CONTRACT.md](BUSINESS_CONTRACT.md): especificación que no se negocia para pasar tests.
- [labs/README.md](labs/README.md): entregables y criterios de aprobación.
- [solutions/README.md](solutions/README.md): spoilers y solución.
- [docs/EVIDENCE.md](docs/EVIDENCE.md): alcance de las verificaciones y límites de las métricas.

**Databricks**: importa los notebooks `.py` como *source notebooks*, empezando por
`databricks/00_setup/bootstrap.py`; continúa con `silver_START.py` y `reconcile.py`.
Son autocontenidos: no hacen peticiones a GitHub ni instalan librerías en el workspace.

## Ramas y revisión

`main` contiene todo el kit; `workshop/start` deja el candidato inicial;
`workshop/solution` tiene la solución aplicada a `labs/lab02/silver.sql`.
Para trabajar, crea una rama propia desde `workshop/start` y envía un PR a `main`.

La CI de `main` comprueba los fixtures y la solución, y prueba que el defecto
sembrado sigue siendo detectable. **En un PR también reconcilia el candidato del lab**;
un PR con el START sin corregir debe fallar. Un badge verde en `main` no aprueba
el candidato defectuoso. No hay merge ni despliegue automáticos.

## Alcance de Free Edition

El kit usa datasets pequeños, tablas Delta y notebooks serverless. Free Edition
tiene límites de uso y restricciones de red; prepara el respaldo local.
Su documentación establece uso no comercial: **los datos sintéticos no eliminan
esa restricción**. Confirma que el uso de tu sesión está permitido; una capacitación
comercial puede requerir otro workspace o acuerdo. [Fuentes oficiales](docs/REFERENCES.md).

No hay datos de clientes, claves, endpoints de producción ni dependencias con servicios
externos. Las respuestas de IA y las opciones de interfaz pueden variar según cuenta y versión.
