#!/bin/bash

# Скрипт для сбора всех файлов проекта MyBiz в один текстовый файл
# Для использования в WSL Ubuntu

OUTPUT_FILE="project_analysis.txt"
LOG_FILE="collection_log.txt"

echo "=== Начало сбора файлов проекта MyBiz ===" > "$LOG_FILE"
date >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Функция для добавления файла в отчет
add_file() {
    local file_path=$1
    local description=$2

    echo "Обработка: $file_path" | tee -a "$LOG_FILE"

    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "ФАЙЛ: $file_path" >> "$OUTPUT_FILE"
    echo "ОПИСАНИЕ: $description" >> "$OUTPUT_FILE"
    echo "================================================================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    if [ -f "$file_path" ]; then
        cat "$file_path" >> "$OUTPUT_FILE"
        echo "✓ Успешно добавлен" >> "$LOG_FILE"
    else
        echo "✗ Файл не найден: $file_path" >> "$OUTPUT_FILE"
        echo "✗ Файл не найден" >> "$LOG_FILE"
    fi

    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
}

# Создаем или очищаем выходной файл
> "$OUTPUT_FILE"

echo "=== СНИМОК ПРОЕКТА MYBIZ ===" >> "$OUTPUT_FILE"
echo "Дата создания: $(date)" >> "$OUTPUT_FILE"
echo "Для анализа AI-ассистентом" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 1. КОНФИГУРАЦИОННЫЕ ФАЙЛЫ
echo "=== 1. КОНФИГУРАЦИОННЫЕ ФАЙЛЫ ===" >> "$OUTPUT_FILE"

add_file "config/settings.py" "Основные настройки Django проекта"
add_file "config/urls.py" "Главные URL-маршруты проекта"
add_file "requirements.txt" "Зависимости Python проекта"

# 2. МОДЕЛИ ДАННЫХ
echo "=== 2. МОДЕЛИ ДАННЫХ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/models.py" "Модели для товаров и категорий"
add_file "content/models.py" "Модели для контента и настроек сайта"
add_file "pages/models.py" "Модели для SEO-страниц"

# 3. ПРЕДСТАВЛЕНИЯ (VIEWS)
echo "=== 3. ПРЕДСТАВЛЕНИЯ (VIEWS) ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/views.py" "Представления для товаров и категорий"
add_file "pages/views.py" "Представления для SEO-страниц"

# 4. URL-МАРШРУТЫ
echo "=== 4. URL-МАРШРУТЫ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/urls.py" "URL-маршруты приложения mybiz_core"
add_file "pages/urls.py" "URL-маршруты приложения pages"

# 5. АДМИН-ПАНЕЛЬ
echo "=== 5. АДМИН-ПАНЕЛЬ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/admin.py" "Админка для товаров и категорий"
add_file "content/admin.py" "Админка для контента и настроек"
add_file "pages/admin.py" "Админка для SEO-страниц"

# 6. КОНТЕКСТНЫЕ ПРОЦЕССОРЫ
echo "=== 6. КОНТЕКСТНЫЕ ПРОЦЕССОРЫ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/context_processors.py" "Контекстный процессор для категорий"
add_file "content/context_processors.py" "Контекстные процессоры для настроек и промо-акций"

# 7. ШАБЛОНЫ
echo "=== 7. ШАБЛОНЫ ===" >> "$OUTPUT_FILE"

add_file "templates/base.html" "Базовый шаблон сайта"
add_file "templates/home.html" "Шаблон главной страницы"
add_file "templates/products/product_list.html" "Шаблон списка товаров"
add_file "templates/products/product_detail.html" "Шаблон детальной страницы товара"
add_file "templates/products/product_items.html" "Шаблон для AJAX-подгрузки товаров"
add_file "templates/includes/header.html" "Шаблон хедера"
add_file "templates/includes/footer.html" "Шаблон футера"

# 8. КОМАНДА ДЛЯ ТЕСТОВЫХ ДАННЫХ
echo "=== 8. КОМАНДА ДЛЯ ТЕСТОВЫХ ДАННЫХ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/management/commands/seed_data.py" "Команда для генерации тестовых данных"

# 9. ФАЙЛЫ МИГРАЦИЙ (последние)
echo "=== 9. ФАЙЛЫ МИГРАЦИЙ ===" >> "$OUTPUT_FILE"

# Находим последние файлы миграций для каждого приложения
find_migration() {
    local app=$1
    local migration_file=$(find "$app/migrations" -name "*.py" ! -name "__init__.py" | sort -V | tail -1)

    if [ -n "$migration_file" ]; then
        add_file "$migration_file" "Последняя миграция для $app"
    else
        echo "================================================================================" >> "$OUTPUT_FILE"
        echo "ФАЙЛ: $app/migrations/ (нет миграций или приложение не найдено)" >> "$OUTPUT_FILE"
        echo "================================================================================" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
}

find_migration "mybiz_core"
find_migration "content"
find_migration "pages"

# 10. ТЕСТЫ
echo "=== 10. ТЕСТЫ ===" >> "$OUTPUT_FILE"

add_file "mybiz_core/tests.py" "Тесты для приложения mybiz_core"

# Добавляем информацию о структуре проекта
echo "=== СТРУКТУРА ПРОЕКТА ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Директории проекта:" >> "$OUTPUT_FILE"
find . -type d -name ".*" -prune -o -type d -print | sort | head -30 >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Файлы проекта (первые 50):" >> "$OUTPUT_FILE"
find . -type f -name ".*" -prune -o -type f -print | sort | head -50 >> "$OUTPUT_FILE"

# Добавляем информацию о Python-пакетах
echo "" >> "$OUTPUT_FILE"
echo "=== ИНФОРМАЦИЯ О СРЕДЕ ===" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Python версия:" >> "$OUTPUT_FILE"
python3 --version 2>> "$OUTPUT_FILE" || echo "Python не найден" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Установленные пакеты (Django):" >> "$OUTPUT_FILE"
python3 -c "import django; print(f'Django версия: {django.__version__}')" 2>> "$OUTPUT_FILE" || echo "Django не установлен" >> "$OUTPUT_FILE"

# Завершаем лог
echo "" >> "$LOG_FILE"
echo "=== Завершение сбора файлов ===" >> "$LOG_FILE"
echo "Всего файлов обработано: $(grep -c "Обработка:" "$LOG_FILE")" >> "$LOG_FILE"
echo "Файлов найдено: $(grep -c "✓ Успешно добавлен" "$LOG_FILE")" >> "$LOG_FILE"
echo "Файлов не найдено: $(grep -c "✗ Файл не найден" "$LOG_FILE")" >> "$LOG_FILE"
echo "Итоговый файл: $OUTPUT_FILE ($(wc -l < "$OUTPUT_FILE") строк)" >> "$LOG_FILE"

echo ""
echo "✅ Сбор файлов проекта завершен!"
echo "📁 Основной файл: $OUTPUT_FILE"
echo "📋 Лог сбора: $LOG_FILE"
echo ""
echo "Отправьте содержимое файла '$OUTPUT_FILE' AI-ассистенту для анализа"
