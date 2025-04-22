#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Ожидание доступности базы данных PostgreSQL..."

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; do
  echo "БД ещё не готова — ждём 1 секунду..."
  sleep 1
done

echo "База данных готова!"

if [ -n "${REDIS_HOST:-}" ]; then
  echo "⏳ Ожидаем доступность Redis..."
  until nc -z "$REDIS_HOST" 6379; do
    echo "Redis ещё не готов — ждём 1 секунду..."
    sleep 1
  done
  echo "Redis готов!"
fi

echo "Выполнение миграций..."
python manage.py migrate

echo "Запуск Django сервера..."
python manage.py runserver 0.0.0.0:8000
