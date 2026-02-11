
# mybiz_core/templatetags/color_filters.py
from django import template
import re

register = template.Library()

@register.filter
def hex_to_rgb(value):
    """Преобразует HEX цвет в RGB строку без скобок"""
    if not value:
        return '59, 130, 246' # Цвет по умолчанию (blue-500)

    # Убираем решетку и проверяем формат
    hex_color = value.lstrip('#').lower()
    if not re.match(r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', hex_color):
        # Если формат неверный, возвращаем цвет по умолчанию
        return '59, 130, 246'

    # Преобразуем короткий формат в полный
    if len(hex_color) == 3:
        hex_color = ''.join([char * 2 for char in hex_color])

    # Преобразуем в RGB
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'{r}, {g}, {b}'
    except ValueError:
        # Если ошибка преобразования, возвращаем цвет по умолчанию
        return '59, 130, 246'

@register.filter
def hex_to_rgb_dict(value):
    """Преобразует HEX цвет в словарь RGB"""
    if not value:
        return {'r': 59, 'g': 130, 'b': 246}

    hex_color = value.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    try:
        return {
            'r': int(hex_color[0:2], 16),
            'g': int(hex_color[2:4], 16),
            'b': int(hex_color[4:6], 16)
        }
    except (ValueError, IndexError):
        return {'r': 59, 'g': 130, 'b': 246}

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_class(value, arg):
    """Добавляет CSS класс к строке"""
    classes = value.split(' ')
    if arg not in classes:
        classes.append(arg)
    return ' '.join(classes)
