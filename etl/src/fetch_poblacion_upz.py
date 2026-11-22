"""Descarga y une límites de UPZ con proyecciones de población por UPZ.

Fuentes:
- Límites de UPZ (112 features, polígono): servicio ArcGIS REST
  "indicadorespaciopublico" de Catastro Bogotá, capa 4 ("Total por UPZ").
- Población: Secretaría Distrital de Planeación (SDP), "Proyecciones y
  retroproyecciones de Población (2005-2035)" por UPZ, vía Datos Abiertos
  Bogotá: https://datosabiertos.bogota.gov.co/dataset/proyecciones-y-retroproyecciones-de-poblacion-2005-2035
  Licencia: CC BY 4.0.
"""

import io
import logging
import sys

import geopandas as gpd
import pandas as pd
import requests

logger = logging.getLogger("etl.fetch_poblacion_upz")

UPZ_LAYER_URL = (
    "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/"
    "espaciopublico/indicadorespaciopublico/MapServer/4/query"
)
POBLACION_URL = (
    "https://datosabiertos.bogota.gov.co/dataset/"
    "proyecciones-y-retroproyecciones-de-poblacion-2005-2035/resource/"
    "96583ea9-9c0b-40c3-9797-156d173eb734/download/"
    "202503_upz_proyeccion_retroproyeccion_poblacion_2005_2035.ods"
)
TARGET_YEAR = 2026
METRIC_CRS = "EPSG:3116"  # MAGNA-SIRGAS / Colombia Bogota, para calcular área en m²
SIMPLIFY_TOLERANCE_DEG = 0.0001  # ~11 m, suficiente para polígonos a escala de zona
COORDINATE_PRECISION = 5
OUTPUT_PATH = "data/processed/poblacion_upz.geojson"


def fetch_upz_boundaries() -> gpd.GeoDataFrame:
    params = {
        "where": "1=1",
        "outFields": "CODIGO_UPZ,NOMBRE",
        "returnGeometry": "true",
        "f": "geojson",
    }
    try:
        response = requests.get(UPZ_LAYER_URL, params=params, timeout=60)
        response.raise_for_status()
        gdf = gpd.GeoDataFrame.from_features(response.json()["features"], crs="EPSG:4326")
    except (requests.RequestException, ValueError, KeyError) as exc:
        logger.error("No se pudieron obtener los límites de UPZ: %s", exc)
        raise
    logger.info("Límites de UPZ descargados: %s features", len(gdf))
    return gdf


def download_population_table() -> bytes:
    try:
        response = requests.get(POBLACION_URL, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.RequestException as exc:
        logger.error("No se pudo descargar la tabla de población de la SDP: %s", exc)
        raise


def parse_population_table(content: bytes, year: int = TARGET_YEAR) -> pd.DataFrame:
    raw = pd.read_excel(io.BytesIO(content), engine="odf", header=None)
    header = raw.iloc[4].tolist()
    df = raw.iloc[5:].copy()
    df.columns = header
    df["AÑO"] = pd.to_numeric(df["AÑO"], errors="coerce")
    df["Código UPZ"] = pd.to_numeric(df["Código UPZ"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

    year_df = df[df["AÑO"] == year][["Código UPZ", "Total"]].rename(
        columns={"Código UPZ": "codigo_upz", "Total": "poblacion_total"}
    )
    logger.info("Población filtrada al año %s: %s UPZ", year, len(year_df))
    return year_df


def join_population(upz_gdf: gpd.GeoDataFrame, poblacion_df: pd.DataFrame) -> gpd.GeoDataFrame:
    upz_gdf = upz_gdf.copy()
    upz_gdf["codigo_upz"] = pd.to_numeric(upz_gdf["CODIGO_UPZ"], errors="coerce")
    merged = upz_gdf.merge(poblacion_df, on="codigo_upz", how="inner")
    merged = merged.rename(columns={"NOMBRE": "nombre"})[
        ["codigo_upz", "nombre", "poblacion_total", "geometry"]
    ]
    merged = gpd.GeoDataFrame(merged, geometry="geometry", crs=upz_gdf.crs)
    logger.info("UPZ con población unida: %s de %s", len(merged), len(upz_gdf))
    return merged


def add_density(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    area_m2 = gdf.geometry.to_crs(METRIC_CRS).area
    area_ha = area_m2 / 10_000
    gdf["area_ha"] = area_ha.round(2)
    gdf["densidad_hab_ha"] = (gdf["poblacion_total"] / area_ha).round(2)
    return gdf


def simplify(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    logger.info("Simplificando geometrías (tolerancia=%s°)", SIMPLIFY_TOLERANCE_DEG)
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=True)
    return gdf


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
        force=True,
    )


def main() -> None:
    configure_logging()
    logger.info("Iniciando ETL de población por UPZ")
    try:
        upz_gdf = fetch_upz_boundaries()
        poblacion_df = parse_population_table(download_population_table())
        gdf = join_population(upz_gdf, poblacion_df)
        gdf = add_density(gdf)
        gdf = simplify(gdf)
        gdf.to_file(OUTPUT_PATH, driver="GeoJSON", COORDINATE_PRECISION=COORDINATE_PRECISION)
        logger.info("%s UPZ escritas en %s", len(gdf), OUTPUT_PATH)
    except Exception:
        logger.exception("El ETL de población por UPZ falló")
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
