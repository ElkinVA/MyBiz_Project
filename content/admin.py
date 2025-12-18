# content/admin.py
from django.contrib import admin
from django.utils.html import format_html
from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import Promotion, SiteSettings
from .widgets import ColorPickerWidget

class PromotionForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Promotion
        fields = '__all__'


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
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'meta_keywords': forms.Textarea(attrs={'rows': 3}),
            'primary_color': ColorPickerWidget(),
            'secondary_color': ColorPickerWidget(),
            'accent_color': ColorPickerWidget(),
            'text_color': ColorPickerWidget(),
            'background_color': ColorPickerWidget(),
            'header_bg_color': ColorPickerWidget(),
            'footer_bg_color': ColorPickerWidget(),
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm

    def get_fieldsets(self, request, obj=None):
        return (
            ('Основные настройки', {
                'fields': ('site_name', 'site_tagline', 'logo', 'favicon', 'hero_image')
            }),
            ('Цветовая палитра', {
                'fields': (
                    'primary_color',
                    'secondary_color',
                    'accent_color',
                    'text_color',
                    'background_color',
                    'header_bg_color',
                    'footer_bg_color',
                ),
                'classes': ('wide',),
                'description': '''
                    <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-bottom: 10px; font-size: 13px;">
                        <strong>🎨 Настройка цветов сайта:</strong><br>
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

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    class Media:
        css = {
            'all': ('admin/css/color-picker.css',)
        }
        js = ('admin/js/color-picker.js',)
