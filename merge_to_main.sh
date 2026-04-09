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

# Отменяем локальные изменения в db.sqlite3 (бинарный файл, не подлежит слиянию)
if git diff --quiet HEAD -- db.sqlite3; then
    echo "✅ Файл db.sqlite3 чист."
else
    echo "⚠️  Обнаружены локальные изменения в db.sqlite3. Отменяем их для слияния..."
    git checkout HEAD -- db.sqlite3
fi

# Fetch изменений из origin
echo "📡 Получение изменений из origin..."
git fetch origin

# Merge ветки в main (игнорируем изменения в db.sqlite3 из ветки)
echo "🔀 Слияние ветки '$BRANCH_NAME' в 'main'..."
git merge origin/"$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into main" -X ours --no-commit || true

# Если были конфликты в db.sqlite3, разрешаем их в пользу текущей версии
if [ -f db.sqlite3 ] && grep -q "^<<<<<<< " db.sqlite3 2>/dev/null; then
    echo "⚠️  Конфликт в db.sqlite3. Используем текущую версию..."
    git checkout HEAD -- db.sqlite3
fi

# Завершаем коммит, если он был начат
if git rev-parse --verify MERGE_HEAD >/dev/null 2>&1; then
    git commit -m "Merge branch '$BRANCH_NAME' into main"
fi

# Push изменений в origin/main
echo "⬆️ Пуш изменений в origin/main..."
git push origin main

echo "✅ Успешно! Ветка '$BRANCH_NAME' слита в main и отправлена на сервер."
echo "🎉 Готово!"
