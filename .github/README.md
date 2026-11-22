# `.github/`

**Estado actual:** vacío (Fase 1). No hay workflows reales todavía.

**Qué llegará en `.github/workflows/`:**
- **`etl.yml`** (Fase 3 — Automatización con GitHub Actions): ejecuta el
  script ETL de `etl/` con un cron semanal y hace commit automático de las
  capas resultantes en `data/processed/`.
- **`deploy.yml`** (Fase 5 — Despliegue, si no se usa la integración nativa de
  Cloudflare Pages/Vercel con GitHub): construye y despliega el sitio estático
  de `site/`.
