# Events Aggregator

Backend-сервис на Python (FastAPI), который агрегирует данные из внешнего Events Provider API. 
Сервис кэширует события в локальной базе данных (PostgreSQL), предоставляет удобную пагинацию, фильтрацию и валидацию, а также фоновую синхронизацию.

## Технологический стек

- Python 3.9+ (тестировалось на 3.12)
- FastAPI
- PostgreSQL
- SQLAlchemy (async) + asyncpg
- Alembic (миграции)
- httpx (клиент внешнего API)
- ruff (линтер)

## Запуск проекта

1. **Клонируйте репозиторий и перейдите в папку:**
   ```bash
   git clone <URL_репозитория>
   cd events-aggregator
   
1. **Клонируйте репозиторий и перейдите в папку:**
   ```bash
   git clone <URL_репозитория>
   cd events-aggregator
   
2. **Создайте и активируйте виртуальное окружение:**
   ```bash
     python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
3. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt

4. **Настройте переменные окружения:**
Скопируйте .env.example в .env и заполните данные:

    ```bash
    cp .env.example .env
Необходимо указать строку подключения к БД (DATABASE_URL) и ваш API-ключ из LMS (EVENTS_PROVIDER_API_KEY).

5. **Запустите PostgreSQL:**
Если базы нет, можно поднять её в Docker:

    ```bash
    docker run --name events-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=events_db -p 5432:5432 -d postgres:16

6. **Примените миграции:**

    ```bash
    alembic upgrade head

7. **Запустите сервер:**

    ```bash
    uvicorn app.main:app --reload
   
Приложение будет доступно по адресу: http://127.0.0.1:8000.
Swagger-документация: http://127.0.0.1:8000/docs

Реализованные эндпоинты
Метод	Путь	Описание
GET	/api/health	Проверка доступности сервиса
GET	/api/events	Получение списка событий (пагинация, date_from)
GET	/api/events/{event_id}	Получение деталей события
GET	/api/events/{event_id}/seats	Получение свободных мест (кэш 30 сек)
POST	/api/tickets	Регистрация на мероприятие
DELETE	/api/tickets/{ticket_id}	Отмена регистрации
POST	/api/sync/trigger	Ручной запуск синхронизации событий

Фоновая синхронизация
В сервисе реализован фоновый процесс (worker), который запускается вместе с приложением и синхронизирует события раз в 24 часа (интервал настраивается через SYNC_INTERVAL_HOURS).
Первая синхронизация загружает все события, последующие — только измененные (через параметр changed_at).

Линтер и тесты
В проекте настроен линтер ruff и тесты на pytest.


Запуск линтера:

   ruff check .

Запуск тестов (мокают запросы к внешнему API через unittest.mock):

pytest -v
CI/CD
Настроен GitHub Actions (.github/workflows/ci.yml).
При каждом пуше запускается проверка линтером (ruff check) и тестами (pytest). Шаг деплоя (в текущей реализации — заглушка) запускается строго после успешного прохождения линтера и тестов (needs: lint-and-test).
