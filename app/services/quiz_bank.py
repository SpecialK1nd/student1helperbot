"""
quiz_bank.py
Банк вопросов для /quiz. Можно расширять темами.

Логика:
- Пользователь пишет /quiz <тема>
- Бот выбирает случайные вопросы по теме и задает их подряд
- Ответы проверяются (с небольшой нормализацией)
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class QuizQuestion:
    question: str
    answers: set[str]  # набор допустимых ответов (в нижнем регистре)


QUIZ_BANK: dict[str, list[QuizQuestion]] = {
    "python": [
        QuizQuestion("Как называется структура данных {1, 2, 3} в Python?", {"set", "множество"}),
        QuizQuestion("Какой оператор используется для создания функции?", {"def"}),
        QuizQuestion("Как называется ошибка деления на ноль?", {"zerodivisionerror", "zero division error"}),
        QuizQuestion("Какой тип у значения True?", {"bool", "boolean"}),
        QuizQuestion("Как открыть файл для чтения?", {"open", "open()"}),
    ],
    "math": [
        QuizQuestion("Чему равна производная x^2?", {"2x", "2*x"}),
        QuizQuestion("Сколько градусов в развернутом угле?", {"180"}),
        QuizQuestion("Как называется число, делящееся только на 1 и на себя?", {"простое", "простое число", "prime"}),
        QuizQuestion("Чему равно 7*8?", {"56"}),
        QuizQuestion("Как называется корень квадратного уравнения?", {"корень", "roots", "root"}),
    ],
    "history": [
        QuizQuestion("В каком году началась Вторая мировая война?", {"1939"}),
        QuizQuestion("Столица Франции?", {"париж", "paris"}),
        QuizQuestion("Кто был первым человеком в космосе (фамилия)?", {"гагарин", "gagarin"}),
        QuizQuestion("В каком году распался СССР?", {"1991"}),
        QuizQuestion("Как назывался древнеримский амфитеатр в Риме?", {"колизей", "colosseum", "coliseum"}),
    ],
}


def normalize(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalnum() or ch in {"*", "^"})


def available_topics() -> list[str]:
    return sorted(QUIZ_BANK.keys())


def pick_questions(topic: str, count: int = 3) -> list[QuizQuestion]:
    key = topic.strip().lower()
    if key not in QUIZ_BANK:
        return []
    questions = QUIZ_BANK[key][:]
    random.shuffle(questions)
    return questions[: max(1, min(count, len(questions)))]


def check_answer(q: QuizQuestion, user_answer: str) -> bool:
    ua = normalize(user_answer)
    for a in q.answers:
        if ua == normalize(a):
            return True
    return False

