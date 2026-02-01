"""
start_help.py
/start и /help
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.services.quiz_bank import available_topics
from app.utils.text import join_lines


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first = update.effective_user.first_name if update.effective_user else "друг"
    topics = ", ".join(available_topics())

    text = join_lines(
        [
            f"Привет, {user_first}!",
            "",
            "Я Student Helper Bot: заметки, мини-викторины и погода.",
            "",
            "Быстрый старт:",
            "— /note add Купить тетрадь по матану;",
            "— /note list;",
            "— /quiz python;",
            "— /weather Berlin;",
            "— /stats;",
            "",
            f"Темы викторины: {topics}",
            "",
            "Напиши /help, чтобы увидеть все команды.",
        ]
    )
    await update.message.reply_text(text)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topics = ", ".join(available_topics())
    text = join_lines(
        [
            "Команды бота:",
            "",
            "/start — приветствие и инструкция;",
            "/help — список команд;",
            "",
            "/note add <текст> — добавить заметку в БД;",
            "/note list — показать последние 10 заметок;",
            "/note del <id> — удалить заметку по id;",
            "",
            f"/quiz <тема> — мини-викторина (темы: {topics});",
            "/weather <город> — текущая погода (Open-Meteo);",
            "/stats — ваша статистика (заметки + викторины);",
            "",
            "Примеры:",
            "— /note add Сдать отчёт в пятницу;",
            "— /note del 3;",
            "— /quiz history;",
            "— /weather München;",
        ]
    )
    await update.message.reply_text(text)

