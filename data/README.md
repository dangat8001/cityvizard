# `data/`

Almacenamiento estático de las capas geoespaciales del proyecto. No hay base
de datos ni servidor: todo vive como archivos versionados (o ignorados, según
el caso) dentro de este repositorio.

**Estado actual:** dos capas procesadas disponibles.

| Capa | Archivo | Fuente | Licencia | Generado por |
|---|---|---|---|---|
| Ciclorutas Bogotá | `processed/ciclorutas.geojson` | [Datos Abiertos Bogotá — IDU](https://datosabiertos.bogota.gov.co/dataset/cicloruta-bogota-d-c) | CC BY 4.0 | `etl/src/fetch_ciclorutas.py` |
| Población por UPZ (112 zonas, proyección 2026) | `processed/poblacion_upz.geojson` | Límites: Catastro Bogotá. Población: [SDP — Proyecciones y retroproyecciones de Población 2005-2035](https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035) | CC BY 4.0 | `etl/src/fetch_poblacion_upz.py` |

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
