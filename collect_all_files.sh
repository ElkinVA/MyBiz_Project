#!/bin/bash
# =========================================================================
# collect_all_files.sh – сбор значимых исходников для анализа AI
# =========================================================================
# Исправленная версия:
# – надёжное исключение служебных директорий из дерева и из файлов
# – исключение самого выходного файла и лога
# – исключение минифицированных/сгенерированных ресурсов (tailwind.css)
# – один проход find для списка файлов
# – корректный вывод дерева только нужных папок
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
    # Сам выходной файл и лог
    "$OUTPUT_FILE"
    "$LOG_FILE"
    # Минифицированный CSS/JS, не несущий смысловой нагрузки
    "tailwind.css"            # скомпилированный Tailwind
    "tailwind.min.css"
    "bootstrap.min.css"
    "bootstrap.min.js"
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
    "package-lock.json"
    "composer.lock"
    ".prettierrc"
    ".eslintrc"
    ".babelrc"
    # Дополнительно явно укажем скомпилированные файлы Tailwind,
    # даже если они попали бы по расширению css
    "tailwind.css"
    "tailwind.min.css"
)

# -------------------------------------------------------------------------
# Функция проверки, нужно ли обрабатывать файл
# -------------------------------------------------------------------------
should_include() {
    local filepath="$1"
    local filename=$(basename "$filepath")

    # Исключаем выходной файл и лог (уже есть в EXCLUDE_NAMES, но доп. проверка)
    if [[ "$filename" == "$OUTPUT_FILE" || "$filename" == "$LOG_FILE" ]]; then
        return 1
    fi

    # Исключаем файлы по точному имени
    for pattern in "${EXCLUDE_NAMES[@]}"; do
        if [[ "$filename" == $pattern ]]; then
            return 1
        fi
    done

    # Исключаем конкретные нежелательные файлы (по полному имени)
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        if [[ "$filename" == "$pattern" ]]; then
            return 1
        fi
    done

    # Исключаем файлы внутри директорий migrations (код миграций Django)
    if [[ "$filepath" == */migrations/* ]]; then
        return 1
    fi

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

    # Дополнительно убеждаемся, что файл текстовый (MIME-тип)
    local mime=$(file --mime-type -b "$filepath" 2>/dev/null)
    if [[ "$mime" == text/* ]]; then
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
# Построение безопасного выражения prune для find
# -------------------------------------------------------------------------
prune_expr=""
for dir in "${EXCLUDE_DIRS[@]}"; do
    prune_expr+=" -path './$dir' -prune -o"
done

# -------------------------------------------------------------------------
# Основной проход: находим все подходящие файлы за один проход
# -------------------------------------------------------------------------
# Временный файл для списка файлов
file_list=$(mktemp)

# Собираем все файлы (исключая директории через prune)
eval "find . \( $prune_expr -type f -print \) 2>/dev/null" | sort > "$file_list"

total=0
while IFS= read -r file; do
    if should_include "$file"; then
        total=$((total + 1))
    fi
done < "$file_list"

echo "Найдено релевантных файлов: $total" >> "$LOG_FILE"
echo "Начинаем сбор..." >> "$LOG_FILE"

count=0
while IFS= read -r file; do
    if should_include "$file"; then
        count=$((count + 1))
        add_file "$file" "$count"
        echo "Обработан [$count/$total]: $file"
    fi
done < "$file_list"

# Удаляем временный файл
rm -f "$file_list"

# -------------------------------------------------------------------------
# Добавляем дерево директорий (только для включённых папок)
# -------------------------------------------------------------------------
echo "=== ДЕРЕВО ДИРЕКТОРИЙ ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
# Используем то же prune-выражение, но выводим только директории
eval "find . \( $prune_expr -type d -print \) 2>/dev/null" | sort | \
    sed 's|[^/]*/| |- |g' >> "$OUTPUT_FILE"

# -------------------------------------------------------------------------
# Сводная информация
# -------------------------------------------------------------------------
echo "" >> "$OUTPUT_FILE"
echo "=== СБОР ЗАВЕРШЁН ===" >> "$OUTPUT_FILE"
echo "Всего файлов: $count" >> "$OUTPUT_FILE"
echo "Выходной файл: $OUTPUT_FILE" >> "$OUTPUT_FILE"

echo "Готово! Собран $count файлов в $OUTPUT_FILE"
