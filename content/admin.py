from django.contrib import admin
from django.utils.html import format_html
from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import Promotion, SiteSettings


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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'contact_phone')
    fieldsets = (
        ('Основные настройки', {
            'fields': ('site_name', 'site_tagline', 'logo', 'favicon', 'hero_image')
        }),
        ('Контактная информация', {
            'fields': ('contact_email', 'contact_phone', 'contact_address', 'working_hours')
        }),
        ('Социальные сети', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
    )

    def has_add_permission(self, request):
        # Разрешаем только один объект настроек
        return not SiteSettings.objects.exists()
