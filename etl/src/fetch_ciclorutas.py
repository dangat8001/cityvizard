"""Descarga, limpia y simplifica la capa de ciclorutas de Bogotá.

Fuente: servicio ArcGIS REST "Mapa_Referencia" de Catastro Bogotá, capa 18
("Cicloruta"), cuyo dato original pertenece al IDU (Instituto de Desarrollo
Urbano) y está licenciado CC BY 4.0 vía Datos Abiertos Bogotá:
https://datosabiertos.bogota.gov.co/dataset/cicloruta-bogota-d-c
"""

import logging
import sys
import time

import geopandas as gpd
import pandas as pd
import requests
from tqdm import tqdm

logger = logging.getLogger("etl.fetch_ciclorutas")

LAYER_BASE_URL = (
    "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/"
    "Mapa_Referencia/Mapa_Referencia/MapServer/18"
)
LAYER_URL = f"{LAYER_BASE_URL}/query"
SURFACE_FIELD = "CICTSUPERF"
SURFACE_LABEL_FIELD = "tipo_superficie"
PAGE_SIZE = 1000
SIMPLIFY_TOLERANCE_DEG = 0.00005  # ~5 m en el ecuador, suficiente para un mapa web
COORDINATE_PRECISION = 5  # ~1.1 m, reduce el peso del GeoJSON sin perder fidelidad visible
OUTPUT_PATH = "data/processed/ciclorutas.geojson"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )


def get_total_count() -> int:
    params = {"where": "1=1", "returnCountOnly": "true", "f": "json"}
    try:
        response = requests.get(LAYER_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()["count"]
    except (requests.RequestException, ValueError, KeyError) as exc:
        logger.error("No se pudo obtener el conteo total de features: %s", exc)
        raise


def fetch_page(offset: int) -> dict:
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "resultRecordCount": PAGE_SIZE,
        "resultOffset": offset,
    }
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(LAYER_URL, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            logger.warning(
                "Intento %s/%s fallido al descargar offset=%s: %s",
                attempt,
                MAX_RETRIES,
                offset,
                exc,
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    logger.error("Agotados los reintentos al descargar offset=%s", offset)
    raise last_exc


def fetch_all_features(total_count: int | None = None) -> gpd.GeoDataFrame:
    if total_count is None:
        total_count = get_total_count()
    logger.info("Total de features a descargar: %s", total_count)

    frames = []
    offset = 0
    with tqdm(total=total_count, unit="feature", desc="Descargando ciclorutas") as pbar:
        while True:
            payload = fetch_page(offset)
            features = payload.get("features", [])
            page = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
            if page.empty:
                break
            frames.append(page)
            pbar.update(len(page))
            offset += PAGE_SIZE
            if len(page) < PAGE_SIZE:
                break

    if not frames:
        logger.warning("No se descargaron features del servicio.")
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")

    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")
    logger.info("Descarga completa: %s features obtenidas", len(gdf))
    return gdf


def get_surface_domain() -> dict[int, str]:
    try:
        response = requests.get(LAYER_BASE_URL, params={"f": "json"}, timeout=30)
        response.raise_for_status()
        fields = response.json()["fields"]
        surface_field = next(f for f in fields if f["name"] == SURFACE_FIELD)
        return {cv["code"]: cv["name"] for cv in surface_field["domain"]["codedValues"]}
    except (requests.RequestException, ValueError, KeyError, StopIteration) as exc:
        logger.error("No se pudo obtener el dominio de %s: %s", SURFACE_FIELD, exc)
        raise


def label_surface_types(gdf: gpd.GeoDataFrame, domain: dict[int, str]) -> gpd.GeoDataFrame:
    logger.info("Etiquetando %s a partir del dominio del servicio", SURFACE_LABEL_FIELD)
    gdf = gdf.copy()
    gdf[SURFACE_LABEL_FIELD] = gdf[SURFACE_FIELD].map(domain).fillna("Desconocido")
    return gdf


def simplify(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    logger.info("Simplificando geometrías (tolerancia=%s°)", SIMPLIFY_TOLERANCE_DEG)
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=True)
    return gdf


def main() -> None:
    configure_logging()
    logger.info("Iniciando ETL de ciclorutas")
    try:
        gdf = fetch_all_features()
        domain = get_surface_domain()
        gdf = label_surface_types(gdf, domain)
        gdf = simplify(gdf)
        gdf.to_file(OUTPUT_PATH, driver="GeoJSON", COORDINATE_PRECISION=COORDINATE_PRECISION)
        logger.info("%s features escritas en %s", len(gdf), OUTPUT_PATH)
    except Exception:
        logger.exception("El ETL de ciclorutas falló")
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
