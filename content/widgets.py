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
    Виджет для выбора цвета с превью
    Отображает input type="color" и текстовое поле для HEX кода
    """
    template_name = 'admin/widgets/color_picker.html'

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
        """Рендеринг виджета"""
        if value is None:
            value = '#000000'

        # ✅ ИСПРАВЛЕНО: Правильный способ установки атрибутов для Django 5.2+
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs.update({
            'type': 'text',
            'name': name,
            'value': value,
        })

        attrs_string = ' '.join(f'{key}="{val}"' for key, val in final_attrs.items())

        html = f'''
        <div class="color-picker-wrapper" data-widget="color-picker">
            <div class="color-preview" style="background-color: {value};"></div>
            <input {attrs_string}>
            <span class="color-hex-label">HEX</span>
        </div>
        '''
        return mark_safe(html)


class ImagePreviewWidget(forms.ClearableFileInput):
    """
    Виджет для загрузки изображений с превью
    Отображает текущее изображение и предпросмотр нового
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
        """Добавление URL изображения в контекст"""
        context = super().get_context(name, value, attrs)
        if value and hasattr(value, 'url'):
            context['image_url'] = value.url
            context['image_name'] = value.name
        else:
            context['image_url'] = None
            context['image_name'] = None
        return context

    def render(self, name, value, attrs=None, renderer=None):
        """Рендеринг виджета с превью"""
        context = self.get_context(name, value, attrs)

        # ✅ ИСПРАВЛЕНО: Правильный способ установки атрибутов для Django 5.2+
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs.update({
            'name': name,
        })

        attrs_string = ' '.join(f'{key}="{val}"' for key, val in final_attrs.items())

        html = f'''
        <div class="image-preview-wrapper" data-widget="image-preview">
        '''

        # Текущее изображение
        if context['image_url']:
            html += f'''
            <div class="current-image">
                <p class="image-label">Текущее изображение:</p>
                <img src="{context['image_url']}" alt="{context['image_name']}"
                     style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #e5e7eb;">
                <p class="image-name">{context['image_name']}</p>
            </div>
            '''

        # Поле загрузки
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
    """
    Виджет для предпросмотра CKEditor контента
    """
    class Media:
        css = {
            'all': ('admin/css/ckeditor-preview.css',)
        }

    def render(self, name, value, attrs=None, renderer=None):
        """Рендеринг с предпросмотром"""
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
