#!/bin/bash

# Скрипт для сбора ВСЕХ файлов проекта MyBiz в один текстовый файл
# Рекурсивно обходит все папки и подпапки

OUTPUT_FILE="full_project_analysis.txt"
LOG_FILE="collection.log"

echo "-== Начало полного сбора файлов проекта MyBiz ==-"
echo "Логирование в: $LOG_FILE"

# Создаем или очищаем выходной файл
> "$OUTPUT_FILE"
> "$LOG_FILE"

echo "=== ПОЛНЫЙ СНИМОК ПРОЕКТА MYBIZ ===" >> "$OUTPUT_FILE"
echo "Дата создания: $(date)" >> "$OUTPUT_FILE"
echo "Полная рекурсивная коллекция всех файлов" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Исключаем некоторые директории и файлы
EXCLUDE_DIRS=(
    ".git"
    "__pycache__"
    ".pytest_cache"
    ".vscode"
    "node_modules"
    "venv"
    "env"
    ".env"
    "staticfiles"
    "media"
)

EXCLUDE_FILES=(
    "*.pyc"
    "*.pyo"
    "*.pyd"
    ".DS_Store"
    "*.db"
    "*.sqlite3"
    "*.log"
    "*.txt"
)

# Создаем строку исключений для find
EXCLUDE_FIND_ARGS=""
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_FIND_ARGS="$EXCLUDE_FIND_ARGS -name $dir -prune -o"
done

# Функция для добавления файла в отчет
add_file() {
    local file_path=$1
    local total_files=$2
    local added_files=$3

    echo "[$added_files/$total_files] Обработка: $file_path" >> "$LOG_FILE"

    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "ФАЙЛ: $file_path" >> "$OUTPUT_FILE"
    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ -f "$file_path" ]; then
        # Проверяем, является ли файл текстовым (не бинарным)
        if file "$file_path" | grep -q "text"; then
            cat "$file_path" >> "$OUTPUT_FILE"
        else
            echo "[БИНАРНЫЙ ФАЙЛ - содержимое не показано]" >> "$OUTPUT_FILE"
        fi
    else
        echo "✗ Файл не найден" >> "$OUTPUT_FILE"
    fi

    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Инициализируем счетчики
TOTAL_FILES=0
ADDED_FILES=0

# Сначала подсчитываем общее количество файлов
echo "Подсчет общего количества файлов..." >> "$LOG_FILE"
while IFS= read -r file; do
    # Пропускаем исключенные файлы
    skip=false
    for pattern in "${EXCLUDE_FILES[@]}"; do
        if [[ "$(basename "$file")" == $pattern ]]; then
            skip=true
            break
        fi
    done

    # Пропускаем сам выходной файл и лог
    if [[ "$file" == "./$OUTPUT_FILE" ]] || [[ "$file" == "./$LOG_FILE" ]]; then
        skip=true
    fi

    if [ "$skip" = false ]; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
    fi
done < <(find . $EXCLUDE_FIND_ARGS -type f -print)

echo "Найдено файлов: $TOTAL_FILES" >> "$LOG_FILE"
echo "Начинаем обработку..." >> "$LOG_FILE"

# Теперь обрабатываем файлы
while IFS= read -r file; do
    # Пропускаем исключенные файлы
    skip=false
    for pattern in "${EXCLUDE_FILES[@]}"; do
        if [[ "$(basename "$file")" == $pattern ]]; then
            skip=true
            break
        fi
    done

    # Пропускаем сам выходной файл и лог
    if [[ "$file" == "./$OUTPUT_FILE" ]] || [[ "$file" == "./$LOG_FILE" ]]; then
        skip=true
    fi

    if [ "$skip" = false ]; then
        ADDED_FILES=$((ADDED_FILES + 1))
        add_file "$file" "$TOTAL_FILES" "$ADDED_FILES"
    fi
done < <(find . $EXCLUDE_FIND_ARGS -type f -print)

echo "=== СТРУКТУРА ПРОЕКТА (дерево директорий) ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
find . $EXCLUDE_FIND_ARGS -type d -print | sort | sed 's|[^/]*/|- |g' >> "$OUTPUT_FILE"

# Добавляем информацию о Python-пакетах
echo "" >> "$OUTPUT_FILE"
echo "=== ИНФОРМАЦИЯ О СРЕДЕ ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Python версия:" >> "$OUTPUT_FILE"
python3 --version 2>> "$OUTPUT_FILE" || echo "Python не найден" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Установленные пакеты Django:" >> "$OUTPUT_FILE"
python3 -c "import django; print(f'Django версия: {django.__version__}')" 2>> "$OUTPUT_FILE" || echo "Django не установлен" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Зависимости проекта:" >> "$OUTPUT_FILE"
if [ -f "requirements.txt" ]; then
    cat requirements.txt >> "$OUTPUT_FILE"
else
    echo "requirements.txt не найден" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
echo "=== СБОР ЗАВЕРШЕН ===" >> "$OUTPUT_FILE"
echo "Обработано файлов: $ADDED_FILES из $TOTAL_FILES" >> "$OUTPUT_FILE"
echo "Итоговый файл: $OUTPUT_FILE ($(wc -l < "$OUTPUT_FILE") строк, $(wc -c < "$OUTPUT_FILE") символов)" >> "$OUTPUT_FILE"
echo "Размер выходного файла: $(du -h "$OUTPUT_FILE" | cut -f1)" >> "$OUTPUT_FILE"

echo "Сбор завершен!"
echo "📁 Основной файл: $OUTPUT_FILE"
echo "📋 Лог обработки: $LOG_FILE"
echo ""
echo "Отправьте содержимое файла '$OUTPUT_FILE' AI-ассистенту для полного анализа"
