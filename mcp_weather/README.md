# MCP Weather

Simple weather toolkit providing:
- MCP server exposing tools (search_city, get_weather, get_hourly_forecast, get_daily_forecast)
- FastAPI app to test endpoints locally
- A small client to call the API

No API key required (uses Open-Meteo services).

## Install

If not already installed in your env:

```
pip install fastapi uvicorn httpx
```

(If you want to run MCP tools directly and your client requires the Python MCP package, install it too.)

## FastAPI

Run the API:

```
uvicorn mcp_weather.api:app --reload --port 8000
```

Endpoints:
- GET /health
- GET /weather?city=Berlin
- GET /weather/coords?lat=52.52&lon=13.41
- GET /forecast/hourly?city=Berlin&hours=24
- GET /forecast/daily?city=Berlin&days=3

Example client:

```
python -m mcp_weather.client --city "Berlin" --lat 52.52 --lon 13.41
```

## MCP Server

Config (.mcp.json):

```
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["-m", "mcp_weather.server", "--stdio"]
    }
  }
}
```

Run the server (stdio):

```
python -m mcp_weather.server --stdio
```

Tools exposed:
- search_city(query: str)
- get_weather(city?: str, latitude?: float, longitude?: float)
- get_hourly_forecast(city?: str, latitude?: float, longitude?: float, hours?: int=24)
- get_daily_forecast(city?: str, latitude?: float, longitude?: float, days?: int=3)

## Tests

- FastAPI endpoints: `pytest -q tests/test_weather_api.py`
- MCP tools (skips if MCP package not available): `pytest -q tests/test_mcp_tools.py`
