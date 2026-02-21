from __future__ import annotations
from typing import Any, Dict, Optional
import httpx

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    params = {"name": city, "count": 1}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(GEOCODE_URL, params=params)
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or []
        if not results:
            return None
        top = results[0]
        return {
            "name": top.get("name"),
            "latitude": top.get("latitude"),
            "longitude": top.get("longitude"),
            "country": top.get("country"),
        }


async def fetch_weather(lat: float, lon: float) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        return r.json()


async def fetch_hourly(lat: float, lon: float, hours: int = 24) -> Dict[str, Any]:
    """Fetch hourly forecast for the next N hours."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weathercode",
        "forecast_hours": max(1, min(int(hours), 120)),  # clamp 1..120
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        return r.json()


async def fetch_daily(lat: float, lon: float, days: int = 3) -> Dict[str, Any]:
    """Fetch daily forecast for the next N days."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weathercode",
        "forecast_days": max(1, min(int(days), 7)),  # clamp 1..7
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPEN_METEO_URL, params=params)
        r.raise_for_status()
        return r.json()
