"""
MCP server exposing weather tools.

Run (stdio):
  python -m mcp_weather.server --stdio

Client config example (.mcp.json):
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "mcp_weather.server", "--stdio"]
    }
  }
}
"""
from __future__ import annotations
import argparse
import asyncio
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .helpers import geocode_city, fetch_weather, fetch_hourly, fetch_daily

server = Server("weather")


@server.tool()
async def search_city(query: str) -> str:
    """Search for a city's coordinates using Open-Meteo geocoding.

    Args:
      query: City name, e.g., "Paris" or "San Francisco"
    Returns:
      JSON string: {name, latitude, longitude, country}
    """
    info = await geocode_city(query)
    if not info:
        return TextContent(text=f"No results for '{query}'").text
    return TextContent(text=httpx.dumps_json(info, indent=2)).text


@server.tool()
async def get_weather(city: str | None = None, latitude: float | None = None, longitude: float | None = None) -> str:
    """Get current weather by city or coordinates.

    Args:
      city: City name (uses geocoding)
      latitude: Latitude (if providing coords)
      longitude: Longitude (if providing coords)
    Returns:
      JSON string with weather data
    """
    if city:
        info = await geocode_city(city)
        if not info:
            return TextContent(text=f"No results for '{city}'").text
        latitude = info["latitude"]
        longitude = info["longitude"]

    if latitude is None or longitude is None:
        return TextContent(text="Provide either city or both latitude and longitude").text

    data = await fetch_weather(float(latitude), float(longitude))
    return TextContent(text=httpx.dumps_json({
        "city": city,
        "coords": {"lat": latitude, "lon": longitude},
        "weather": data.get("current_weather", data)
    }, indent=2)).text


@server.tool()
async def get_hourly_forecast(city: str | None = None, latitude: float | None = None, longitude: float | None = None, hours: int = 24) -> str:
    """Get hourly forecast by city or coordinates.

    Args:
      city: City name (optional)
      latitude, longitude: Coordinates (optional)
      hours: Number of hours to forecast (default 24, max 120)
    Returns:
      JSON string with hourly forecast
    """
    if city:
        info = await geocode_city(city)
        if not info:
            return TextContent(text=f"No results for '{city}'").text
        latitude = info["latitude"]
        longitude = info["longitude"]

    if latitude is None or longitude is None:
        return TextContent(text="Provide either city or both latitude and longitude").text

    data = await fetch_hourly(float(latitude), float(longitude), int(hours))
    return TextContent(text=httpx.dumps_json({
        "city": city,
        "coords": {"lat": latitude, "lon": longitude},
        "hours": hours,
        "forecast": data.get("hourly", data)
    }, indent=2)).text


@server.tool()
async def get_daily_forecast(city: str | None = None, latitude: float | None = None, longitude: float | None = None, days: int = 3) -> str:
    """Get daily forecast (next N days) by city or coordinates.

    Args:
      city: City name (optional)
      latitude, longitude: Coordinates (optional)
      days: Number of days (default 3, max 7)
    Returns:
      JSON string with daily forecast
    """
    if city:
        info = await geocode_city(city)
        if not info:
            return TextContent(text=f"No results for '{city}'").text
        latitude = info["latitude"]
        longitude = info["longitude"]

    if latitude is None or longitude is None:
        return TextContent(text="Provide either city or both latitude and longitude").text

    data = await fetch_daily(float(latitude), float(longitude), int(days))
    return TextContent(text=httpx.dumps_json({
        "city": city,
        "coords": {"lat": latitude, "lon": longitude},
        "days": days,
        "forecast": data.get("daily", data)
    }, indent=2)).text


async def amain_stdio() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Weather Server")
    parser.add_argument("--stdio", action="store_true", help="Run as stdio MCP server")
    args = parser.parse_args()

    if args.stdio:
        asyncio.run(amain_stdio())
        return 0

    print("Use --stdio to run the MCP server over stdio.")
    print("Configure your client with .mcp.json as shown in this file's docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
