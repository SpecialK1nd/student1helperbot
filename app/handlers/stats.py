"""
stats.py
/stats — сводная статистика пользователя.
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.db import count_notes, get_quiz_stats
from app.utils.text import join_lines


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = int(update.effective_user.id) if update.effective_user else 0

    notes_cnt = count_notes(context.application.bot_data["db_path"], user_id)
    qs = get_quiz_stats(context.application.bot_data["db_path"], user_id)

    quizzes = int(qs["quizzes_total"])
    questions = int(qs["questions_total"])
    correct = int(qs["correct_total"])
    last_topic = qs.get("last_topic")

    accuracy = round((correct / questions) * 100, 1) if questions else 0.0

    text = join_lines(
        [
            "Твоя статистика:",
            f"Заметок: {notes_cnt}",
            f"Викторин пройдено: {quizzes}",
            f"Вопросов всего: {questions}",
            f"Правильных ответов: {correct}",
            f"Точность: {accuracy}%",
            f"Последняя тема: {last_topic if last_topic else '—'}",
        ]
    )
    await update.message.reply_text(text)

