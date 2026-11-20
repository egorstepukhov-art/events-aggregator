#!/bin/bash
set -e

echo "Ожидание базы данных..."
# Ждем, пока БД поднимется (простая проверка через Python)
python -c "
import time, asyncpg, asyncio, os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('DATABASE_URL', '').replace('postgresql+asyncpg://', 'postgresql://')
async def check():
    for i in range(30):
        try:
            conn = await asyncpg.connect(url)
            await conn.close()
            print('База данных готова!')
            return
        except Exception:
            time.sleep(1)
    raise Exception('База данных не поднялась за 30 секунд')
asyncio.run(check())
"

echo "Применение миграций Alembic..."
alembic upgrade head

echo "Запуск веб-сервера Uvicorn..."
# --host 0.0.0.0 обязателен для доступа извне контейнера
exec uvicorn app.main:app --host 0.0.0.0 --port 8000