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
async def on_text_quiz_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Роутер, который ловит обычные текстовые сообщения, когда пользователь в режиме викторины.
    Держит очередь вопросов в user_data и по одному задает следующий.
    """

    if not update.message or not update.message.text:
        return

    # Если пользователь не в режиме викторины — игнорируем.
    if not context.user_data.get("quiz_waiting"):
        return

    text = update.message.text.strip()
    if text.lower() in {"стоп", "stop", "cancel"}:
        # Сбрасываем состояние.
        context.user_data.pop("quiz_waiting", None)
        context.user_data.pop("quiz_queue", None)
        context.user_data.pop("quiz_score", None)
        context.user_data.pop("quiz_total", None)
        context.user_data.pop("quiz_topic", None)
        await update.message.reply_text("Ок, остановил викторину.")
        return

    # Восстановим текущий вопрос из очереди:
    queue = context.user_data.get("quiz_queue") or []
    if not queue:
        # Нечего обрабатывать — сбрасываем.
        context.user_data.pop("quiz_waiting", None)
        await update.message.reply_text("Похоже, викторина уже завершена. Запусти заново: /quiz <тема>")
        return

    current = queue[0]
    answers = set(a.lower() for a in current.get("answers", []))

    # Инициализируем счетчики, если их еще нет:
    if "quiz_score" not in context.user_data:
        context.user_data["quiz_score"] = 0
    if "quiz_total" not in context.user_data:
        context.user_data["quiz_total"] = len(queue)

    # Проверка ответа:
    from app.services.quiz_bank import QuizQuestion  # локальный импорт, чтобы файл был самостоятельным
    q_obj = QuizQuestion(question=current.get("question", ""), answers=answers)

    is_ok = check_answer(q_obj, text)
    if is_ok:
        context.user_data["quiz_score"] += 1
        await update.message.reply_text("Верно ✅")
    else:
        # Покажем 1 “эталонный” ответ, чтобы не спамить списком.
        example = next(iter(answers)) if answers else "—"
        await update.message.reply_text(f"Не совсем ❌ Пример правильного ответа: {example}")

    # Убираем текущий вопрос из очереди:
    queue.pop(0)
    context.user_data["quiz_queue"] = queue

    # Если вопросы закончились — подводим итог и пишем статистику:
    if not queue:
        score = int(context.user_data.get("quiz_score", 0))
        total = int(context.user_data.get("quiz_total", 0))
        topic = str(context.user_data.get("quiz_topic", "")) or None

        user_id = int(update.effective_user.id) if update.effective_user else 0

        upsert_quiz_stats(
            context.application.bot_data["db_path"],
            user_id=user_id,
            quizzes_add=1,
            questions_add=total,
            correct_add=score,
            last_topic=topic,
        )

        percent = round((score / total) * 100, 1) if total else 0.0
        await update.message.reply_text(
            join_lines(
                [
                    "Викторина завершена!",
                    f"Результат: {score}/{total} ({percent}%)",
                    "Статистика обновлена. Посмотри: /stats",
                ]
            )
        )

        # Сбрасываем состояние:
        context.user_data.pop("quiz_waiting", None)
        context.user_data.pop("quiz_queue", None)
        context.user_data.pop("quiz_score", None)
        context.user_data.pop("quiz_total", None)
        context.user_data.pop("quiz_topic", None)
        return

    # Иначе задаем следующий вопрос:
    next_q = queue[0]
    idx_done = int(context.user_data.get("quiz_total", 0)) - len(queue)
    total = int(context.user_data.get("quiz_total", 0))
    await update.message.reply_text(f"Вопрос {idx_done + 1}/{total}: {next_q.get('question', '')}")

