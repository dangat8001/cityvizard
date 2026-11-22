# `etl/`

Capa de extracción, limpieza y simplificación de datos geoespaciales.

**Estado actual:** dos scripts funcionales: `src/fetch_ciclorutas.py` y
`src/fetch_poblacion_upz.py`.

## Ejecutar localmente

```bash
# desde la raíz del repo, con el venv del proyecto activo
pip install -r etl/requirements.txt
python3 etl/src/fetch_ciclorutas.py
python3 etl/src/fetch_poblacion_upz.py
```

Genera/actualiza `data/processed/ciclorutas.geojson` y
`data/processed/poblacion_upz.geojson` respectivamente.

## `src/fetch_ciclorutas.py`

Descarga la capa **Cicloruta** del servicio ArcGIS REST "Mapa_Referencia" de
Catastro Bogotá (capa 18, geometría de polígono), paginando en bloques de
1000 features (límite del servicio, ~6300 features en total), simplifica las
geometrías (`shapely.simplify`, tolerancia ~5 m) y escribe el resultado como
GeoJSON con precisión de coordenadas reducida a 5 decimales (~1.1 m) para
mantener el archivo ligero (~1.7 MB para toda la ciudad).

Durante la ejecución muestra una barra de progreso (`tqdm`) sobre el total de
features a descargar y registra logs informativos de cada etapa (conteo
total, descarga completa, simplificación, escritura final) y de errores
(reintentos de red con backoff, fallos agotados, excepciones no controladas)
vía el módulo estándar `logging`, bajo el logger `etl.fetch_ciclorutas`.

- **Fuente:** [Ciclorruta. Bogotá D.C. — Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/cicloruta-bogota-d-c)
  (entidad responsable: IDU — Instituto de Desarrollo Urbano).
- **Licencia de los datos:** CC BY 4.0.
- **Endpoint consultado:** `https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/Mapa_Referencia/Mapa_Referencia/MapServer/18/query`
- **Campos originales:** `CICCODIGO` (id único), `CICCIV` (código vial),
  `CICTSUPERF` (tipo de superficie), `OBJECTID`.

**Pendiente:** `config/` para centralizar URLs de múltiples fuentes a medida
que se agreguen más capas (salud, sitios de interés, restaurantes).

## `src/fetch_poblacion_upz.py`

Une dos fuentes para generar un mapa de población con densidad por UPZ
(Unidad de Planeamiento Zonal, 112 zonas):

- **Límites geográficos:** servicio ArcGIS REST `indicadorespaciopublico` de
  Catastro Bogotá, capa 4 ("Total por UPZ") — campos `CODIGO_UPZ`, `NOMBRE`,
  geometría de polígono.
  `https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/espaciopublico/indicadorespaciopublico/MapServer/4/query`
- **Población:** Secretaría Distrital de Planeación (SDP), dataset
  ["Proyecciones y retroproyecciones de Población (2005-2035)"](https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035)
  por UPZ (archivo `.ods`, parseado con `pandas` + `odfpy`), filtrado al año
  `TARGET_YEAR` (2026 por defecto).

Ambas fuentes se unen por código de UPZ (`codigo_upz`). Se calcula además
`area_ha` (reproyectando a `EPSG:3116`, MAGNA-SIRGAS/Bogotá) y
`densidad_hab_ha` (población / área). El resultado se simplifica
(`shapely.simplify`, ~11 m) y se escribe como GeoJSON (~154 KB para las 112
UPZ).

**Nota sobre granularidad:** UPZ es el nivel más fino con datos de población
*vigentes y confiables* que encontramos. DANE sí publica población a nivel de
manzana censal (2018), pero no hay una unidad oficial "por barrio", y la
fuente de manzanas es una API frágil con un archivo nacional de ~400 MB —
ver la discusión completa en el historial del proyecto antes de intentar esa
granularidad.

- **Licencia de los datos:** CC BY 4.0.

## Tests y cobertura

Todo módulo Python de `src/` debe tener su correspondiente suite en `tests/`,
con el objetivo de mantener **100% de cobertura** (política del proyecto,
no solo de esta carpeta). Se verifica con `pytest-cov` y falla si la
cobertura cae por debajo del 100% (`fail_under = 100` en `pyproject.toml`).

```bash
# desde la raíz del repo, con el venv del proyecto activo
pip install -r etl/requirements.txt -r etl/requirements-dev.txt
cd etl && python -m pytest --cov=src --cov-report=term-missing
```

Los tests no hacen llamadas de red reales: mockean `requests.get` (vía
`monkeypatch`) para simular respuestas exitosas, errores HTTP/timeout con
reintentos, y respuestas vacías o malformadas.

## Automatización (Fase 3)

Ambos scripts ya se ejecutan solos, sin intervención manual, vía
[`.github/workflows/etl.yml`](../.github/workflows/etl.yml): cron semanal
(lunes 06:00 UTC) + disparo manual (`workflow_dispatch`). El workflow corre
los tests como gate de calidad, ejecuta los dos scripts y, si `data/processed/`
cambió, lo commitea y pushea automáticamente a `main` como
`github-actions[bot]`. Ver también [`.github/README.md`](../.github/README.md).
