# `etl/`

Capa de extracción, limpieza y simplificación de datos geoespaciales.

**Estado actual:** esqueleto vacío (Fase 1). Sin código funcional todavía.

**Qué llegará aquí (Fase 2 — ETL geoespacial en Python):**
- Scripts en `src/` escritos en Python usando `geopandas` y `requests` para
  descargar capas desde las APIs de [IDECA](https://www.ideca.gov.co/) y
  [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/), limpiarlas y
  simplificar sus geometrías.
- Archivos de configuración en `config/` (por ejemplo, un YAML con las URLs y
  metadatos de cada fuente de datos a consumir).
- Un `requirements.txt` real con las dependencias del ETL.
- La primera capa funcional candidata: ciclorutas de Bogotá.

**Qué llegará después (Fase 3 — Automatización):**
- Estos scripts serán invocados periódicamente (cron semanal) por un workflow
  de GitHub Actions definido en `.github/workflows/etl.yml`, que ejecutará el
  ETL y hará commit automático de los resultados en `data/processed/`.
