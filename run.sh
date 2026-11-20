#!/bin/bash
set -e

echo "Ожидание базы данных..."
# Вызываем python, чтобы он сам собрал строку подключения через наш config.py
python -c "
import asyncio
import asyncpg
from app.config import get_settings

async def check():
    settings = get_settings()
    # Убираем префикс драйвера, так как asyncpg.connect его не понимает
    db_url = settings.db_url.replace('postgresql+asyncpg://', 'postgresql://')

    for i in range(30):
        try:
            conn = await asyncpg.connect(db_url)
            await conn.close()
            print('База данных готова!')
            return
        except Exception as e:
            print(f'Ошибка подключения: {e}. Ждем...')
            await asyncio.sleep(2)
    raise Exception('База данных не поднялась за 60 секунд')

asyncio.run(check())
"

echo "Применение миграций Alembic..."
alembic upgrade head

echo "Запуск веб-сервера Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000