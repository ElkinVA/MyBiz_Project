# pages/admin.py
from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Page


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(
                config_name='extends',
                attrs={'class': 'django_ckeditor_5'}
            ),
        }


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    
    # Список: только самое важное
    list_display = ('title', 'slug_preview', 'is_active', 'show_in_header', 'show_in_footer')
    list_filter = ('is_active', 'show_in_header', 'show_in_footer')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)
    save_on_top = True
    
    # Группировка полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug'),
            'description': 'Заголовок и URL-адрес страницы'
        }),
        ('Содержание', {
            'fields': ('content',),
            'description': 'Текст страницы с форматированием'
        }),
        ('Отображение', {
            'fields': ('is_active', 'show_in_header', 'show_in_footer'),
            'description': 'Где и как показывать страницу'
        }),
        ('SEO-настройки', {
            'fields': ('excerpt', 'meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),  # Скрытая секция
            'description': 'Мета-теги для поисковых систем (необязательно)'
        }),
    )
    
    def slug_preview(self, obj):
        """Краткое отображение slug"""
        return f"/{obj.slug}/"
    slug_preview.short_description = "URL"
    slug_preview.ordering = 'slug'
