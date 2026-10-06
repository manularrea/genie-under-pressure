# Lab 3 — Production Gate

Lee `lying_pr.md`. Solicita a la IA una revisión del diff contra el contrato,
después contrasta sus hallazgos con las ejecuciones. Corrige la descripción con
solo resultados observados. Si no ejecutaste algo, dilo.

Desde `workshop/start`, crea `feature/reconcile-migration`. Modifica el candidato,
ejecuta `scripts.run_lab`, revisa el diff y haz commit. Abre PR en tu fork o en el
repo si tienes permisos. La CI de PR reconcilia el candidato.

Mapa Gitflow: main → desarrollo → feature; release y hotfix solo como conceptos.
Este repo usa main y ramas de ejercicio para reducir setup. GitHub y Azure Repos
comparten commits/branches/PR; identidades, permisos y pipelines se configuran aparte.

No hay merge ni deploy automáticos. La aprobación requiere revisión humana además
de CI; no se creó una política de protección o permisos en tu cuenta.
