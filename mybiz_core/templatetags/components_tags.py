# mybiz_core/templatetags/components_tags.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.inclusion_tag('components/button.html')
def button_component(href="#", type="primary", size="md", full_width=False, icon=None, text=""):
    """Компонент кнопки"""
    return {
        'href': href,
        'type': type,
        'size': size,
        'full_width': full_width,
        'icon': icon,
        'text': text,
    }

@register.inclusion_tag('components/card.html')
def card_component(title=None, subtitle=None, image=None, badge=None):
    """Компонент карточки"""
    return {
        'title': title,
        'subtitle': subtitle,
        'image': image,
        'badge': badge,
    }

@register.inclusion_tag('components/stat.html')
def stat_component(number, label, icon=None, color="primary", animation=True):
    """Компонент статистики"""
    return {
        'number': number,
        'label': label,
        'icon': icon,
        'color': color,
        'animation': animation,
    }

@register.inclusion_tag('components/feature.html')
def feature_component(icon, title, description):
    """Компонент фичи"""
    return {
        'icon': icon,
        'title': title,
        'description': description,
    }

@register.inclusion_tag('components/testimonial.html')
def testimonial_component(text, author, role=None, avatar=None):
    """Компонент отзыва"""
    return {
        'text': text,
        'author': author,
        'role': role,
        'avatar': avatar,
    }

@register.inclusion_tag('components/pricing.html')
def pricing_component(title, price, period, features, button_text, button_url, popular=False):
    """Компонент цены"""
    return {
        'title': title,
        'price': price,
        'period': period,
        'features': features,
        'button_text': button_text,
        'button_url': button_url,
        'popular': popular,
    }

@register.inclusion_tag('components/section_header.html')
def section_header_component(title, subtitle=None, align="center"):
    """Компонент заголовка секции"""
    return {
        'title': title,
        'subtitle': subtitle,
        'align': align,
    }

@register.inclusion_tag('components/spinner.html')
def spinner_component(size="md", color="primary"):
    """Компонент спиннера"""
    return {
        'size': size,
        'color': color,
    }

@register.inclusion_tag('components/alert.html')
def alert_component(type="info", title=None, dismissible=True, message=""):
    """Компонент алерта"""
    return {
        'type': type,
        'title': title,
        'dismissible': dismissible,
        'message': message,
    }

@register.inclusion_tag('components/product_card.html')
def product_card_component(product):
    """Компонент карточки товара"""
    return {
        'product': product,
    }

# Простые функции-хелперы
@register.filter
def add_class(value, css_class):
    """Добавляет CSS класс к строке"""
    if value and css_class:
        return f"{value} {css_class}"
    return value

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
