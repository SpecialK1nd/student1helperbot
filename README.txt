Название: Student Helper Telegram Bot

Структура проекта:
1) bot.py
   Точка входа. Создает Application, подключает хендлеры, запускает polling.

2) config.py
   Читает переменные окружения (BOT_TOKEN), задает настройки и пути.

3) app/db.py
   Инициализация SQLite, создание таблиц, функции для работы с БД.

4) app/models.py
   Простые структуры данных/константы (при необходимости расширения).

5) app/handlers/
   start_help.py  - /start, /help
   notes.py       - /note add|list|del (SQLite)
   quiz.py        - /quiz (случайные вопросы, учет статистики)
   weather.py     - /weather (Open-Meteo API, обработка ошибок)
   stats.py       - /stats (сводная статистика пользователя)

6) app/services/
   quiz_bank.py   - банк вопросов, генерация викторины по теме
   open_meteo.py  - запрос геокодинга и прогноза (HTTP)

7) app/utils/text.py
   Утилиты форматирования текста (экранирование, аккуратные сообщения).

Как добавить новую команду:
- Создать файл в app/handlers/;
- Описать CommandHandler и callback;
- Подключить handler в bot.py.

