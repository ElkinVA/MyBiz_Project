# mybiz_core/templatetags/social_tags.py
from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles import finders
from django.conf import settings
import os
import re
import logging

logger = logging.getLogger(__name__)
register = template.Library()

# Кэш для загруженных SVG
_svg_cache = {}

def _load_svg_content(icon_name):
    """Загружает содержимое SVG файла"""
    # Проверяем кэш
    if icon_name in _svg_cache:
        return _svg_cache[icon_name]

    # Путь к файлу иконки
    icon_path = f'social/{icon_name}.svg'

    try:
        # Ищем файл в статике
        file_path = finders.find(icon_path)

        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                _svg_cache[icon_name] = content
                return content
        else:
            logger.warning(f"SVG иконка не найдена: {icon_path}")
            # Пытаемся найти в медиа
            media_path = os.path.join(settings.MEDIA_ROOT, icon_path)
            if os.path.exists(media_path):
                with open(media_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    _svg_cache[icon_name] = content
                    return content
    except Exception as e:
        logger.error(f"Ошибка загрузки SVG иконки {icon_name}: {e}")

    return None

def _process_svg_content(svg_content, icon_name):
    """Обрабатывает SVG для правильного отображения"""
    if not svg_content:
        return None

    # Удаляем XML декларацию если есть
    svg_content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)

    # Находим тег <svg> и обрабатываем его
    def process_svg_tag(match):
        svg_tag = match.group(1)

        # Удаляем атрибуты width и height (будут заданы через CSS)
        svg_tag = re.sub(r'\s(width|height)="[^"]*"', '', svg_tag)

        # Добавляем классы для Tailwind
        if 'class="' in svg_tag:
            # Добавляем w-6 h-6 если нет
            if 'w-6' not in svg_tag or 'h-6' not in svg_tag:
                svg_tag = re.sub(r'class="([^"]*)"', r'class="\1 w-6 h-6"', svg_tag)
        else:
            svg_tag = svg_tag.replace('<svg', '<svg class="w-6 h-6"', 1)

        # Устанавливаем fill="currentColor" для наследования цвета
        if 'fill="' not in svg_tag and "fill='" not in svg_tag:
            svg_tag = svg_tag.replace('<svg', '<svg fill="currentColor"', 1)
        else:
            # Заменяем существующий fill на currentColor
            svg_tag = re.sub(r'fill="[^"]*"', 'fill="currentColor"', svg_tag)
            svg_tag = re.sub(r"fill='[^']*'", "fill='currentColor'", svg_tag)

        # Добавляем viewBox если нет
        if 'viewBox' not in svg_tag:
            svg_tag = svg_tag.replace('<svg', '<svg viewBox="0 0 24 24"', 1)

        return svg_tag

    # Применяем обработку только к первому тегу <svg>
    svg_content = re.sub(r'(<svg[^>]*)', process_svg_tag, svg_content, count=1)

    return svg_content.strip()

@register.simple_tag
def social_icon(icon_name):
    """Загружает SVG иконку социальной сети"""
    if not icon_name:
        return mark_safe('<span class="w-6 h-6">?</span>')

    # Загружаем содержимое SVG
    svg_content = _load_svg_content(icon_name)

    # Обрабатываем SVG
    if svg_content:
        processed_content = _process_svg_content(svg_content, icon_name)
        if processed_content:
            return mark_safe(processed_content)

    # Fallback иконки (встроенные SVG)
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
        ''',
        'check': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
        </svg>
    ''',
    'truck': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
        </svg>
    ''',
    'lock': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
        </svg>
    ''',
    'headset': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
    ''',
    'star': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
    ''',
    'heart': '''
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"/>
        </svg>
    ''',
    'clock': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
    ''',
    'shield': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
        </svg>
    ''',
    'credit-card': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
        </svg>
    ''',
    'gift': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"/>
        </svg>
    ''',
    'phone': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
        </svg>
    ''',
    'map-pin': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
    ''',
    'users': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
        </svg>
    ''',
    'award': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
        </svg>
    ''',
    'thumbs-up': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"/>
        </svg>
    ''',
    'refresh': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
        </svg>
    ''',
    'discount': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l5 5a2 2 0 01.586 1.414V19a2 2 0 01-2 2H7a2 2 0 01-2-2V5a2 2 0 012-2z"/>
        </svg>
    ''',
    'package': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
        </svg>
    ''',
    'coffee': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
    ''',
    'wifi': '''
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.14 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/>
        </svg>
    ''',
    }

    return mark_safe(fallback_icons.get(icon_name, '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"></svg>'))
