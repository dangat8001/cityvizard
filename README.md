# CityVizard — visor geoespacial de Bogotá

Plataforma de visualización y filtrado interactivo de información geoespacial
de interés para la ciudad, construida sobre un stack 100% gratuito.

## Estado del proyecto

🚧 **Fase 1 en curso** — fundamentos, documentación y estructura base. Todavía
no hay datos ni mapas funcionales; ver el [roadmap](#roadmap-de-fases) abajo.

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
   [Sitio estático en site/ — Astro o HTML/JS + MapLibre GL JS]
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
| 1 | Fundamentos y documentación | README, estructura de carpetas, placeholders, ganchos de configuración (esta fase) |
| 2 | ETL geoespacial en Python | `geopandas`/`requests`, `requirements.txt` real, primera capa funcional (ej. ciclorutas) |
| 3 | Automatización con GitHub Actions | Workflow `etl.yml` con cron periódico, commit automático de `data/processed/` |
| 4 | Frontend estático + MapLibre GL JS | Decisión Astro vs HTML/JS puro, visualización y filtros interactivos |
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
- En esta Fase 1 todavía no hay código ejecutable: las siguientes secciones se
  completarán a medida que avance el proyecto.

## Cómo ejecutar localmente

### Requisitos

_Pendiente — se completará en la Fase 2 (ETL) y Fase 4 (frontend)._

### Instalación

_Pendiente._

### Variables de entorno

Ver [`.env.example`](.env.example) para la lista de variables previstas (sin
valores reales todavía).

### Comandos

_Pendiente._

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
  [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/).
- Mapa base: [OpenStreetMap](https://www.openstreetmap.org/copyright) /
  [Carto](https://carto.com/attributions).

Cada fuente exige su propia atribución visible; esto se documentará en detalle
en [`data/README.md`](data/README.md) a medida que se integre cada capa.

## Licencia

El código de este repositorio se distribuye bajo licencia [MIT](LICENSE).
Esta licencia **no cubre** los datos geoespaciales de terceros (IDECA, Datos
Abiertos Bogotá, OpenStreetMap), cuyos propios términos de uso y atribución
deben respetarse y quedan documentados en `data/README.md`.

## Contacto

Daniel Gaitan Forero — danielgaitanforero@gmail.com
