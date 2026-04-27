#!/bin/bash
# =========================================================================
# collect_source_for_ai.sh – сбор значимых исходников для анализа AI
# =========================================================================

OUTPUT_FILE="project_sources.txt"
LOG_FILE="collection.log"

echo "== Сбор исходных кодов проекта MyBiz для AI-анализа =="
echo "Лог: $LOG_FILE"

> "$OUTPUT_FILE"
> "$LOG_FILE"

# -------------------------------------------------------------------------
# Директории, которые нужно полностью исключить из обхода
# -------------------------------------------------------------------------
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
    "htmlcov"
    ".coverage"
    "release"
    ".mypy_cache"
    ".ruff_cache"
)

# -------------------------------------------------------------------------
# Файлы, исключаемые по имени (точное совпадение имени файла)
# -------------------------------------------------------------------------
EXCLUDE_NAMES=(
    ".gitignore"
    ".flake8"
    ".env.example"
    "package-lock.json"
    "yarn.lock"
    "db.sqlite3"
    ".DS_Store"
    "*.pyc"
    "*.pyo"
    "*.pyd"
    "*.db"
    "*.log"
)

# -------------------------------------------------------------------------
# Расширения файлов, которые нас интересуют (только текстовые исходники)
# -------------------------------------------------------------------------
INCLUDE_EXT=(
    "*.py"
    "*.html"
    "*.css"
    "*.js"
    "*.svg"
    "*.md"
    "*.txt"
    "*.toml"
    "*.ini"
    "*.cfg"
    "*.conf"
    "*.yml"
    "*.yaml"
    "*.json"
)

# Исключения из включаемых расширений (полные имена файлов)
EXCLUDE_PATTERNS=(
    "package-lock.json"   # уже есть в EXCLUDE_NAMES, но на всякий случай
    "composer.lock"
    ".prettierrc"
    ".eslintrc"
    ".babelrc"
)

# -------------------------------------------------------------------------
# Функция проверки, нужно ли обрабатывать файл
# -------------------------------------------------------------------------
should_include() {
    local filepath="$1"
    local filename=$(basename "$filepath")

    # Исключаем файлы по точному имени
    for pattern in "${EXCLUDE_NAMES[@]}"; do
        if [[ "$filename" == $pattern ]]; then
            return 1
        fi
    done

    # Исключаем файлы внутри директорий migrations
    if [[ "$filepath" == */migrations/* ]]; then
        return 1
    fi

    # Исключаем конкретные нежелательные файлы
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$filename" == "$pattern" ]]; then
            return 1
        fi
    done

    # Проверяем, что файл имеет нужное расширение
    local ext_match=false
    for ext in "${INCLUDE_EXT[@]}"; do
        # ext имеет вид "*.py", используем glob-сравнение
        if [[ "$filename" == $ext ]]; then
            ext_match=true
            break
        fi
    done

    if ! $ext_match; then
        return 1
    fi

    # Дополнительно убеждаемся, что файл текстовый
    if file "$filepath" | grep -q "text"; then
        return 0
    else
        return 1
    fi
}

# -------------------------------------------------------------------------
# Функция добавления файла в отчёт
# -------------------------------------------------------------------------
add_file() {
    local filepath="$1"
    local count="$2"
    echo "[$count] $filepath" >> "$LOG_FILE"

    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "FILE: $filepath" >> "$OUTPUT_FILE"
    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ -f "$filepath" ]; then
        cat "$filepath" >> "$OUTPUT_FILE"
    else
        echo "✗ File not found" >> "$OUTPUT_FILE"
    fi
    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# -------------------------------------------------------------------------
# Построение списка исключаемых директорий для find
# -------------------------------------------------------------------------
prune_args=""
for dir in "${EXCLUDE_DIRS[@]}"; do
    prune_args="$prune_args -name \"$dir\" -prune -o"
done

# -------------------------------------------------------------------------
# Основной проход: находим все файлы, фильтруем и пишем отчёт
# -------------------------------------------------------------------------
count=0
total=0

# Сначала считаем общее количество подходящих файлов (для прогресса)
while IFS= read -r file; do
    if should_include "$file"; then
        total=$((total + 1))
    fi
done < <(eval "find . $prune_args -type f -print 2>/dev/null")

echo "Найдено релевантных файлов: $total" >> "$LOG_FILE"
echo "Начинаем сбор..." >> "$LOG_FILE"

# Теперь собираем содержимое
while IFS= read -r file; do
    if should_include "$file"; then
        count=$((count + 1))
        add_file "$file" "$count"
        echo "Обработан [$count/$total]: $file"
    fi
done < <(eval "find . $prune_args -type f -print 2>/dev/null")

# -------------------------------------------------------------------------
# Добавляем дерево директорий (только для включённых файлов)
# -------------------------------------------------------------------------
echo "=== ДЕРЕВО ДИРЕКТОРИЙ ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
find . $prune_args -type d | sort | sed 's|[^/]*/|- |g' >> "$OUTPUT_FILE" 2>/dev/null

# -------------------------------------------------------------------------
# Сводная информация
# -------------------------------------------------------------------------
echo "" >> "$OUTPUT_FILE"
echo "=== СБОР ЗАВЕРШЁН ===" >> "$OUTPUT_FILE"
echo "Всего файлов: $count" >> "$OUTPUT_FILE"
echo "Выходной файл: $OUTPUT_FILE" >> "$OUTPUT_FILE"

echo "Готово! Собран $count файлов в $OUTPUT_FILE"
