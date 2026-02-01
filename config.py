"""
config.py
Конфигурация проекта: токен, пути, таймауты.

Важно:
- Токен Telegram-бота не храним в репозитории.
- Берем токен из переменной окружения BOT_TOKEN.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_helper.sqlite3"


@dataclass(frozen=True)
class Settings:
    bot_token: str
    db_path: Path
    http_timeout_sec: float


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN.\n"
            "Добавьте переменную окружения BOT_TOKEN со значением токена от BotFather, "
            "затем перезапустите терминал/IDE."
        )

    return Settings(
        bot_token=token,
        db_path=DB_PATH,
        http_timeout_sec=10.0,
    )

