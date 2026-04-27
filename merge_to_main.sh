#!/bin/bash

# merge_to_main.sh
# Назначение: Автоматическое слияние НОВОЙ ветки из GitHub в main.
# Логика:
# 1. Если передан аргумент (имя ветки) -> сливаем именно её.
# 2. Если аргумента нет -> ищем самую свежую ветку в origin, которую еще не слили в main.

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "🚀 Слияние новой ветки с GitHub в main"
echo "========================================="

# 1. Проверка текущей ветки и подтягивание изменений
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${YELLOW}⚠️ Вы не на ветке main. Переключаемся...${NC}"
    git checkout main
fi

echo -e "${BLUE}📡 Получение последних изменений из GitHub...${NC}"
git fetch origin --prune

# Обновляем локальный main до состояния удаленного
git reset --hard origin/main

# 2. Определение целевой ветки для слияния
TARGET_BRANCH=""

if [ -n "$1" ]; then
    # Если передан аргумент, используем его
    TARGET_BRANCH="$1"
    echo -e "${GREEN}✅ Используется ветка из аргумента: ${TARGET_BRANCH}${NC}"
else
    # Если аргумента нет, ищем самую свежую нес литую ветку
    echo -e "${BLUE}🔍 Поиск самой свежей ветки для слияния...${NC}"

    # Получаем список всех удаленных веток кроме main/master/head
    # Сортируем их по дате последнего коммита (самые свежие сверху)
    TARGET_BRANCH=$(git branch -r --format='%(refname:lstrip=3)' --sort=-committerdate | grep -v 'HEAD' | grep -v 'main' | grep -v 'master' | head -n 1)

    if [ -z "$TARGET_BRANCH" ]; then
        echo -e "${RED}❌ Ошибка: Не найдено новых веток для слияния.${NC}"
        exit 1
    fi

    # Проверка: уже слита ли эта ветка?
    if git branch --merged main | grep -q "$(echo $TARGET_BRANCH | sed 's/origin\///')"; then
         # Если самая свежая уже слита, пробуем найти следующую нес литую
         FOUND_UNMERGED=false
         for branch in $(git branch -r --format='%(refname:lstrip=3)' --sort=-committerdate | grep -v 'HEAD' | grep -v 'main' | grep -v 'master'); do
             if ! git branch --merged main | grep -qw "$branch"; then
                 TARGET_BRANCH="$branch"
                 FOUND_UNMERGED=true
                 break
             fi
         done

         if [ "$FOUND_UNMERGED" = false ]; then
             echo -e "${GREEN}✨ Все ветки уже слиты в main!${NC}"
             exit 0
         fi
    fi

    echo -e "${GREEN}✅ Найдена ветка для слияния: ${TARGET_BRANCH}${NC}"
fi

# Приводим имя ветки к формату без origin/, если оно вдруг попало
TARGET_BRANCH_CLEAN=$(echo "$TARGET_BRANCH" | sed 's|origin/||')

# 3. Подготовка к слиянию
echo -e "${YELLOW}⚙️ Подготовка базы данных (сброс локальных изменений)...${NC}"
if [ -f "db.sqlite3" ]; then
    git checkout --ours db.sqlite3 2>/dev/null || true
    git add db.sqlite3
    # Не делаем коммит сразу, чтобы не засорять историю, просто возвращаем файл в состояние main
    git checkout HEAD -- db.sqlite3
fi

# 4. Процесс слияния
echo "-----------------------------------------"
echo -e "${BLUE}🔀 Слияние ветки '${TARGET_BRANCH_CLEAN}' в 'main'...${NC}"
echo "-----------------------------------------"

# Пытаемся слить
# Используем стратегию, которая предпочитает наши изменения при конфликтах в текстовых файлах,
# но для бинарных (sqlite) нужно ручное разрешение или выбор одной стороны.
# Здесь мы сначала пытаемся слить, а потом обрабатываем ошибки.

git merge origin/"$TARGET_BRANCH_CLEAN" -m "Merge branch '$TARGET_BRANCH_CLEAN' into main" || {
    echo -e "${RED}⚠️ Возникли конфликты при слиянии.${NC}"

    # Обработка конфликтов в бинарных файлах (db.sqlite3)
    if git diff --name-only --diff-filter=U | grep -q "db.sqlite3"; then
        echo -e "${YELLOW}🗄️ Конфликт в db.sqlite3. Оставляем версию из MAIN (безопасно).${NC}"
        git checkout --ours db.sqlite3
        git add db.sqlite3
    fi

    # Для остальных файлов пытаемся принять "наши" изменения (так как main - это истина после fetch)
    # Или можно принять "их" изменения, если мы хотим полностью взять код из новой ветки.
    # В нашем случае: код из новой ветки важнее, поэтому принимаем "theirs" для кода, "ours" для БД.

    # Получаем список конфликтующих файлов (кроме БД)
    CONFLICT_FILES=$(git diff --name-only --diff-filter=U | grep -v "db.sqlite3" || true)

    if [ -n "$CONFLICT_FILES" ]; then
        echo -e "${YELLOW}📝 Разрешение конфликтов в коде (приоритет новой ветке)...${NC}"
        for file in $CONFLICT_FILES; do
            git checkout --theirs "$file"
            git add "$file"
        done
    fi

    # Завершаем слияние
    git commit -m "Auto-merge: resolved conflicts for $TARGET_BRANCH_CLEAN (code from branch, DB from main)"
}

# 5. Финализация
echo "-----------------------------------------"
echo -e "${GREEN}✅ Слияние успешно завершено!${NC}"
echo -e "${BLUE}📤 Отправка изменений на GitHub...${NC}"

git push origin main

echo "========================================="
echo -e "${GREEN}🎉 Готово! Ветка ${TARGET_BRANCH_CLEAN} слита в main.${NC}"
echo "========================================="

# Возвращаемся на main (на всякий случай)
git checkout main
