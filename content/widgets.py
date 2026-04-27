# content/widgets.py
"""
Кастомные виджеты для админ-панели Django
"""
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
import os


class ColorPickerWidget(forms.TextInput):
    """
    Виджет для выбора цвета с палитрой (input type="color") и текстовым полем HEX + превью.
    Структура: .color-picker-widget > .color-picker-container > input[type=color] + input.color-hex-input + .color-preview
    """
    template_name = 'admin/widgets/color_picker.html'  # оставлено для совместимости, но не используется

    class Media:
        css = {
            'all': (
                'admin/css/color-picker.css',
                'admin/css/color-fields-compact.css',
            )
        }
        js = ('admin/js/color-picker.js',)

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'vColorPickerField',
            'placeholder': '#000000',
            'pattern': '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Нормализация HEX-значения
        if not value or value.strip() == '':
            value = '#000000'
        else:
            # Добавляем # если его нет
            if not value.startswith('#'):
                value = '#' + value
            # Преобразуем к нижнему регистру
            value = value.lower()
            # Если короткий формат (#RGB), преобразуем в полный (#RRGGBB)
            if len(value) == 4:
                value = '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3]

        # Базовые атрибуты для текстового поля HEX
        final_attrs = self.build_attrs(self.attrs, attrs)
        
        # Объединяем классы корректно
        base_classes = final_attrs.get('class', '')
        all_classes = f"{base_classes} color-hex-input".strip()
        
        final_attrs.update({
            'name': name,
            'value': value,
            'maxlength': '7',
            'class': all_classes,
        })

        # Формируем строку атрибутов без type (так как задаем явно)
        attrs_list = []
        for key, val in final_attrs.items():
            if key == 'type':
                continue  # Пропускаем type из attrs, так как задаем свой
            attrs_list.append(f'{key}="{val}"')
        attrs_string = ' '.join(attrs_list)

        # Генерируем input type="color" и текстовое поле HEX
        html = f'''
        <div class="color-picker-widget" data-widget="color-picker">
            <div class="color-picker-container">
                <input type="color" value="{value}">
                <input type="text" {attrs_string} placeholder="#000000">
                <div class="color-preview" style="background-color: {value};"></div>
            </div>
        </div>
        '''
        return mark_safe(html)


class ImagePreviewWidget(forms.ClearableFileInput):
    """
    Виджет для загрузки изображений с превью.
    """
    template_name = 'admin/widgets/image_preview.html'

    class Media:
        css = {
            'all': ('admin/css/image-preview.css',)
        }
        js = ('admin/js/image-preview.js',)

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'vImageField',
            'accept': 'image/*',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value and hasattr(value, 'url'):
            context['image_url'] = value.url
            context['image_name'] = value.name
        else:
            context['image_url'] = None
            context['image_name'] = None
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)

        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs.update({'name': name, 'type': 'file'})
        attrs_string = ' '.join(f'{key}="{val}"' for key, val in final_attrs.items())

        html = f'''
        <div class="image-preview-wrapper" data-widget="image-preview">
        '''
        if context['image_url']:
            html += f'''
            <div class="current-image">
                <p class="image-label">Текущее изображение:</p>
                <img src="{context['image_url']}" alt="{context['image_name']}"
                     style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #e5e7eb;">
                <p class="image-name">{context['image_name']}</p>
            </div>
            '''
        html += f'''
            <div class="new-image-upload">
                <p class="image-label">Новое изображение:</p>
                <input {attrs_string}>
                <div class="image-preview-container" style="display: none;">
                    <img class="image-preview"
                         style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #3b82f6; margin-top: 10px;">
                </div>
            </div>
        </div>
        '''
        return mark_safe(html)


class CKEditor5PreviewWidget(forms.Textarea):
    class Media:
        css = {'all': ('admin/css/ckeditor-preview.css',)}

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        if value:
            html += f'''
            <div class="ckeditor-preview" style="margin-top: 10px; padding: 15px;
                background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
                <p style="margin: 0 0 10px 0; font-weight: 600; color: #6b7280;">Предпросмотр:</p>
                <div style="color: #1f2937;">{value}</div>
            </div>
            '''
        return mark_safe(html)
