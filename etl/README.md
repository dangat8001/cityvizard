# `etl/`

Capa de extracción, limpieza y simplificación de datos geoespaciales.

**Estado actual (Fase 2 — ETL geoespacial en Python):** primera capa
funcional lista: `src/fetch_ciclorutas.py`.

## Ejecutar localmente

```bash
# desde la raíz del repo, con el venv del proyecto activo
pip install -r etl/requirements.txt
python3 etl/src/fetch_ciclorutas.py
```

Genera/actualiza `data/processed/ciclorutas.geojson`.

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

**Pendiente (fuera de alcance de esta fase):** `config/` para centralizar URLs
de múltiples fuentes a medida que se agreguen más capas (salud, población,
sitios de interés, restaurantes).

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

**Qué llegará después (Fase 3 — Automatización):**
- Este script será invocado periódicamente (cron semanal) por un workflow de
  GitHub Actions definido en `.github/workflows/etl.yml`, que lo ejecutará y
  hará commit automático de los resultados en `data/processed/`.
