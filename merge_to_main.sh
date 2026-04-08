#!/bin/bash

# Скрипт для слияния текущей ветки с main и пуша в origin
# Использование: ./merge_to_main.sh [имя_ветки]
# Если имя ветки не указано, используется текущая ветка

set -e  # Выход при ошибке

# Получаем имя текущей ветки
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Если передан аргумент, используем его как имя ветки
if [ -n "$1" ]; then
    BRANCH_NAME="$1"
else
    BRANCH_NAME="$CURRENT_BRANCH"
fi

echo "🚀 Начало процесса слияния ветки '$BRANCH_NAME' в main..."

# Проверяем, есть ли локальная ветка main
if ! git show-ref --verify --quiet refs/heads/main; then
    echo "❌ Локальная ветка 'main' не найдена. Создаю её из origin/main..."
    git checkout -b main origin/main
else
    echo "✅ Локальная ветка 'main' найдена."
fi

# Переключаемся на main
echo "📥 Переключение на ветку 'main'..."
git checkout main

# Fetch изменений из origin
echo "📡 Получение изменений из origin..."
git fetch origin

# Merge ветки в main
echo "🔀 Слияние ветки '$BRANCH_NAME' в 'main'..."
git merge origin/"$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into main"

# Push изменений в origin/main
echo "⬆️ Пуш изменений в origin/main..."
git push origin main

echo "✅ Успешно! Ветка '$BRANCH_NAME' слита в main и отправлена на сервер."
echo "🎉 Готово!"
