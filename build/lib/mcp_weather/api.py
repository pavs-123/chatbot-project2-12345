"""
FastAPI app for local weather checks.

Run:
  uvicorn mcp_weather.api:app --reload --port 8000

Examples:
  curl "http://127.0.0.1:8000/weather?city=Berlin"
  curl "http://127.0.0.1:8000/weather/coords?lat=52.52&lon=13.41"
"""
from __future__ import annotations
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Query

from .helpers import geocode_city, fetch_weather, fetch_hourly, fetch_daily

app = FastAPI(title="MCP Weather API", version="0.1.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/weather")
async def weather_city(city: str = Query(..., description="City name")) -> Dict[str, Any]:
    info = await geocode_city(city)
    if not info:
        raise HTTPException(status_code=404, detail=f"No results for '{city}'")
    data = await fetch_weather(info["latitude"], info["longitude"])
    return {
        "city": info["name"],
        "coords": {"lat": info["latitude"], "lon": info["longitude"]},
        "weather": data.get("current_weather", data)
    }


@app.get("/weather/coords")
async def weather_coords(lat: float, lon: float) -> Dict[str, Any]:
    data = await fetch_weather(lat, lon)
    return {
        "coords": {"lat": lat, "lon": lon},
        "weather": data.get("current_weather", data)
    }


@app.get("/forecast/hourly")
async def hourly_forecast(city: str | None = None, lat: float | None = None, lon: float | None = None, hours: int = 24) -> Dict[str, Any]:
    if city:
        info = await geocode_city(city)
        if not info:
            raise HTTPException(status_code=404, detail=f"No results for '{city}'")
        lat, lon = info["latitude"], info["longitude"]
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Provide either city or both lat & lon")
    data = await fetch_hourly(lat, lon, hours)
    return {
        "city": city,
        "coords": {"lat": lat, "lon": lon},
        "hours": hours,
        "forecast": data.get("hourly", data)
    }


@app.get("/forecast/daily")
async def daily_forecast(city: str | None = None, lat: float | None = None, lon: float | None = None, days: int = 3) -> Dict[str, Any]:
    if city:
        info = await geocode_city(city)
        if not info:
            raise HTTPException(status_code=404, detail=f"No results for '{city}'")
        lat, lon = info["latitude"], info["longitude"]
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Provide either city or both lat & lon")
    data = await fetch_daily(lat, lon, days)
    return {
        "city": city,
        "coords": {"lat": lat, "lon": lon},
        "days": days,
        "forecast": data.get("daily", data)
    }
