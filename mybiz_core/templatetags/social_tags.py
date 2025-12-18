# mybiz_core/templatetags/social_tags.py
from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles import finders
import re

register = template.Library()


@register.simple_tag
def social_icon(icon_name):
    """Загружает SVG иконку социальной сети"""
    icon_path = f"social/{icon_name}.svg"

    try:
        # Пытаемся найти файл в статических файлах
        result = finders.find(icon_path)

        if result:
            with open(result, 'r', encoding='utf-8') as f:
                svg_content = f.read()

                # Удаляем XML декларацию если есть
                svg_content = svg_content.replace('<?xml version="1.0" encoding="UTF-8"?>', '')

                # Используем более точное регулярное выражение для тега svg
                # Находим тег <svg и все его атрибуты
                svg_pattern = r'(<svg[^>]*)'

                def process_svg_tag(match):
                    svg_tag = match.group(1)

                    # Удаляем атрибуты width и height
                    svg_tag = re.sub(r'\s(width|height)="[^"]*"', '', svg_tag)

                    # Добавляем или обновляем классы
                    if 'class="' in svg_tag:
                        # Проверяем, нет ли уже классов w-6 h-6
                        if 'w-6' not in svg_tag or 'h-6' not in svg_tag:
                            svg_tag = re.sub(r'class="([^"]*)"', r'class="\1 w-6 h-6"', svg_tag)
                    else:
                        svg_tag = svg_tag.replace('<svg', '<svg class="w-6 h-6"', 1)

                    # Убедимся что fill="currentColor"
                    if 'fill="' not in svg_tag and "fill='" not in svg_tag:
                        svg_tag = svg_tag.replace('<svg', '<svg fill="currentColor"', 1)
                    else:
                        # Заменяем существующий fill на currentColor
                        svg_tag = re.sub(r'fill="[^"]*"', 'fill="currentColor"', svg_tag)
                        svg_tag = re.sub(r"fill='[^']*'", "fill='currentColor'", svg_tag)

                    return svg_tag

                # Применяем обработку только к открывающему тегу <svg
                svg_content = re.sub(svg_pattern, process_svg_tag, svg_content, count=1)

                svg_content = svg_content.strip()
                return mark_safe(svg_content)

    except Exception as e:
        # В случае ошибки возвращаем простую иконку
        print(f"Ошибка загрузки иконки {icon_name}: {e}")

    # Запасной вариант: базовые иконки с правильными классами
    fallback_icons = {
        'telegram': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.25 1.58-1.32 5.4-1.87 7.17-.2.7-.59.94-.97.94-.41 0-.57-.29-1.23-.58-1.92-.77-3.18-1.25-4.04-2.5-.43-.58-.77-1.66.08-2.39.47-.41 3.88-3.74 3.95-4.06.01-.04.01-.19-.07-.27-.08-.09-.2-.06-.29-.04-.12.03-2.01 1.27-5.67 3.73-.53.37-1.01.55-1.44.54-.48-.01-1.41-.27-2.1-.5-.85-.28-1.53-.43-1.47-.9.03-.24.28-.48.77-.73 2.95-1.28 4.93-2.14 7.36-3.18 1.1-.47 2.2-.98 3.11-1.01.23 0 .74.04 1.08.33.28.24.36.57.39.82.04.46.07 1.19.07 2.22 0 .31-.02.67-.03 1.08z"/>
        </svg>
        ''',
        'vk': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M15.07 2H8.93C3.33 2 2 3.33 2 8.93v6.14C2 20.67 3.33 22 8.93 22h6.14c5.6 0 6.93-1.33 6.93-6.93V8.93C22 3.33 20.67 2 15.07 2zm3.77 14.14c-.12.33-.47.52-1.08.52h-.17c-.78 0-2.05-.48-2.91-1.18-.15 2.25-.67 3.15-1.94 3.15-1.1 0-1.65-.84-1.65-2.34 0-1.24.08-2.22.16-3.09l.01-.15c.08-.86.17-1.73.25-2.59.04-.33.19-.5.46-.5h1.4c.34 0 .5.17.5.5v2.59c0 .33.17.5.5.5h.08c.33 0 .5-.17.5-.5V8.36c0-.33.17-.5.5-.5h1.89c.33 0 .5.17.5.5v2.09c0 .33.17.5.5.5h.08c.33 0 .5-.17.5-.5V8.36c0-.33.17-.5.5-.5h1.89c.33 0 .5.17.5.5v3.68c0 .33-.17.5-.5.5h-.08c-.33 0-.5-.17-.5-.5v-.59c0-.33-.17-.5-.5-.5h-.08c-.33 0-.5.17-.5.5v1.59c0 .33-.17.5-.5.5h-.08c-.33 0-.5-.17-.5-.5v-1.59c0-.33-.17-.5-.5-.5h-.08c-.33 0-.5.17-.5.5v2.59c0 .33-.17.5-.5.5h-.08c-.33 0-.5-.17-.5-.5v-2.09c0-.33-.17-.5-.5-.5h-.08c-.33 0-.5.17-.5.5v3.18c0 .33.17.5.5.5h.34c.61 0 1.1-.19 1.1-.69 0-.2-.03-.4-.08-.57z"/>
        </svg>
        ''',
        'max': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        ''',
        'instagram': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 01-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 017.8 2m-.2 2A3.6 3.6 0 004 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 003.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 011.25 1.25A1.25 1.25 0 0117.25 8 1.25 1.25 0 0116 6.75a1.25 1.25 0 011.25-1.25M12 7a5 5 0 015 5 5 5 0 01-5 5 5 5 0 01-5-5 5 5 0 015-5m0 2a3 3 0 00-3 3 3 3 0 003 3 3 3 0 003-3 3 3 0 00-3-3z"/>
        </svg>
        '''
    }

    return mark_safe(fallback_icons.get(icon_name, '<svg class="w-6 h-6" fill="currentColor"></svg>'))
