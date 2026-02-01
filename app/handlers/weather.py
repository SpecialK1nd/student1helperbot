"""
weather.py
/weather <город>

Логика:
- Берем город из аргументов;
- Геокодим через Open-Meteo;
- Берем current_weather;
- Форматируем и показываем.
"""

from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from app.services.open_meteo import geocode_city, get_weather_now, describe_weather_code
from app.utils.text import join_lines


async def cmd_weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /weather <город>\nПример: /weather Berlin")
        return

    city = " ".join(args).strip()
    timeout = float(context.application.bot_data.get("http_timeout_sec", 10.0))

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            geo = await geocode_city(client, city)
            if not geo:
                await update.message.reply_text("Не нашёл такой город. Попробуй другой вариант написания.")
                return

            w = await get_weather_now(client, geo.latitude, geo.longitude)
            desc = describe_weather_code(w.weather_code)

            text = join_lines(
                [
                    f"Погода сейчас: {geo.name} ({geo.country})",
                    f"Температура: {w.temperature_c:.1f}°C",
                    f"Ветер: {w.wind_kmh:.1f} км/ч",
                    f"Состояние: {desc}",
                ]
            )
            await update.message.reply_text(text)

        except httpx.HTTPError:
            await update.message.reply_text("Ошибка сети при запросе погоды. Попробуй чуть позже.")
        except Exception:
            await update.message.reply_text("Неожиданная ошибка при обработке погоды.")

