#!/bin/bash

# Скрипт для безопасного слияния ветки в main
# Использование: ./merge_to_main.sh [имя_ветки]

set -e  # Выход при любой ошибке

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Получаем имя ветки из аргумента или используем текущую
if [ -n "$1" ]; then
    BRANCH_NAME="$1"
else
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
fi

echo -e "${GREEN}🚀 Начало процесса слияния ветки '$BRANCH_NAME' в main...${NC}"

# 1. Обновляем список удаленных веток
echo -e "${YELLOW}📡 Получение актуального списка веток из origin...${NC}"
git fetch origin

# 2. Проверяем, существует ли ветка на сервере
if ! git ls-remote --exit-code --heads origin "$BRANCH_NAME" > /dev/null; then
    echo -e "${RED}❌ Ошибка: Ветка '$BRANCH_NAME' не найдена на удаленном сервере (origin).${NC}"
    echo "Проверьте название ветки на GitHub."
    exit 1
fi

# 3. Создаем или обновляем локальную ветку из удаленной
# Это критический шаг, которого не хватало в старом скрипте
echo -e "📥 Синхронизация локальной ветки '$BRANCH_NAME' с origin..."
if git show-ref --verify --quiet refs/heads/"$BRANCH_NAME"; then
    # Если ветка есть локально, просто подтягиваем изменения
    git checkout "$BRANCH_NAME"
    git reset --hard origin/"$BRANCH_NAME"
else
    # Если нет, создаем её
    git checkout -b "$BRANCH_NAME" origin/"$BRANCH_NAME"
fi

# 4. Переключаемся на main и обновляем его
echo -e "🔄 Переключение на ветку 'main'..."
git checkout main

echo -e "📥 Обновление local main из origin/main..."
git reset --hard origin/main

# 5. Выполняем слияние
echo -e "🔀 Слияние '$BRANCH_NAME' в 'main'..."
# Используем стратегию, которая лучше обрабатывает конфликты
if ! git merge "$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into main"; then
    echo -e "${RED}⚠️ Возникли конфликты при слиянии!${NC}"
    echo "Разрешите конфликты вручную, затем выполните:"
    echo "   git add <файлы>"
    echo "   git commit"
    echo "   git push origin main"
    exit 1
fi

# 6. Отправляем результат на сервер
echo -e "⬆️ Пуш изменений в origin/main..."
git push origin main

echo -e "${GREEN}✅ Успешно! Ветка '$BRANCH_NAME' слита в main.${NC}"
echo -e "${GREEN}🎉 Готово!${NC}"
