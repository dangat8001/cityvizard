# `.github/`

**Estado actual (Fase 3 — Automatización con GitHub Actions):** dos workflows activos en `workflows/`.

- **`ci.yml`** — gate de calidad: corre `pytest --cov=src` (100% de cobertura
  requerido, ver [`etl/README.md`](../etl/README.md#tests-y-cobertura)) en
  cada PR o push a `main` que toque `etl/**`.
- **`etl.yml`** — automatización de datos: cron semanal (lunes 06:00 UTC) +
  disparo manual (`workflow_dispatch`). Corre los mismos tests como gate,
  ejecuta `etl/src/fetch_ciclorutas.py` y, si el resultado cambió, commitea
  y pushea `data/processed/` automáticamente a `main` como
  `github-actions[bot]`.

**Qué llegará después (Fase 5 — Despliegue):**
- **`deploy.yml`**, si no se usa la integración nativa de Cloudflare
  Pages/Vercel con GitHub, para construir y desplegar el sitio estático de
  `site/`.
