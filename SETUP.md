# Preparación de la sesión

## 1. Ensayo local (sin instalaciones de paquetes)

Requisitos: Python 3.10+ y Git. En Windows usa `python` si `python3` no existe.

```bash
git clone https://github.com/manularrea/genie-under-pressure.git
cd genie-under-pressure
python3 -m unittest discover -s tests -v
python3 -m scripts.demo prompt-trap
python3 -m scripts.demo silent-loss
python3 -m scripts.demo schema-drift
python3 -m scripts.demo lying-pr
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
```

El último comando falla deliberadamente (exit 1). Comprueba el PASS del respaldo:

```bash
python3 -m scripts.run_lab --candidate solutions/lab02/silver.sql
```

No ejecutes `generate_data` durante el lab para cambiar el resultado esperado.
Los CSV ya están incluidos. Solo la facilitadora regenera datos al cambiar el diseño.

## 2. Databricks antes del día del workshop

1. Accede a tu workspace autorizado. Confirma que puedes abrir un notebook Python,
   usar serverless y abrir **Genie Code**. No es un Genie de preguntas sobre dashboards.
2. En Catalog comprueba el catálogo existente al que tienes acceso. El notebook
   toma `current_catalog()` como valor inicial; no exige crear un catálogo nuevo.
3. Cada participante usa un schema personal, por ejemplo `genie_workshop_manu`.
   No compartan el mismo schema entre parejas que trabajen independientemente.
4. Descarga/clona este repo fuera de Databricks. Usa Workspace → Import (o el
   control de importación de tu versión), selecciona **File** e importa los `.py`
   como formato **Source**. Importarlos como archivos normales no los ejecuta
   como notebook: verifica que aparecen celdas separadas.
5. Importa estas piezas, manteniendo nombres:

| Orden | Archivo | Resultado |
|---|---|---|
| 1 | `databricks/00_setup/bootstrap.py` | Bronze y expected de contrato en Delta |
| 2 | `databricks/01_legacy/legacy_autopsy.py` | T-SQL como texto para dar contexto al asistente |
| 3 | `databricks/01_bronze/inspect.py` | Inspección de esquema y raw |
| 4 | `databricks/02_silver/silver_START.py` | Silver defectuoso y cuarentena |
| 5 | `databricks/03_validation/reconcile.py` | Falla del START: 834 vs 1.007 |
| 6 | `solutions/lab02/silver_SOLUTION.py` | Silver corregido |
| 7 | `databricks/04_gold/customer_daily.py` | Producto de datos tras PASS |
| Extra | `databricks/experiments/schema_drift.py` | Cast estricto que falla y normalización acotada |

6. Selecciona serverless. En **todos** los notebooks fija el mismo `catalog` y
   `schema`. Bootstrap escribe tablas con `mode(overwrite)` únicamente en ese schema:
   elige uno nuevo de práctica antes de ejecutarlo.
7. Ejecuta bootstrap una sola vez. Espera raw=20014, expected_silver=1007,
   quarantine=3. Recorre START → reconcile (falla) → SOLUTION → reconcile (PASS).
8. Ejecuta Gold al final. Si no hay PASS, no continúes.
9. Revisa la cuota/capacidades visibles y ensaya abrir Genie Code. La disponibilidad
   de agente, referencias o controles puede variar; chat sobre el notebook basta
   para el lab. Nunca cambies políticas de privacidad o seguridad para habilitar una demo.

Los notebooks incorporan el generador y la lógica necesaria: no requieren
`%pip`, DBFS, mounts, secretos, repos conectados, almacenamiento externo ni acceso
de red desde el cómputo. Git folders es opcional; la importación de archivos es la ruta base.

## 3. Dar contexto a Genie Code

Abre el notebook del lab y pega las reglas de `BUSINESS_CONTRACT.md` junto con el
prompt correspondiente. Adjunta/selecciona el contexto que permita tu interfaz.
Pide primero diagnóstico y supuestos, después cambios mínimos y evidencia de ejecución.
`.github/copilot-instructions.md` es para Copilot, no se carga automáticamente en Genie.
`@workspace` es una experiencia de Copilot en VS Code; no es un comando universal de Genie.

## 4. Copilot / Git opcionales

Si tienes VS Code y una licencia Copilot, abre el repo y usa chat/inline/agente
según los modos disponibles. Comparte esquema y contrato; revisa cada diff. Si
Copilot no está disponible, el mismo análisis puede hacerse en Genie y el commit
se hace con Git. Nunca introducir tokens en notebooks ni en el repo.

```bash
git switch workshop/start
git switch -c feature/reconcile-migration
# Corregir labs/lab02/silver.sql y el notebook candidato.
python3 -m scripts.run_lab --candidate labs/lab02/silver.sql
git add labs/lab02/silver.sql databricks/02_silver/silver_START.py
git commit -m "Preserve cancellation history and daily snapshot boundaries"
git push -u origin feature/reconcile-migration
```

Participantes sin acceso de escritura: fork en GitHub, clonar el fork y crear el
PR dentro del fork durante el workshop. No se necesitan invitaciones al repo original.
Un GitHub PR demuestra el mismo flujo básico que Azure Repos; no configuramos Azure DevOps.

## 5. Respaldo ante problemas

| Problema | Continuación |
|---|---|
| Cuota agotada / serverless no disponible | Ejecuta los labs locales y enseña el informe JSON |
| Genie no disponible | Usa la propuesta defectuosa preparada y los prompts como revisión manual |
| IA propone una solución correcta al primer intento | Verifica y compara con el START; no fuerces una equivocación de la IA |
| Cuenta sin permiso para crear schema | Usa tu schema personal autorizado; pide al dueño del workspace prepararlo |
| Importación muestra texto en vez de celdas | Reimporta como notebook Source |
| T-SQL falla en Spark | T-SQL es contexto de migración, no código que deba ejecutarse en Spark |

Free Edition está limitada a usos no comerciales; datos sintéticos no cambian esa
condición. Confirma la elegibilidad de la actividad con el responsable de la cuenta.
No prometemos cuotas ni disponibilidad para una clase completa. [Fuentes](docs/REFERENCES.md).
