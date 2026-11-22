"""Descarga, limpia y simplifica la capa de ciclorutas de Bogotá.

Fuente: servicio ArcGIS REST "Mapa_Referencia" de Catastro Bogotá, capa 18
("Cicloruta"), cuyo dato original pertenece al IDU (Instituto de Desarrollo
Urbano) y está licenciado CC BY 4.0 vía Datos Abiertos Bogotá:
https://datosabiertos.bogota.gov.co/dataset/cicloruta-bogota-d-c
"""

import geopandas as gpd
import pandas as pd
import requests

LAYER_URL = (
    "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/"
    "Mapa_Referencia/Mapa_Referencia/MapServer/18/query"
)
PAGE_SIZE = 1000
SIMPLIFY_TOLERANCE_DEG = 0.00005  # ~5 m en el ecuador, suficiente para un mapa web
COORDINATE_PRECISION = 5  # ~1.1 m, reduce el peso del GeoJSON sin perder fidelidad visible
OUTPUT_PATH = "data/processed/ciclorutas.geojson"


def fetch_all_features() -> gpd.GeoDataFrame:
    frames = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
            "resultRecordCount": PAGE_SIZE,
            "resultOffset": offset,
        }
        response = requests.get(LAYER_URL, params=params, timeout=60)
        response.raise_for_status()
        page = gpd.GeoDataFrame.from_features(response.json()["features"], crs="EPSG:4326")
        if page.empty:
            break
        frames.append(page)
        offset += PAGE_SIZE
        if len(page) < PAGE_SIZE:
            break
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:4326")


def simplify(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=True)
    return gdf


def main() -> None:
    gdf = fetch_all_features()
    gdf = simplify(gdf)
    gdf.to_file(OUTPUT_PATH, driver="GeoJSON", COORDINATE_PRECISION=COORDINATE_PRECISION)
    print(f"{len(gdf)} features escritas en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
