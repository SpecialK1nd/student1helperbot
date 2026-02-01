"""
bot.py
Точка входа проекта.

Собираем Application (python-telegram-bot async),
подключаем команды и запускаем polling.
"""

from __future__ import annotations

import logging

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from config import load_settings
from app.db import init_db
from app.handlers.start_help import cmd_start, cmd_help
from app.handlers.notes import cmd_note
from app.handlers.weather import cmd_weather
from app.handlers.stats import cmd_stats
from app.handlers.quiz import cmd_quiz, on_text_quiz_router


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        level=logging.INFO,
    )

    settings = load_settings()

    # Инициализация БД
    init_db(settings.db_path)

    # ApplicationBuilder — рекомендуемый способ сборки приложения. :contentReference[oaicite:4]{index=4}
    app = ApplicationBuilder().token(settings.bot_token).build()

    # Общие данные приложения (доступны из context.application.bot_data)
    app.bot_data["db_path"] = settings.db_path
    app.bot_data["http_timeout_sec"] = settings.http_timeout_sec

    # Команды
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("weather", cmd_weather))
    app.add_handler(CommandHandler("quiz", cmd_quiz))
    app.add_handler(CommandHandler("stats", cmd_stats))

    # Роутер для текстовых ответов викторины (срабатывает только когда user_data["quiz_waiting"]=True)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_quiz_router))

    # Запуск
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()

