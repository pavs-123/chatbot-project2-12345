import pytest
pytest.importorskip("mcp")

import types
import asyncio

# Import after skipping check
from mcp_weather import server as srv


@pytest.mark.asyncio
async def test_get_weather_tool(monkeypatch):
    async def fake_geocode_city(city: str):
        return {"name": city, "latitude": 1.23, "longitude": 4.56, "country": "X"}

    async def fake_fetch_weather(lat: float, lon: float):
        return {"current_weather": {"temperature": 25.0}}

    monkeypatch.setattr(srv, "geocode_city", fake_geocode_city, raising=True)
    monkeypatch.setattr(srv, "fetch_weather", fake_fetch_weather, raising=True)

    out = await srv.get_weather(city="Testville")
    assert "Testville" in out
    assert "current_weather" in out


@pytest.mark.asyncio
async def test_get_hourly_tool(monkeypatch):
    async def fake_geocode_city(city: str):
        return {"name": city, "latitude": 1.23, "longitude": 4.56, "country": "X"}

    async def fake_fetch_hourly(lat: float, lon: float, hours: int):
        return {"hourly": {"time": ["t1", "t2"], "temperature_2m": [20.1, 21.3]}}

    monkeypatch.setattr(srv, "geocode_city", fake_geocode_city, raising=True)
    monkeypatch.setattr(srv, "fetch_hourly", fake_fetch_hourly, raising=True)

    out = await srv.get_hourly_forecast(city="Testville", hours=2)
    assert "hours" in out and "forecast" in out


@pytest.mark.asyncio
async def test_get_daily_tool(monkeypatch):
    async def fake_geocode_city(city: str):
        return {"name": city, "latitude": 1.23, "longitude": 4.56, "country": "X"}

    async def fake_fetch_daily(lat: float, lon: float, days: int):
        return {"daily": {"time": ["d1", "d2", "d3"], "temperature_2m_max": [25, 26, 27]}}

    monkeypatch.setattr(srv, "geocode_city", fake_geocode_city, raising=True)
    monkeypatch.setattr(srv, "fetch_daily", fake_fetch_daily, raising=True)

    out = await srv.get_daily_forecast(city="Testville", days=3)
    assert "days" in out and "forecast" in out
