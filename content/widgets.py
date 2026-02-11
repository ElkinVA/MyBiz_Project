# content/widgets.py
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import escape

class ColorPickerWidget(forms.TextInput):
    """Виджет для выбора цвета с предпросмотром"""

    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'color',
            'class': 'color-picker-input',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Рендерим обычное поле ввода цвета
        input_html = super().render(name, value, attrs, renderer)

        # Безопасно экранируем значение
        safe_value = escape(value or '#3b82f6')

        # Добавляем наш кастомный HTML для пикера
        html = f'''
        <div class="color-picker-widget">
            <div class="color-picker-container">
                {input_html}
                <div class="color-picker-text">
                    <input type="text"
                           class="color-hex-input"
                           value="{safe_value}"
                           placeholder="#3b82f6"
                           style="width: 120px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-left: 10px;"
                           maxlength="7">
                </div>
            </div>
        </div>
        '''

        # Помечаем HTML как безопасный для отображения
        return mark_safe(html)

    class Media:
        css = {
            'all': ('admin/css/color-picker.css',)
        }
        js = ('admin/js/color-picker.js',)
