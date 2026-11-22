# `site/`

Frontend estático que renderiza los mapas interactivos.

**Estado actual:** visor funcional con dos capas — ciclorutas (filtro por
tipo de superficie) y población por UPZ en 3D.

- **Generador de sitio:** [Astro](https://astro.build/) (`output: "static"`).
- **Mapa:** [MapLibre GL JS](https://maplibre.org/) sobre el basemap vectorial
  gratuito de [OpenFreeMap](https://openfreemap.org/), estilo **`positron`**
  (sin API key ni límites de uso). Se eligió `positron` sobre `liberty` porque
  es minimalista en gris/beige — sin azules de agua ni verdes de parques que
  compitan visualmente con nuestras propias capas de datos. *Nota: el basemap
  raster de CARTO usado en el borrador inicial ahora exige API key, por eso se
  migró a OpenFreeMap.*
- **Datos:** `src/components/CityMap.astro` hace `fetch('/data/ciclorutas.geojson')`
  en el navegador. Ese archivo es una copia de `data/processed/ciclorutas.geojson`
  generada por `scripts/copy-data.mjs` (hook `predev`/`prebuild` de npm) — la
  fuente de verdad sigue siendo `data/processed/`, nunca se edita la copia.
  Se renderiza con dos capas sobre la misma fuente: un `fill` naranja
  translúcido y un `line` del mismo color con ancho fijo en píxeles (crece un
  poco con el zoom) — sin la capa de línea, los polígonos reales (delgados)
  casi no se distinguen a escala de ciudad.
- **Filtro:** `src/lib/filters.js` expone `uniqueSurfaceTypes` (deriva las
  categorías de `tipo_superficie` presentes en el GeoJSON) y
  `buildSurfaceFilter` (construye la expresión de filtro de MapLibre). El
  componente del mapa genera un checkbox por categoría y llama
  `map.setFilter(...)` sobre las dos capas (`ciclorutas-fill` y
  `ciclorutas-line`) al marcar/desmarcar.
- **Población 3D:** `fetch('/data/poblacion_upz.geojson')` + una capa
  `fill-extrusion` (`poblacion-upz-3d`), oculta por defecto detrás de un
  checkbox "Mostrar en el mapa (3D)". `src/lib/population.js` construye las
  expresiones de MapLibre: altura = `poblacion_total` (interpolada
  linealmente a 0-4000 m según el rango real de los datos) y color =
  `densidad_hab_ha` (ámbar claro → rojo oscuro). Todas las funciones son
  puras y tienen su suite en `population.test.js`.
- **Inclinación 3D libre:** un slider ("Inclinación 3D") deja al usuario
  elegir el ángulo (0-60°, el `maxPitch` por defecto de MapLibre) en
  cualquier momento — no queda fijo. Al activar el checkbox de población se
  sugiere 45° *solo si el mapa sigue plano* (pitch 0), sin forzarlo si el
  usuario ya lo ajustó. El mapa también se puede rotar/inclinar arrastrando
  con clic derecho o Ctrl+clic (gesto nativo de MapLibre); un listener del
  evento `map.on("pitch", ...)` mantiene el slider sincronizado sin importar
  el método usado. `NavigationControl` se configura con `visualizePitch: true`
  para que el ícono de la brújula refleje la inclinación actual.
- **Layout:** `#map` (65%) + un panel lateral `.panel` (35%, scrollable) con
  los controles — ya no hay una leyenda flotante encima del mapa.
- **Tabla de UPZ:** el panel incluye una tabla ordenada por población
  descendente, con la celda de densidad coloreada con la misma escala que la
  capa 3D (`interpolateDensityColor`, misma función usada para construir la
  expresión de MapLibre, ambas comparten los mismos colores/rango — ver
  `src/lib/population.js`). Un `<select>` "Top N" (10/25/50/Todas) filtra a
  la vez la tabla y el filtro de la capa 3D (`buildUpzFilter`), y hacer clic
  en una fila centra el mapa en esa UPZ (`roughCentroid`, en
  `src/lib/geo.js`, un centroide aproximado por promedio de vértices — no
  geométricamente exacto, pero suficiente para un `flyTo`) y resalta su
  contorno con una capa de línea auxiliar (`poblacion-upz-highlight`).

## Ejecutar localmente

```bash
cd site
npm install
npm run dev       # http://localhost:4321, con recarga en caliente
npm run build     # genera dist/ (copia los datos primero)
npm run preview   # sirve dist/ localmente para probar el build de producción
```

## Tests

Política del proyecto: todo código (no solo `.py`) debe tener tests. Toda la
lógica pura (filtros de ciclorutas, expresiones/colores de población,
centroide) vive en `src/lib/*.js` con su suite correspondiente en Vitest
(`src/lib/*.test.js`), con 100% de cobertura exigido vía `vitest.config.mjs`.
Los componentes `.astro` (markup + orquestación del mapa)
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
