# `data/`

Almacenamiento estático de las capas geoespaciales del proyecto. No hay base
de datos ni servidor: todo vive como archivos versionados (o ignorados, según
el caso) dentro de este repositorio.

**Estado actual:** esqueleto vacío (Fase 1). Sin datos todavía.

## Convención de carpetas

- **`raw/`** — descargas temporales/crudas obtenidas directamente de las APIs
  de origen (IDECA, Datos Abiertos Bogotá). **No se versiona** (ver
  `.gitignore`), salvo este `README.md` y el `.gitkeep` que mantiene la
  carpeta visible en git. Su contenido se regenera en cada ejecución del ETL.
- **`processed/`** — resultado final, ya limpio y simplificado, en formatos
  ultraligeros (GeoJSON simplificado o PMTiles). **Sí se versiona**: es el
  archivo que consumirá directamente el frontend estático en `site/`.

## Licencias y atribución de los datos

La licencia MIT del repositorio (ver `/LICENSE`) cubre el código, no los
datos. Cada fuente de datos integrada (IDECA, Datos Abiertos Bogotá,
OpenStreetMap/Carto como basemap) tiene sus propios términos de uso y
requisitos de atribución, que deben documentarse aquí a medida que se
incorpore cada capa en la Fase 2.
