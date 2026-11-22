# `site/`

Frontend estático que renderiza los mapas interactivos.

**Estado actual (Fase 4 — Frontend estático + MapLibre GL JS):** visor
funcional con la primera capa (ciclorutas) y un filtro real por tipo de
superficie.

- **Generador de sitio:** [Astro](https://astro.build/) (`output: "static"`).
- **Mapa:** [MapLibre GL JS](https://maplibre.org/) sobre el basemap vectorial
  gratuito de [OpenFreeMap](https://openfreemap.org/) (estilo `liberty`, sin
  API key ni límites de uso). *Nota: el basemap raster de CARTO usado en el
  borrador inicial ahora exige API key, por eso se migró a OpenFreeMap.*
- **Datos:** `src/components/CityMap.astro` hace `fetch('/data/ciclorutas.geojson')`
  en el navegador. Ese archivo es una copia de `data/processed/ciclorutas.geojson`
  generada por `scripts/copy-data.mjs` (hook `predev`/`prebuild` de npm) — la
  fuente de verdad sigue siendo `data/processed/`, nunca se edita la copia.
- **Filtro:** `src/lib/filters.js` expone `uniqueSurfaceTypes` (deriva las
  categorías de `tipo_superficie` presentes en el GeoJSON) y
  `buildSurfaceFilter` (construye la expresión de filtro de MapLibre). El
  componente del mapa genera un checkbox por categoría y llama
  `map.setFilter(...)` al marcar/desmarcar.

## Ejecutar localmente

```bash
cd site
npm install
npm run dev       # http://localhost:4321, con recarga en caliente
npm run build     # genera dist/ (copia los datos primero)
npm run preview   # sirve dist/ localmente para probar el build de producción
```

## Tests

Política del proyecto: todo código (no solo `.py`) debe tener tests. La
lógica pura de filtrado vive en `src/lib/filters.js` y tiene su suite en
`src/lib/filters.test.js` (Vitest), con 100% de cobertura exigido vía
`vitest.config.mjs`. Los componentes `.astro` (markup + orquestación del mapa)
no se cubren con tests unitarios — se verifican manualmente en el navegador
(ver `npm run build && npm run preview`), igual que el `if __name__ == "__main__"`
del ETL se excluye de cobertura: no hay forma razonable de testear WebGL/mapas
sin herramientas de e2e mucho más pesadas que lo que amerita esta fase.

```bash
npm run test            # una vez
npm run test:coverage   # con reporte de cobertura (100% requerido)
```

## Nota técnica: maplibre-gl + Vite

`maplibre-gl` (v6+) carga su web worker con una ruta que Vite no emite por
defecto, causando `Worker failed to load` en producción. Se resuelve
importando el worker con el sufijo `?url` y registrándolo con `setWorkerUrl()`
antes de crear el mapa — ver el principio de `src/components/CityMap.astro`.

## Despliegue (Fase 5 — Cloudflare) ✅

**En vivo:** https://cityvizard.danielgaitanforero.workers.dev

Cloudflare unificó "Pages" dentro de la plataforma "Workers": un sitio
estático se despliega como un Worker *assets-only* (sin código de servidor),
configurado por `wrangler.jsonc`:

```jsonc
{
  "name": "cityvizard",
  "compatibility_date": "2026-11-22",
  "assets": { "directory": "./dist" }
}
```

No requiere el adapter `@astrojs/cloudflare` (ese es solo para renderizado en
servidor/on-demand; este sitio es 100% estático).

**Conectado vía GitHub (Cloudflare dashboard → Workers & Pages → Connect GitHub):**
- Root directory: `site`
- Build command: `npm run build`
- Deploy command: `npx wrangler deploy` (default, no tocar)
- Variable de entorno `NODE_VERSION=20`

> ⚠️ Si el build falla con `npm error enoent ... /opt/buildhome/repo/package.json`,
> el campo **Root directory** no quedó en `site`. En un proyecto ya creado se
> corrige en **Settings → Build** (no en el asistente inicial), guardando y
> reintentando el deployment.

**Manual desde la terminal:**

```bash
cd site
npm run build
npx wrangler deploy          # sube dist/ con la config de wrangler.jsonc
npx wrangler deploy --dry-run  # valida sin subir nada
```

Se eligió Cloudflare sobre Vercel porque el plan gratuito de Vercel (Hobby)
prohíbe explícitamente uso comercial en sus Términos de Servicio, lo cual
entra en conflicto con el objetivo de monetización (Fase 6) del proyecto;
Cloudflare no tiene esa restricción y da ancho de banda ilimitado gratis.

## `public/`

Carpeta de archivos estáticos servidos tal cual, sin procesar por el build.

- **`robots.txt`** — placeholder mínimo y seguro. Se completará con reglas
  reales y referencia a `sitemap.xml` en la Fase 6 (SEO y monetización).
- **`ads.txt`** — placeholder comentado, sin `pub-id` real. Se activará en la
  Fase 6 una vez exista una cuenta de Google AdSense aprobada.
- **`data/`** — generada automáticamente (ver arriba), no se versiona.

`index.astro` ya incluye `<title>`, `<meta name="description">` y
`og:title`/`og:description`/`og:type` básicos. `sitemap.xml` y meta tags más
avanzados quedan pendientes de la Fase 6.
