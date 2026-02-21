import pytest
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from mcp_weather.api import app
import mcp_weather.api as api_mod


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_weather_city_endpoint(monkeypatch):
    # Monkeypatch the API-level helpers to avoid network calls
    async def fake_geocode_city(city: str):
        return {"name": city, "latitude": 52.52, "longitude": 13.41, "country": "DE"}

    async def fake_fetch_weather(lat: float, lon: float):
        return {"current_weather": {"temperature": 20.0, "windspeed": 5.0}}

    monkeypatch.setattr(api_mod, "geocode_city", fake_geocode_city, raising=True)
    monkeypatch.setattr(api_mod, "fetch_weather", fake_fetch_weather, raising=True)

    client = TestClient(app)
    r = client.get("/weather", params={"city": "Berlin"})
    assert r.status_code == 200
    data = r.json()
    assert data["city"] == "Berlin"
    assert data["coords"] == {"lat": 52.52, "lon": 13.41}
    assert "weather" in data


def test_weather_coords_endpoint(monkeypatch):
    async def fake_fetch_weather(lat: float, lon: float):
        return {"current_weather": {"temperature": 21.5, "windspeed": 3.2}}

    monkeypatch.setattr(api_mod, "fetch_weather", fake_fetch_weather, raising=True)

    client = TestClient(app)
    r = client.get("/weather/coords", params={"lat": 40.7128, "lon": -74.0060})
    assert r.status_code == 200
    data = r.json()
    assert data["coords"] == {"lat": 40.7128, "lon": -74.006}
    assert "weather" in data
