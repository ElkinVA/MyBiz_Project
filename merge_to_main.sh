
# Скрипт для автоматического слияния всех веток репозитория в main
# Автоматически скачивает репозиторий, получает все ветки и сливает их в main
# Бинарные файлы (db.sqlite3) автоматически разрешаются в пользу текущей версии main

set -e  # Выход при критической ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Автоматическое слияние всех веток в main${NC}"
echo -e "${BLUE}========================================${NC}"

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git не установлен. Пожалуйста, установите git.${NC}"
    exit 1
fi

# Проверка наличия репозитория
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Текущая директория не является git-репозиторием.${NC}"
    exit 1
fi

# Получаем имя основной ветки (main или master)
MAIN_BRANCH="main"
if ! git show-ref --verify --quiet refs/heads/main; then
    if git show-ref --verify --quiet refs/heads/master; then
        MAIN_BRANCH="master"
        echo -e "${YELLOW}⚠️  Ветка 'main' не найдена, используем 'master'${NC}"
    else
        echo -e "${RED}❌ Не найдена основная ветка (main/master). Создаю 'main'...${NC}"
        git checkout -b main
        MAIN_BRANCH="main"
    fi
fi

echo -e "${GREEN}✅ Основная ветка: $MAIN_BRANCH${NC}"

# Fetch всех изменений из origin
echo -e "${BLUE}📡 Получение всех изменений из origin...${NC}"
git fetch origin --prune

# Сохраняем текущую ветку для возврата в конце
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Переключаемся на основную ветку
echo -e "${BLUE}📥 Переключение на ветку '$MAIN_BRANCH'...${NC}"
git checkout "$MAIN_BRANCH"

# Сбрасываем локальные изменения в db.sqlite3 перед началом
if ! git diff --quiet HEAD -- db.sqlite3 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Обнаружены локальные изменения в db.sqlite3. Отменяем их...${NC}"
    git checkout HEAD -- db.sqlite3
fi

# Обновляем основную ветку до актуального состояния origin
echo -e "${BLUE}🔄 Обновление $MAIN_BRANCH до origin/$MAIN_BRANCH...${NC}"
git reset --hard origin/"$MAIN_BRANCH"

# Получаем список всех удаленных веток, исключая основную ветку и HEAD
echo -e "${BLUE}🔍 Поиск всех веток для слияния...${NC}"
BRANCHES_TO_MERGE=$(git branch -r | grep -v "\->" | grep -v "origin/$MAIN_BRANCH$" | grep -v "origin/HEAD" | sed 's/origin\///' | sort -u)

if [ -z "$BRANCHES_TO_MERGE" ]; then
    echo -e "${GREEN}✅ Нет веток для слияния. Все ветки уже объединены или отсутствуют.${NC}"
    echo -e "${BLUE}🎉 Процесс завершен!${NC}"
    # Возвращаемся на исходную ветку
    if [ "$ORIGINAL_BRANCH" != "$MAIN_BRANCH" ]; then
        git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
    fi
    exit 0
fi

echo -e "${GREEN}📋 Найдено веток для слияния: $(echo "$BRANCHES_TO_MERGE" | wc -l | tr -d ' ')${NC}"
echo "$BRANCHES_TO_MERGE" | while read branch; do
    echo -e "   • $branch"
done

# Счетчики
SUCCESS_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

# Проходим по каждой ветке и сливаем её в main
for BRANCH_NAME in $BRANCHES_TO_MERGE; do
    echo -e "\n${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}🔀 Слияние ветки '$BRANCH_NAME' в '$MAIN_BRANCH'...${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
    
    # Проверяем, существует ли ветка в origin
    if ! git ls-remote --exit-code origin "refs/heads/$BRANCH_NAME" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ветка '$BRANCH_NAME' не найдена в origin. Пропускаем...${NC}"
        ((SKIP_COUNT++))
        continue
    fi
    
    # Пытаемся слить ветку
    MERGE_SUCCESS=false
    
    # Сначала пробуем обычное слияние с стратегией ours для текстовых файлов
    if git merge origin/"$BRANCH_NAME" -m "Merge branch '$BRANCH_NAME' into $MAIN_BRANCH" -X ours --no-commit 2>/dev/null; then
        MERGE_SUCCESS=true
    else
        # Если было обычное слияние с конфликтами (но не критическая ошибка)
        if git rev-parse --verify MERGE_HEAD >/dev/null 2>&1; then
            MERGE_SUCCESS=true
        fi
    fi
    
    # Разрешаем конфликты в бинарных файлах (особенно db.sqlite3)
    if [ -f db.sqlite3 ]; then
        # Проверяем, есть ли маркеры конфликта в файле
        if grep -q "^<<<<<<< " db.sqlite3 2>/dev/null || grep -q "^=======$" db.sqlite3 2>/dev/null || grep -q "^>>>>>>> " db.sqlite3 2>/dev/null; then
            echo -e "${YELLOW}⚠️  Конфликт в db.sqlite3. Используем версию из $MAIN_BRANCH...${NC}"
            git checkout HEAD -- db.sqlite3
        fi
    fi
    
    # Проверяем другие потенциально проблемные бинарные файлы
    for binary_file in "*.db" "*.sqlite" "*.sqlite3" "*.bin" "*.dat"; do
        if git ls-files --error-unmatch $binary_file 2>/dev/null; then
            for file in $binary_file; do
                if [ -f "$file" ] && grep -q "^<<<<<<< " "$file" 2>/dev/null; then
                    echo -e "${YELLOW}⚠️  Конфликт в бинарном файле '$file'. Используем версию из $MAIN_BRANCH...${NC}"
                    git checkout HEAD -- "$file"
                fi
            done
        fi
    done
    
    # Завершаем коммит, если слияние успешно или есть незавершенное слияние
    if [ "$MERGE_SUCCESS" = true ] && git rev-parse --verify MERGE_HEAD >/dev/null 2>&1; then
        # Добавляем все разрешенные файлы
        git add -A
        
        # Завершаем коммит
        if git commit -m "Merge branch '$BRANCH_NAME' into $MAIN_BRANCH (auto-merged)"; then
            echo -e "${GREEN}✅ Ветка '$BRANCH_NAME' успешно слита в '$MAIN_BRANCH'${NC}"
            ((SUCCESS_COUNT++))
        else
            echo -e "${RED}❌ Ошибка при завершении коммита для ветки '$BRANCH_NAME'${NC}"
            # Отменяем слияние при ошибке
            git merge --abort 2>/dev/null || true
            ((ERROR_COUNT++))
        fi
    elif git rev-parse --verify MERGE_HEAD >/dev/null 2>&1; then
        # Если слияние не удалось, но есть MERGE_HEAD - отменяем
        echo -e "${YELLOW}⚠️  Слияние ветки '$BRANCH_NAME' прервано. Отменяем...${NC}"
        git merge --abort 2>/dev/null || true
        ((SKIP_COUNT++))
    else
        # Если слияние не потребовалось (ветки идентичны)
        echo -e "${GREEN}✅ Ветка '$BRANCH_NAME' уже включена в '$MAIN_BRANCH' или не требует слияния${NC}"
        ((SKIP_COUNT++))
    fi
done

# Возвращаемся к исходному состоянию db.sqlite3 если нужно
echo -e "\n${BLUE}📊 Итоги слияния:${NC}"
echo -e "   ${GREEN}✅ Успешно слито: $SUCCESS_COUNT${NC}"
echo -e "   ${YELLOW}⚠️  Пропущено/не требовалось: $SKIP_COUNT${NC}"
echo -e "   ${RED}❌ Ошибок: $ERROR_COUNT${NC}"

# Push изменений в origin, только если были успешные слияния
if [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "\n${BLUE}⬆️ Пуш изменений в origin/$MAIN_BRANCH...${NC}"
    if git push origin "$MAIN_BRANCH"; then
        echo -e "${GREEN}✅ Изменения успешно отправлены на сервер${NC}"
    else
        echo -e "${RED}❌ Ошибка при пуше в origin. Возможно, требуются дополнительные права или есть конфликты на сервере.${NC}"
        echo -e "${YELLOW}💡 Попробуйте выполнить 'git pull --rebase origin $MAIN_BRANCH' и повторить попытку${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠️  Пуш не выполнен, так как не было успешных слияний${NC}"
fi

# Возвращаемся на исходную ветку
if [ "$ORIGINAL_BRANCH" != "$MAIN_BRANCH" ]; then
    echo -e "\n${BLUE}🔄 Возврат на исходную ветку '$ORIGINAL_BRANCH'...${NC}"
    git checkout "$ORIGINAL_BRANCH" 2>/dev/null || echo -e "${YELLOW}⚠️  Не удалось вернуться на ветку '$ORIGINAL_BRANCH'${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
if [ $ERROR_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 Процесс слияния завершен успешно!${NC}"
else
    echo -e "${YELLOW}⚠️  Процесс завершен с ошибками. Проверьте логи выше.${NC}"
fi
echo -e "${BLUE}========================================${NC}"

# Выход с кодом ошибки, если были ошибки
if [ $ERROR_COUNT -gt 0 ]; then
    exit 1
fi

exit 0
