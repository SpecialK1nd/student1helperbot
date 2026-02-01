"""
text.py
Утилиты для аккуратного вывода текста пользователю.
"""

from __future__ import annotations


def clamp(text: str, max_len: int = 3500) -> str:
    # Telegram имеет ограничения на длину сообщений; обрезаем мягко.
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def join_lines(lines: list[str]) -> str:
    return "\n".join(lines).strip()

