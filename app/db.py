"""
db.py
SQLite-хранилище:
- notes: заметки пользователя;
- quiz_stats: статистика по викторинам.

Все функции максимально простые и прозрачные для учебного проекта.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional


def get_conn(db_path: Path) -> sqlite3.Connection:
    # check_same_thread=False позволяет безопаснее работать с SQLite в контексте бота,
    # где колбэки могут быть асинхронными (но операции здесь короткие и простые).
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                text TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_stats (
                user_id INTEGER PRIMARY KEY,
                quizzes_total INTEGER NOT NULL,
                questions_total INTEGER NOT NULL,
                correct_total INTEGER NOT NULL,
                last_topic TEXT
            )
            """
        )

        conn.commit()
    finally:
        conn.close()


def add_note(db_path: Path, user_id: int, created_at_iso: str, text: str) -> int:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notes (user_id, created_at, text) VALUES (?, ?, ?)",
            (user_id, created_at_iso, text),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_notes(db_path: Path, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, created_at, text
            FROM notes
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_note(db_path: Path, user_id: int, note_id: int) -> bool:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM notes WHERE user_id = ? AND id = ?",
            (user_id, note_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def count_notes(db_path: Path, user_id: int) -> int:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM notes WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return int(row["c"]) if row else 0
    finally:
        conn.close()


def get_quiz_stats(db_path: Path, user_id: int) -> dict[str, Any]:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_id, quizzes_total, questions_total, correct_total, last_topic
            FROM quiz_stats
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return {
                "user_id": user_id,
                "quizzes_total": 0,
                "questions_total": 0,
                "correct_total": 0,
                "last_topic": None,
            }
        return dict(row)
    finally:
        conn.close()


def upsert_quiz_stats(
    db_path: Path,
    user_id: int,
    quizzes_add: int,
    questions_add: int,
    correct_add: int,
    last_topic: Optional[str],
) -> None:
    current = get_quiz_stats(db_path, user_id)

    quizzes_total = int(current["quizzes_total"]) + quizzes_add
    questions_total = int(current["questions_total"]) + questions_add
    correct_total = int(current["correct_total"]) + correct_add

    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO quiz_stats (user_id, quizzes_total, questions_total, correct_total, last_topic)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                quizzes_total = excluded.quizzes_total,
                questions_total = excluded.questions_total,
                correct_total = excluded.correct_total,
                last_topic = excluded.last_topic
            """,
            (user_id, quizzes_total, questions_total, correct_total, last_topic),
        )
        conn.commit()
    finally:
        conn.close()

