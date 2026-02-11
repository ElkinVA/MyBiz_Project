# content/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms
from .models import Promotion, SiteSettings
from .widgets import ColorPickerWidget


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = '__all__'
        widgets = {
            'description': CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'}
            ),
        }


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    form = PromotionForm
    list_display = ('title', 'is_active', 'start_date', 'end_date', 'image_preview')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="max-height: 200px;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Превью изображения'


class SiteSettingsForm(forms.ModelForm):
    # Добавляем поле для предпросмотра цветов
    color_preview = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'color-scheme-preview'
        }),
        label='Предпросмотр цветов',
        help_text='Выбранная цветовая схема'
    )

    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'color_scheme': forms.Select(attrs={'class': 'color-scheme-selector'}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'rows': 3}),
            'primary_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'primary'}),
            'secondary_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'secondary'}),
            'accent_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'accent'}),
            'text_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'text'}),
            'background_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'background'}),
            'header_bg_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'header_bg'}),
            'footer_bg_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'footer_bg'}),
            'hero_bg_color': ColorPickerWidget(attrs={'class': 'color-field', 'data-color-type': 'hero_bg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение для предпросмотра
        if self.instance and self.instance.pk:
            scheme_name = dict(self.instance.COLOR_SCHEME_CHOICES).get(
                self.instance.color_scheme, 'Пользовательская'
            )
            self.initial['color_preview'] = scheme_name


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display_links = None

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return HttpResponseRedirect(
            reverse('admin:content_sitesettings_change', args=[obj.id])
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('Основные настройки', {
                'fields': ('site_name', 'site_tagline', 'logo', 'favicon', 'hero_image')
            }),
            ('Цветовая палитра', {
                'fields': (
                    'color_scheme',
                    'color_preview',
                    'primary_color',
                    'secondary_color',
                    'accent_color',
                    'text_color',
                    'background_color',
                    'header_bg_color',
                    'footer_bg_color',
                    'hero_bg_color',
                ),
                'classes': ('wide', 'color-scheme-fields'),
                'description': '''
                    <div class="color-scheme-description">
                        <strong>🎨 Выберите цветовую схему сайта:</strong>
                        <p>Выберите готовую схему или настройте цвета вручную.</p>
                    </div>
                '''
            }),
            ('Контактная информация', {
                'fields': ('contact_email', 'contact_phone', 'contact_address', 'working_hours')
            }),
            ('Социальные сети', {
                'fields': (
                    ('telegram_url', 'telegram_visible'),
                    ('vk_url', 'vk_visible'),
                    ('max_url', 'max_visible'),
                    ('instagram_url', 'instagram_visible'),
                ),
                'description': '''
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-size: 13px;">
                        <strong>🔗 Настройка социальных сетей:</strong><br>
                        Для каждой соцсети укажите ссылку и включите/выключите отображение.
                    </div>
                '''
            }),
            ('SEO', {
                'fields': ('meta_title', 'meta_description', 'meta_keywords')
            }),
        )
        return fieldsets

    class Media:
        css = {
            'all': (
                'admin/css/color-picker.css',
                'admin/css/color-scheme.css',
            )
        }
        js = (
            'admin/js/color-picker.js',
            'admin/js/color-scheme.js',
        )
