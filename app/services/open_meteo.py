"""
open_meteo.py
Интеграция с Open-Meteo:
- Геокодинг города -> широта/долгота
- Получение текущей погоды

Почему Open-Meteo:
- Бесплатно, без ключа
- Простое API

HTTP-клиент: httpx (async).
"""

from __future__ import annotations

from dataclasses import dataclass
import httpx


@dataclass(frozen=True)
class GeoResult:
    name: str
    country: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class WeatherNow:
    temperature_c: float
    wind_kmh: float
    weather_code: int


WEATHER_CODE_HINTS: dict[int, str] = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Туман (изморось)",
    51: "Морось (слабая)",
    53: "Морось (умеренная)",
    55: "Морось (сильная)",
    61: "Дождь (слабый)",
    63: "Дождь (умеренный)",
    65: "Дождь (сильный)",
    71: "Снег (слабый)",
    73: "Снег (умеренный)",
    75: "Снег (сильный)",
    80: "Ливень (слабый)",
    81: "Ливень (умеренный)",
    82: "Ливень (сильный)",
    95: "Гроза",
}


async def geocode_city(client: httpx.AsyncClient, city: str) -> GeoResult | None:
    city = city.strip()
    if not city:
        return None

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru", "format": "json"}

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    results = data.get("results") or []
    if not results:
        return None

    item = results[0]
    return GeoResult(
        name=str(item.get("name", city)),
        country=str(item.get("country", "")),
        latitude=float(item["latitude"]),
        longitude=float(item["longitude"]),
    )


async def get_weather_now(client: httpx.AsyncClient, lat: float, lon: float) -> WeatherNow:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "wind_speed_unit": "kmh",
        "temperature_unit": "celsius",
    }

    r = await client.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    cw = data.get("current_weather") or {}
    return WeatherNow(
        temperature_c=float(cw.get("temperature", 0.0)),
        wind_kmh=float(cw.get("windspeed", 0.0)),
        weather_code=int(cw.get("weathercode", -1)),
    )


def describe_weather_code(code: int) -> str:
    return WEATHER_CODE_HINTS.get(code, f"Код погоды: {code}")

