# CityVizard — visor geoespacial de Bogotá

Plataforma de visualización y filtrado interactivo de información geoespacial
de interés para la ciudad, construida sobre un stack 100% gratuito.

## Estado del proyecto

🚧 **Fase 4 en curso** — primer mapa interactivo: ciclorutas de Bogotá
filtrables por tipo de superficie. Ver el [roadmap](#roadmap-de-fases) abajo.

## ¿Qué es CityVizard?

CityVizard busca facilitar la exploración de capas geoespaciales de interés
público superpuestas sobre un mapa interactivo: salud, población, sitios de
interés, restaurantes, ciclorutas y más. La idea es que cualquier persona
pueda filtrar y visualizar esta información de forma rápida, sin fricción y
sin depender de herramientas de pago.

## Alcance inicial (MVP)

- **Cobertura geográfica:** únicamente Bogotá D.C. en esta primera etapa.
- **Capas candidatas:** ciclorutas, sitios de interés, restaurantes, salud,
  población (sujeto a disponibilidad y calidad de las fuentes abiertas).
- **Fuentes de datos previstas:**
  - [IDECA — Infraestructura de Datos Espaciales para el Distrito Capital](https://www.ideca.gov.co/)
  - [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/)

## Arquitectura

El proyecto se apoya en tres capas, todas con costo prácticamente nulo:

```
[IDECA / Datos Abiertos Bogotá APIs]
         │  (Python: requests + geopandas)
         ▼
   [ETL en etl/]
         │  (GitHub Actions, cron periódico)
         ▼
   [GeoJSON/PMTiles en data/processed/]
         │
         ▼
   [Sitio estático en site/ — Astro + MapLibre GL JS]
         │  (build)
         ▼
   [Cloudflare Pages / Vercel — CDN]
         │  (dominio propio)
         ▼
      Usuario final
```

No hay servidores activos 24/7 ni bases de datos espaciales en la nube: el
procesamiento pesado (extracción, limpieza, simplificación) ocurre una sola
vez y de forma periódica mediante tareas programadas; el filtrado y el
renderizado del mapa se ejecutan directamente en el navegador del usuario
final, usando archivos estáticos distribuidos por una CDN gratuita.

## Estructura del repositorio

```
cityvizard/
├── etl/                  → extracción, limpieza y simplificación (Python)
├── data/                 → capas geoespaciales (raw/ y processed/)
├── site/                 → frontend estático + MapLibre GL JS
├── .github/workflows/    → automatización (GitHub Actions)
└── docs/                 → documentación extendida (ADRs, diccionario de datos)
```

Cada carpeta tiene su propio `README.md` con el detalle de qué contiene y en
qué fase se completa: [`etl/`](etl/README.md), [`data/`](data/README.md),
[`site/`](site/README.md), [`.github/`](.github/README.md),
[`docs/`](docs/README.md).

## Roadmap de fases

| Fase | Nombre | Contenido |
|---|---|---|
| 1 ✅ | Fundamentos y documentación | README, estructura de carpetas, placeholders, ganchos de configuración |
| 2 ✅ | ETL geoespacial en Python | `geopandas`/`requests`, `requirements.txt` real, primera capa funcional (ciclorutas), tests con 100% de cobertura |
| 3 ✅ | Automatización con GitHub Actions | `ci.yml` (gate de tests) + `etl.yml` con cron semanal y commit automático de `data/processed/` |
| 4 🚧 | Frontend estático + MapLibre GL JS | Astro + MapLibre sobre OpenFreeMap, ciclorutas filtrables por tipo de superficie — esta fase |
| 5 | Despliegue y dominio propio | Cloudflare Pages/Vercel, dominio personalizado, HTTPS |
| 6 | SEO y monetización | `robots.txt`/`sitemap.xml` reales, meta tags/Open Graph, Google Analytics, Google AdSense |
| 7 | Expansión | Nuevas ciudades, nuevas capas, UX avanzada (búsqueda, favoritos, export) |

Esta numeración es una propuesta editable: las fases pueden fusionarse o
reordenarse a medida que avanza el proyecto.

## Cómo contribuir

- Usa commits descriptivos y, cuando aplique, referencia la fase del roadmap
  a la que corresponde el cambio.
- Para proponer una nueva capa de datos, abre un issue indicando la fuente
  oficial y su licencia/términos de uso.
- **Todo archivo `.py` del proyecto debe tener tests** que lo acompañen, con
  el objetivo de mantener 100% de cobertura (ver [`etl/README.md`](etl/README.md#tests-y-cobertura)
  para el ejemplo de referencia). Esta regla aplica a cualquier módulo Python
  futuro, no solo al ETL.

## Cómo ejecutar localmente

### Requisitos

- Python 3.11+ (ETL).
- Node.js 20+ (sitio/frontend).

### Instalación

```bash
# ETL
python3 -m venv .venv && source .venv/bin/activate
pip install -r etl/requirements.txt -r etl/requirements-dev.txt

# Sitio
cd site && npm install
```

### Variables de entorno

Ver [`.env.example`](.env.example) para la lista de variables previstas (sin
valores reales todavía). El ETL actual no requiere ninguna.

### Comandos

```bash
python3 etl/src/fetch_ciclorutas.py   # genera data/processed/ciclorutas.geojson
cd etl && python -m pytest --cov=src --cov-report=term-missing   # tests + cobertura del ETL

cd site && npm run dev     # visor en http://localhost:4321
cd site && npm run build   # build de producción en site/dist/
cd site && npm run test:coverage   # tests + cobertura del frontend
```

El resto de comandos (build/preview del frontend) se documentarán en la Fase 4.

## Monetización y SEO (roadmap)

El proyecto está pensado desde el inicio para poder monetizarse con
[Google AdSense](https://adsense.google.com/) y seguir buenas prácticas de
SEO, aunque **nada de esto está activo todavía**. Ganchos ya dejados en esta
fase, listos para activarse más adelante:

- [`site/public/robots.txt`](site/public/robots.txt) — reglas mínimas de
  indexación.
- [`site/public/ads.txt`](site/public/ads.txt) — placeholder sin `pub-id` real.
- [`.env.example`](.env.example) — nombres de variables `PUBLIC_GA_MEASUREMENT_ID`
  y `PUBLIC_ADSENSE_CLIENT_ID`, sin valores.

La activación real (cuenta de AdSense aprobada, `sitemap.xml`, meta tags/Open
Graph) llega en la Fase 6.

## Fuentes de datos y créditos

- Datos geoespaciales: [IDECA](https://www.ideca.gov.co/) y
  [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/) (ciclorutas:
  IDU, CC BY 4.0).
- Mapa base: [OpenFreeMap](https://openfreemap.org/) (estilo `liberty`,
  datos de [OpenStreetMap](https://www.openstreetmap.org/copyright) vía
  [OpenMapTiles](https://www.openmaptiles.org/)) — gratuito, sin API key.

Cada fuente exige su propia atribución visible; esto se documentará en detalle
en [`data/README.md`](data/README.md) a medida que se integre cada capa.

## Licencia

El código de este repositorio se distribuye bajo licencia [MIT](LICENSE).
Esta licencia **no cubre** los datos geoespaciales de terceros (IDECA, Datos
Abiertos Bogotá, OpenStreetMap), cuyos propios términos de uso y atribución
deben respetarse y quedan documentados en `data/README.md`.

## Contacto

Daniel Gaitan Forero — danielgaitanforero@gmail.com
