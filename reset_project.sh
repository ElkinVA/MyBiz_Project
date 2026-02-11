#!/bin/bash
echo "🔄 Полный сброс проекта..."

# Удаляем базу данных
rm -f db.sqlite3

# Удаляем файлы миграций (кроме __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Создаем новые миграции
echo "Создание миграций..."
python manage.py makemigrations

# Применяем миграции
echo "Применение миграций..."
python manage.py migrate

# Создаем суперпользователя
echo "Создание суперпользователя..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@mybiz.ru', 'admin123')" | python manage.py shell

# Инициализируем настройки
echo "Инициализация настроек..."
python manage.py init_settings

echo "✅ Проект пересоздан!"
