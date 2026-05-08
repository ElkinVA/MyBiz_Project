# content/forms.py
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import SiteSettings, Promotion, StockNotification, NewsletterSubscriber
from .widgets import ColorPickerWidget, ImagePreviewWidget


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'site_name': CKEditor5Widget(config_name='extends'),
            'site_tagline': CKEditor5Widget(config_name='extends'),
            'featured_products_title': forms.TextInput(attrs={'class': 'vTextField'}),
            'featured_products_subtitle': forms.TextInput(attrs={'class': 'vTextField'}),
            'promotions_title': forms.TextInput(attrs={'class': 'vTextField'}),
            'promotions_subtitle': forms.TextInput(attrs={'class': 'vTextField'}),
            'welcome_text': CKEditor5Widget(config_name='extends'),
            'description': CKEditor5Widget(config_name='extends'),

            'primary_color': ColorPickerWidget(),
            'secondary_color': ColorPickerWidget(),
            'accent_color': ColorPickerWidget(),
            'text_color': ColorPickerWidget(),
            'background_color': ColorPickerWidget(),
            'header_footer_bg_color': ColorPickerWidget(),
            'header_footer_text_color': ColorPickerWidget(),
            'border_color': ColorPickerWidget(),

            'logo': ImagePreviewWidget(),
            'favicon': ImagePreviewWidget(),

            'contact_phone': forms.TextInput(attrs={'placeholder': '+7 (XXX) XXX-XX-XX', 'class': 'vTextField'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'example@domain.com', 'class': 'vTextField'}),
            'contact_address': forms.Textarea(attrs={'rows': 3, 'class': 'vLargeTextField'}),
            'meta_keywords': forms.Textarea(attrs={'rows': 3, 'placeholder': 'ключевое слово 1, ...', 'class': 'vLargeTextField'}),
        }

    def clean_primary_color(self):
        data = self.cleaned_data.get('primary_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def clean_secondary_color(self):
        data = self.cleaned_data.get('secondary_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def clean_accent_color(self):
        data = self.cleaned_data.get('accent_color')
        if data and not self._validate_hex_color(data):
            raise forms.ValidationError('Неверный формат HEX цвета.')
        return data

    def _validate_hex_color(self, value):
        import re
        return bool(re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value))


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'vTextField'}),
            'slug': forms.TextInput(attrs={'class': 'vTextField'}),
            'description': CKEditor5Widget(config_name='extends'),
            'short_description': forms.Textarea(attrs={'rows': 3, 'class': 'vLargeTextField'}),
            'button_text': forms.TextInput(attrs={'class': 'vTextField'}),
            'button_url': forms.URLInput(attrs={'class': 'vTextField'}),
            'image': ImagePreviewWidget(),
        }


class StockNotificationForm(forms.ModelForm):
    class Meta:
        model = StockNotification
        fields = ['email', 'product']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email', 'class': 'form-control'}),
        }


class NewsletterSubscriberForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email для рассылки', 'class': 'form-control'}),
        }
