# Contribuir / trabajar en el workshop

Crea tu rama o fork desde `workshop/start`. Identifica el incidente, adjunta
reconciliación, revisa el diff generado y usa el template de PR.
El gate de un PR ejecuta el candidato del lab, además de validar el kit.

No agregar credenciales, datos reales ni código de clientes. No cambiar expected,
oracle o tests para ocultar errores. Un nuevo contrato se discute como cambio
separado con fixtures y evidencia actualizados.

Para regenerar notebooks fuente: `python3 -m scripts.build_notebooks`.
Para validar: `python3 -m unittest discover -s tests -v`.
Los notebooks son autocontenidos; sus archivos generados se versionan para poder
importarlos sin depender de una conexión Git desde Databricks.
