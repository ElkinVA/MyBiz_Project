# content/forms.py
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import SiteSettings, Promotion, StockNotification, NewsletterSubscriber
from .widgets import ColorPickerWidget, ImagePreviewWidget


class SiteSettingsForm(forms.ModelForm):
    """Форма для настроек сайта"""

    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            # Обычные текстовые поля (без HTML)
            'site_name': forms.TextInput(attrs={'class': 'vTextField'}),
            'site_tagline': forms.TextInput(attrs={'class': 'vTextField'}),
            'hero_heading_prefix': forms.TextInput(attrs={'class': 'vTextField'}),
            'hero_subtitle': forms.TextInput(attrs={'class': 'vTextField'}),
            'featured_products_title': forms.TextInput(attrs={'class': 'vTextField'}),
            'featured_products_subtitle': forms.TextInput(attrs={'class': 'vTextField'}),
            'promotions_title': forms.TextInput(attrs={'class': 'vTextField'}),
            'promotions_subtitle': forms.TextInput(attrs={'class': 'vTextField'}),
            
            # CKEditor поле для большого текста
            'welcome_text': CKEditor5Widget(config_name='extends'),
            'description': CKEditor5Widget(config_name='extends'),

            # Цветовые поля
            'primary_color': ColorPickerWidget(),
            'secondary_color': ColorPickerWidget(),
            'accent_color': ColorPickerWidget(),
            'text_color': ColorPickerWidget(),
            'background_color': ColorPickerWidget(),
            'header_bg_color': ColorPickerWidget(),
            'footer_bg_color': ColorPickerWidget(),
            'hero_bg_color': ColorPickerWidget(),
            'border_color': ColorPickerWidget(),

            # Изображения
            'logo': ImagePreviewWidget(),
            'favicon': ImagePreviewWidget(),
            'hero_image': ImagePreviewWidget(),

            # Обычные поля
            'contact_phone': forms.TextInput(attrs={
                'placeholder': '+7 (XXX) XXX-XX-XX',
                'class': 'vTextField'
            }),
            'contact_email': forms.EmailInput(attrs={
                'placeholder': 'example@domain.com',
                'class': 'vTextField'
            }),
            'contact_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'vLargeTextField'
            }),
            'meta_keywords': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'ключевое слово 1, ключевое слово 2, ...',
                'class': 'vLargeTextField'
            }),
        }

    def clean_primary_color(self):
        """Валидация основного цвета"""
        data = self.cleaned_data.get('primary_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def clean_secondary_color(self):
        """Валидация вторичного цвета"""
        data = self.cleaned_data.get('secondary_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def clean_accent_color(self):
        """Валидация акцентного цвета"""
        data = self.cleaned_data.get('accent_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def _validate_hex_color(self, value):
        """Проверка формата HEX цвета"""
        import re
        return bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value))


class PromotionForm(forms.ModelForm):
    """Форма для акций"""

    class Meta:
        model = Promotion
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'vTextField'}),
            'slug': forms.TextInput(attrs={'class': 'vTextField'}),
            'description': CKEditor5Widget(config_name='extends'),
            'short_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'vLargeTextField'
            }),
            'button_text': forms.TextInput(attrs={'class': 'vTextField'}),
            'button_url': forms.URLInput(attrs={'class': 'vTextField'}),
            'image': ImagePreviewWidget(),
            'icon': ImagePreviewWidget(),
        }


class StockNotificationForm(forms.ModelForm):
    """Форма для уведомлений о поступлении"""

    class Meta:
        model = StockNotification
        fields = ['email', 'product']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email',
                'class': 'form-control'
            }),
        }


class NewsletterSubscriberForm(forms.ModelForm):
    """Форма для подписки на рассылку"""

    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email для рассылки',
                'class': 'form-control'
            }),
        }