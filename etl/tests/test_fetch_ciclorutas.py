import logging

import geopandas as gpd
import pytest
import requests
from shapely.geometry import Polygon

import fetch_ciclorutas


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def make_feature(i):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(i), float(i)]},
        "properties": {"id": i},
    }


# --- configure_logging -----------------------------------------------------


def test_configure_logging_sets_level():
    fetch_ciclorutas.configure_logging(level=logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG
    fetch_ciclorutas.configure_logging()  # vuelve a INFO para no afectar otros tests
    assert logging.getLogger().level == logging.INFO


# --- get_total_count ---------------------------------------------------------


def test_get_total_count_success(monkeypatch):
    monkeypatch.setattr(
        fetch_ciclorutas.requests,
        "get",
        lambda *a, **k: FakeResponse({"count": 42}),
    )
    assert fetch_ciclorutas.get_total_count() == 42


def test_get_total_count_request_error_is_logged_and_raised(monkeypatch, caplog):
    def raise_error(*a, **k):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(fetch_ciclorutas.requests, "get", raise_error)
    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(requests.ConnectionError):
            fetch_ciclorutas.get_total_count()
    assert "No se pudo obtener el conteo total" in caplog.text


def test_get_total_count_missing_key_is_logged_and_raised(monkeypatch, caplog):
    monkeypatch.setattr(
        fetch_ciclorutas.requests, "get", lambda *a, **k: FakeResponse({})
    )
    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(KeyError):
            fetch_ciclorutas.get_total_count()
    assert "No se pudo obtener el conteo total" in caplog.text


# --- fetch_page --------------------------------------------------------------


def test_fetch_page_success_first_try(monkeypatch):
    payload = {"features": [make_feature(0)]}
    monkeypatch.setattr(
        fetch_ciclorutas.requests, "get", lambda *a, **k: FakeResponse(payload)
    )
    assert fetch_ciclorutas.fetch_page(0) == payload


def test_fetch_page_retries_then_succeeds(monkeypatch, caplog):
    calls = {"n": 0}
    payload = {"features": [make_feature(0)]}

    def flaky_get(*a, **k):
        calls["n"] += 1
        if calls["n"] < 2:
            raise requests.Timeout("slow")
        return FakeResponse(payload)

    monkeypatch.setattr(fetch_ciclorutas.requests, "get", flaky_get)
    monkeypatch.setattr(fetch_ciclorutas.time, "sleep", lambda *_: None)
    with caplog.at_level(logging.WARNING, logger="etl.fetch_ciclorutas"):
        result = fetch_ciclorutas.fetch_page(0)
    assert result == payload
    assert calls["n"] == 2
    assert "Intento 1/3 fallido" in caplog.text


def test_fetch_page_exhausts_retries(monkeypatch, caplog):
    def always_fails(*a, **k):
        raise requests.Timeout("too slow")

    monkeypatch.setattr(fetch_ciclorutas.requests, "get", always_fails)
    monkeypatch.setattr(fetch_ciclorutas.time, "sleep", lambda *_: None)
    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(requests.Timeout):
            fetch_ciclorutas.fetch_page(0)
    assert "Agotados los reintentos" in caplog.text


# --- fetch_all_features -------------------------------------------------------


def test_fetch_all_features_paginates_until_short_page(monkeypatch):
    monkeypatch.setattr(fetch_ciclorutas, "PAGE_SIZE", 2)
    pages = [
        {"features": [make_feature(0), make_feature(1)]},
        {"features": [make_feature(2)]},
    ]
    calls = {"n": 0}

    def fake_fetch_page(offset):
        page = pages[calls["n"]]
        calls["n"] += 1
        return page

    monkeypatch.setattr(fetch_ciclorutas, "fetch_page", fake_fetch_page)
    gdf = fetch_ciclorutas.fetch_all_features(total_count=3)
    assert len(gdf) == 3
    assert calls["n"] == 2


def test_fetch_all_features_uses_total_count_when_not_provided(monkeypatch):
    monkeypatch.setattr(fetch_ciclorutas, "get_total_count", lambda: 0)
    monkeypatch.setattr(
        fetch_ciclorutas, "fetch_page", lambda offset: {"features": []}
    )
    gdf = fetch_ciclorutas.fetch_all_features()
    assert len(gdf) == 0


def test_fetch_all_features_no_results_logs_warning(monkeypatch, caplog):
    monkeypatch.setattr(
        fetch_ciclorutas, "fetch_page", lambda offset: {"features": []}
    )
    with caplog.at_level(logging.WARNING, logger="etl.fetch_ciclorutas"):
        gdf = fetch_ciclorutas.fetch_all_features(total_count=0)
    assert len(gdf) == 0
    assert "geometry" in gdf.columns
    assert "No se descargaron features" in caplog.text


# --- get_surface_domain / label_surface_types ---------------------------------


def test_get_surface_domain_success(monkeypatch):
    payload = {
        "fields": [
            {"name": "OBJECTID"},
            {
                "name": "CICTSUPERF",
                "domain": {
                    "codedValues": [
                        {"code": 0, "name": "Sin dato"},
                        {"code": 1, "name": "Concreto"},
                    ]
                },
            },
        ]
    }
    monkeypatch.setattr(
        fetch_ciclorutas.requests, "get", lambda *a, **k: FakeResponse(payload)
    )
    assert fetch_ciclorutas.get_surface_domain() == {0: "Sin dato", 1: "Concreto"}


def test_get_surface_domain_request_error_is_logged_and_raised(monkeypatch, caplog):
    def raise_error(*a, **k):
        raise requests.ConnectionError("boom")

    monkeypatch.setattr(fetch_ciclorutas.requests, "get", raise_error)
    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(requests.ConnectionError):
            fetch_ciclorutas.get_surface_domain()
    assert "No se pudo obtener el dominio" in caplog.text


def test_get_surface_domain_missing_field_is_logged_and_raised(monkeypatch, caplog):
    monkeypatch.setattr(
        fetch_ciclorutas.requests,
        "get",
        lambda *a, **k: FakeResponse({"fields": [{"name": "OBJECTID"}]}),
    )
    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(StopIteration):
            fetch_ciclorutas.get_surface_domain()
    assert "No se pudo obtener el dominio" in caplog.text


def test_label_surface_types_maps_known_and_unknown_codes():
    gdf = gpd.GeoDataFrame({"CICTSUPERF": [1, 2, 99]})
    domain = {1: "Concreto", 2: "Asfalto"}

    result = fetch_ciclorutas.label_surface_types(gdf, domain)

    assert result["tipo_superficie"].tolist() == ["Concreto", "Asfalto", "Desconocido"]
    assert "tipo_superficie" not in gdf.columns  # la entrada original no se muta


# --- simplify ------------------------------------------------------------------


def test_simplify_removes_collinear_points_and_preserves_crs():
    coords = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2), (1, 1), (1, 0), (0, 0)]
    poly = Polygon(coords)
    gdf = gpd.GeoDataFrame({"id": [1]}, geometry=[poly], crs="EPSG:4326")
    original_points = len(poly.exterior.coords)

    result = fetch_ciclorutas.simplify(gdf)

    assert result.crs == gdf.crs
    assert len(result) == 1
    simplified_points = len(result.geometry.iloc[0].exterior.coords)
    assert simplified_points < original_points
    # la entrada original no debe mutarse
    assert len(gdf.geometry.iloc[0].exterior.coords) == original_points


# --- main ----------------------------------------------------------------------


class DummyGDF:
    def __init__(self, n, recorder):
        self._n = n
        self._recorder = recorder

    def __len__(self):
        return self._n

    def to_file(self, *args, **kwargs):
        self._recorder.append((args, kwargs))


def test_main_success_logs_and_writes_output(monkeypatch, caplog):
    recorder = []
    monkeypatch.setattr(fetch_ciclorutas, "configure_logging", lambda: None)
    monkeypatch.setattr(
        fetch_ciclorutas, "fetch_all_features", lambda: DummyGDF(3, recorder)
    )
    monkeypatch.setattr(fetch_ciclorutas, "get_surface_domain", lambda: {})
    monkeypatch.setattr(fetch_ciclorutas, "label_surface_types", lambda gdf, domain: gdf)
    monkeypatch.setattr(fetch_ciclorutas, "simplify", lambda gdf: gdf)

    with caplog.at_level(logging.INFO, logger="etl.fetch_ciclorutas"):
        fetch_ciclorutas.main()

    assert len(recorder) == 1
    _, kwargs = recorder[0]
    assert kwargs["driver"] == "GeoJSON"
    assert "3 features escritas en" in caplog.text


def test_main_logs_and_reraises_on_failure(monkeypatch, caplog):
    monkeypatch.setattr(fetch_ciclorutas, "configure_logging", lambda: None)

    def boom():
        raise RuntimeError("fuente caída")

    monkeypatch.setattr(fetch_ciclorutas, "fetch_all_features", boom)

    with caplog.at_level(logging.ERROR, logger="etl.fetch_ciclorutas"):
        with pytest.raises(RuntimeError, match="fuente caída"):
            fetch_ciclorutas.main()

    assert "El ETL de ciclorutas falló" in caplog.text
