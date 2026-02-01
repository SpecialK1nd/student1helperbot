"""
quiz.py
/quiz <topic>

Логика:
- Выбираем 3 случайных вопроса по теме;
- Задаем по очереди;
- Ждем текстовый ответ на каждый вопрос (через await bot);
- Считаем правильные;
- Записываем статистику в SQLite.
"""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.db import upsert_quiz_stats
from app.services.quiz_bank import available_topics, pick_questions, check_answer
from app.utils.text import join_lines


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if not args:
        topics = ", ".join(available_topics())
        await update.message.reply_text(f"Укажи тему: /quiz <тема>\nДоступно: {topics}")
        return

    topic = args[0].strip().lower()
    questions = pick_questions(topic, count=3)
    if not questions:
        topics = ", ".join(available_topics())
        await update.message.reply_text(f"Не знаю такую тему.\nДоступно: {topics}")
        return

    user_id = int(update.effective_user.id) if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        await update.message.reply_text("Не удалось определить чат.")
        return

    await update.message.reply_text(
        f"Викторина по теме: {topic}\n"
        "Отвечай обычным сообщением. Чтобы остановиться — напиши: стоп"
    )

    correct = 0
    total = len(questions)

    for i, q in enumerate(questions, start=1):
        await update.message.reply_text(f"Вопрос {i}/{total}: {q.question}")

        # Ждем следующий текст от этого же пользователя в этом же чате.
        # PTB не дает "из коробки" await next message одним вызовом,
        # поэтому используем ConversationHandler? Можно, но для учебности проще так:
        # мы включим режим "ожидания" через bot_data + MessageHandler в quiz-router.
        #
        # Чтобы не усложнять архитектуру, реализуем мини-диалог через application.user_data:
        # user_data хранит состояние между апдейтами.
        context.user_data["quiz_waiting"] = True
        context.user_data["quiz_expected_answers"] = q.answers
        context.user_data["quiz_topic"] = topic

        # Сигнализируем главному циклу: ожидаем ответ.
        # Дальше управление перейдет в handler on_text_quiz_router.
        # Мы просто выходим: дальнейшие шаги викторины продолжатся там.
        context.user_data["quiz_queue"] = context.user_data.get("quiz_queue", [])
        context.user_data["quiz_queue"].append(
            {"question": q.question, "answers": list(q.answers)}
        )

        # Важно: прерываем здесь, а продолжение идет в роутере.
        # Чтобы пользователь не получал сразу все вопросы подряд.
        return

    # До сюда в текущей реализации не дойдем (вопросы идут через роутер).
    # Оставлено как пояснение для расширения.
    _ = correct

