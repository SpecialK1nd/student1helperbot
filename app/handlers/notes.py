"""
notes.py
Команда /note с подкомандами add|list|del.

Примеры:
- /note add Купить кофе
- /note list
- /note del 5
"""

from __future__ import annotations

from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from app.db import add_note, delete_note, list_notes
from app.utils.text import join_lines


async def cmd_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # context.args — стандартный способ получить "хвост" команды. :contentReference[oaicite:3]{index=3}
    args = context.args
    if not args:
        await update.message.reply_text(
            "Использование:\n"
            "/note add <текст>\n"
            "/note list\n"
            "/note del <id>"
        )
        return

    sub = args[0].strip().lower()
    user_id = int(update.effective_user.id) if update.effective_user else 0

    if sub == "add":
        text = " ".join(args[1:]).strip()
        if not text:
            await update.message.reply_text("Добавление заметки: /note add <текст>")
            return

        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        note_id = add_note(context.application.bot_data["db_path"], user_id, created_at, text)

        await update.message.reply_text(f"Заметка добавлена: id={note_id}")
        return

    if sub == "list":
        notes = list_notes(context.application.bot_data["db_path"], user_id, limit=10)
        if not notes:
            await update.message.reply_text("Заметок пока нет. Добавь: /note add <текст>")
            return

        lines = ["Последние заметки:"]
        for n in notes:
            lines.append(f'{n["id"]}) {n["text"]}  [{n["created_at"]}]')

        await update.message.reply_text(join_lines(lines))
        return

    if sub == "del":
        if len(args) < 2:
            await update.message.reply_text("Удаление: /note del <id>")
            return
        try:
            note_id = int(args[1])
        except ValueError:
            await update.message.reply_text("id должен быть числом. Пример: /note del 3")
            return

        ok = delete_note(context.application.bot_data["db_path"], user_id, note_id)
        await update.message.reply_text("Удалено." if ok else "Не найдено (проверь id).")
        return

    await update.message.reply_text("Неизвестная подкоманда. Используй: add, list или del.")

