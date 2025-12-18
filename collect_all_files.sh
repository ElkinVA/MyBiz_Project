#!/bin/bash

# Скрипт для сбора ВСЕХ файлов проекта MyBiz в один текстовый файл
# Рекурсивно обходит все папки и подпапки

OUTPUT_FILE="full_project_analysis.txt"

echo "-== Начало полного сбора файлов проекта MyBiz ==-"
# Функция для добавления файла в отчет
add_file() {
    local file_path=$1

  #  echo "Обработка: $file_path"

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

# Создаем или очищаем выходной файл
> "$OUTPUT_FILE"

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

# Функция для проверки исключения директории
is_excluded_dir() {
    local dir=$1
    for excluded in "${EXCLUDE_DIRS[@]}"; do
        if [[ "$dir" == *"/$excluded"* ]] || [[ "$dir" == "$excluded"* ]]; then
            return 0
        fi
    done
    return 1
}

# Функция для проверки исключения файла
is_excluded_file() {
    local file=$1
    for pattern in "${EXCLUDE_FILES[@]}"; do
        if [[ "$file" == $pattern ]] || [[ "$(basename "$file")" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# Счетчики
total_files=0
added_files=0
skipped_files=0



# Рекурсивный обход всех файлов
find . -type f | while read -r file; do
    # Пропускаем исключенные директории
    dir=$(dirname "$file")
    if is_excluded_dir "$dir"; then

        skipped_files=$((skipped_files + 1))
        continue
    fi

    # Пропускаем исключенные файлы
    if is_excluded_file "$file"; then

        skipped_files=$((skipped_files + 1))
        continue
    fi

    # Пропускаем сам выходной файл и лог
    if [[ "$file" == "./$OUTPUT_FILE" ]] || [[ "$file" == "./$LOG_FILE" ]]; then
        continue
    fi

    total_files=$((total_files + 1))

    # Добавляем файл в отчет
    add_file "$file"
    added_files=$((added_files + 1))
done
echo "=== СТРУКТУРА ПРОЕКТА (дерево директорий) ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
find . -type d | grep -vE "$(IFS='|'; echo "${EXCLUDE_DIRS[*]}")" | sort | sed 's|[^/]*/|- |g' >> "$OUTPUT_FILE"

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

# Завершаем лог

echo "Итоговый файл: $OUTPUT_FILE ($(wc -l < "$OUTPUT_FILE") строк, $(wc -c < "$OUTPUT_FILE") символов)"
echo "Размер выходного файла: $(du -h "$OUTPUT_FILE" | cut -f1)"


echo "📁 Основной файл: $OUTPUT_FILE"

echo "Отправьте содержимое файла '$OUTPUT_FILE' AI-ассистенту для полного анализа"
