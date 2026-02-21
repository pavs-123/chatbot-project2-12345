"""
Simple client to test the local FastAPI weather service.

Usage:
  python -m mcp_weather.client --city "Berlin" --lat 52.52 --lon 13.41 --host 127.0.0.1 --port 8000

It will:
  - Check /health
  - Query /weather?city=...
  - Query /weather/coords?lat=...&lon=...
"""
from __future__ import annotations
import argparse
import asyncio
from typing import Any, Dict
import httpx


async def main() -> int:
    p = argparse.ArgumentParser(description="Weather API test client")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--city", default="Berlin")
    p.add_argument("--lat", type=float, default=52.52)
    p.add_argument("--lon", type=float, default=13.41)
    args = p.parse_args()

    base = f"http://{args.host}:{args.port}"
    async with httpx.AsyncClient(timeout=10) as client:
        # Wait for server with retries
        import asyncio as _asyncio
        for _ in range(10):
            try:
                r = await client.get(f"{base}/health")
                r.raise_for_status()
                break
            except Exception:
                await _asyncio.sleep(0.5)
        else:
            # One last try to raise
            r = await client.get(f"{base}/health")
            r.raise_for_status()
        print("/health:", r.json())

        # City
        r = await client.get(f"{base}/weather", params={"city": args.city})
        if r.status_code == 200:
            print(f"/weather?city={args.city}:", r.json())
        else:
            print(f"/weather?city={args.city} status:", r.status_code, r.text)

        # Coords
        r = await client.get(f"{base}/weather/coords", params={"lat": args.lat, "lon": args.lon})
        if r.status_code == 200:
            print(f"/weather/coords lat={args.lat} lon={args.lon}:", r.json())
        else:
            print(f"/weather/coords status:", r.status_code, r.text)

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
