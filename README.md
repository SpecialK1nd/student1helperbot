# Student Helper Telegram Bot (Python)

Учебный Telegram-бот: заметки + викторины + погода + статистика.

## Команды
- /start — приветствие;
- /help — справка;
- /note add <текст> — добавить заметку;
- /note list — показать заметки;
- /note del <id> — удалить заметку;
- /quiz <тема> — мини-викторина;
- /weather <город> — погода (Open-Meteo);
- /stats — статистика.

## Запуск
1) Установите Python 3.10+;
2) `pip install -r requirements.txt`;
3) Задайте переменную окружения `BOT_TOKEN`;
4) `python bot.py`.

## Технологии
- python-telegram-bot (async)
- SQLite
- Open-Meteo API (через httpx)
