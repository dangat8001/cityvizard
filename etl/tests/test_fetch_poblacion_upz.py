import io
import logging

import geopandas as gpd
import pandas as pd
import pytest
import requests
from shapely.geometry import Polygon

import fetch_poblacion_upz as fpu


class FakeResponse:
    def __init__(self, payload=None, content=b"", status_code=200):
        self._payload = payload
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def make_square_feature(codigo_upz, nombre, x0, y0):
    coords = [(x0, y0), (x0, y0 + 1), (x0 + 1, y0 + 1), (x0 + 1, y0), (x0, y0)]
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [coords]},
        "properties": {"CODIGO_UPZ": codigo_upz, "NOMBRE": nombre},
    }


def test_configure_logging_sets_level():
    fpu.configure_logging(level=logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG
    fpu.configure_logging()  # vuelve a INFO para no afectar otros tests
    assert logging.getLogger().level == logging.INFO


def build_population_ods(rows):
    header = ["Código UPZ", "AÑO", "Total"]
    raw_rows = [[None, None, None]] * 4 + [header] + rows
    df = pd.DataFrame(raw_rows)
    buf = io.BytesIO()
    df.to_excel(buf, engine="odf", header=False, index=False)
    return buf.getvalue()


# --- fetch_upz_boundaries -----------------------------------------------------


def test_fetch_upz_boundaries_success(monkeypatch):
    payload = {"features": [make_square_feature("1", "UNO", 0, 0)]}
    monkeypatch.setattr(fpu.requests, "get", lambda *a, **k: FakeResponse(payload=payload))
    gdf = fpu.fetch_upz_boundaries()
    assert len(gdf) == 1
    assert gdf.crs == "EPSG:4326"


def test_fetch_upz_boundaries_request_error_is_logged_and_raised(monkeypatch, caplog):
    def raise_error(*a, **k):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(fpu.requests, "get", raise_error)
    with pytest.raises(requests.ConnectionError):
        fpu.fetch_upz_boundaries()
    assert "No se pudieron obtener los límites de UPZ" in caplog.text


# --- download_population_table -------------------------------------------------


def test_download_population_table_success(monkeypatch):
    monkeypatch.setattr(
        fpu.requests, "get", lambda *a, **k: FakeResponse(content=b"contenido")
    )
    assert fpu.download_population_table() == b"contenido"


def test_download_population_table_request_error_is_logged_and_raised(monkeypatch, caplog):
    def raise_error(*a, **k):
        raise requests.Timeout("slow")

    monkeypatch.setattr(fpu.requests, "get", raise_error)
    with pytest.raises(requests.Timeout):
        fpu.download_population_table()
    assert "No se pudo descargar la tabla de población" in caplog.text


# --- parse_population_table -----------------------------------------------------


def test_parse_population_table_filters_by_year():
    content = build_population_ods(
        [
            ["1", 2025, 100],
            ["1", 2026, 150],
            ["2", 2026, 300],
            ["2", 2027, 350],
        ]
    )
    result = fpu.parse_population_table(content, year=2026)
    assert sorted(result["codigo_upz"].tolist()) == [1, 2]
    assert sorted(result["poblacion_total"].tolist()) == [150, 300]


# --- join_population -------------------------------------------------------------


def test_join_population_keeps_only_matching_codes():
    upz_gdf = gpd.GeoDataFrame(
        {
            "CODIGO_UPZ": ["1", "2", "3"],
            "NOMBRE": ["UNO", "DOS", "TRES"],
            "geometry": [
                Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
                Polygon([(2, 0), (2, 1), (3, 1), (3, 0)]),
                Polygon([(4, 0), (4, 1), (5, 1), (5, 0)]),
            ],
        },
        crs="EPSG:4326",
    )
    poblacion_df = pd.DataFrame({"codigo_upz": [1, 2], "poblacion_total": [150, 300]})

    result = fpu.join_population(upz_gdf, poblacion_df)

    assert sorted(result["nombre"].tolist()) == ["DOS", "UNO"]
    assert set(result.columns) == {"codigo_upz", "nombre", "poblacion_total", "geometry"}
    assert result.crs == upz_gdf.crs


# --- add_density -------------------------------------------------------------------


def test_add_density_computes_area_and_density():
    # cuadrado de 1 grado de lado centrado cerca del ecuador: área conocida y positiva
    gdf = gpd.GeoDataFrame(
        {
            "codigo_upz": [1],
            "nombre": ["UNO"],
            "poblacion_total": [1000],
            "geometry": [Polygon([(0, 0), (0, 0.01), (0.01, 0.01), (0.01, 0)])],
        },
        crs="EPSG:4326",
    )

    result = fpu.add_density(gdf)

    assert result["area_ha"].iloc[0] > 0
    assert result["densidad_hab_ha"].iloc[0] == pytest.approx(
        1000 / result["area_ha"].iloc[0], abs=0.01
    )


# --- simplify ----------------------------------------------------------------------


def test_simplify_preserves_feature_count_and_crs():
    coords = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 0), (0, 0)]
    gdf = gpd.GeoDataFrame(
        {"codigo_upz": [1], "geometry": [Polygon(coords)]}, crs="EPSG:4326"
    )
    result = fpu.simplify(gdf)
    assert len(result) == 1
    assert result.crs == gdf.crs


# --- main ----------------------------------------------------------------------------


class DummyGDF:
    def __init__(self, n, recorder):
        self._n = n
        self._recorder = recorder

    def __len__(self):
        return self._n

    def to_file(self, *args, **kwargs):
        self._recorder.append((args, kwargs))


def test_main_success_writes_output(monkeypatch, caplog):
    recorder = []
    monkeypatch.setattr(fpu, "configure_logging", lambda: None)
    monkeypatch.setattr(fpu, "fetch_upz_boundaries", lambda: object())
    monkeypatch.setattr(fpu, "download_population_table", lambda: b"")
    monkeypatch.setattr(fpu, "parse_population_table", lambda content: object())
    monkeypatch.setattr(fpu, "join_population", lambda upz, pob: DummyGDF(112, recorder))
    monkeypatch.setattr(fpu, "add_density", lambda gdf: gdf)
    monkeypatch.setattr(fpu, "simplify", lambda gdf: gdf)

    with caplog.at_level(logging.INFO, logger="etl.fetch_poblacion_upz"):
        fpu.main()

    assert len(recorder) == 1
    _, kwargs = recorder[0]
    assert kwargs["driver"] == "GeoJSON"
    assert "112 UPZ escritas en" in caplog.text


def test_main_logs_and_reraises_on_failure(monkeypatch, caplog):
    monkeypatch.setattr(fpu, "configure_logging", lambda: None)

    def boom():
        raise RuntimeError("fuente caída")

    monkeypatch.setattr(fpu, "fetch_upz_boundaries", boom)

    with caplog.at_level(logging.ERROR, logger="etl.fetch_poblacion_upz"):
        with pytest.raises(RuntimeError, match="fuente caída"):
            fpu.main()

    assert "El ETL de población por UPZ falló" in caplog.text
