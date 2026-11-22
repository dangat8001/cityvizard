# `site/`

Frontend estático que renderiza los mapas interactivos.

**Estado actual:** esqueleto vacío (Fase 1). Sin código funcional todavía.

**Decisión pendiente (Fase 4 — Frontend estático + MapLibre GL JS):**
- Elegir entre un generador de sitios estáticos como [Astro](https://astro.build/)
  o HTML/CSS/JS puro.
- Integrar [MapLibre GL JS](https://maplibre.org/) sobre un basemap gratuito
  (OpenStreetMap o Carto) para dibujar las capas generadas por el ETL
  (`data/processed/`) con filtros interactivos por tema (salud, población,
  sitios de interés, restaurantes, ciclorutas, etc.).
- Crear el `package.json` real con las dependencias del frontend.

## `public/`

Carpeta de archivos estáticos servidos tal cual, sin procesar por el build.
Ya contiene dos ganchos preparados para fases futuras, hoy inactivos:

- **`robots.txt`** — placeholder mínimo y seguro. Se completará con reglas
  reales y referencia a `sitemap.xml` en la Fase 6 (SEO y monetización).
- **`ads.txt`** — placeholder comentado, sin `pub-id` real. Se activará en la
  Fase 6 una vez exista una cuenta de Google AdSense aprobada.

No existe todavía `sitemap.xml` ni meta tags/Open Graph: no tiene sentido
generarlos sin páginas reales. Quedan documentados aquí como pendientes de las
Fases 4 (meta tags) y 6 (sitemap).
