FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Отключаем создание .pyc файлов и включаем небуферизованный вывод
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Устанавливаем системные зависимости (нужны для asyncpg и сборки некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Делаем run.sh исполняемым
RUN chmod +x run.sh

# Открываем порт
EXPOSE 8000

# Запускаем через run.sh
CMD ["bash", "./run.sh"]