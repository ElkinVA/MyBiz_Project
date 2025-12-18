from django.contrib import admin
from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import Page


class PageForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Page
        fields = '__all__'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageForm
    list_display = ('title', 'slug', 'is_active', 'show_in_header', 'created_at')
    list_filter = ('is_active', 'show_in_header', 'created_at')
    search_fields = ('title', 'content', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')  # Поля только для чтения

    def get_fieldsets(self, request, obj=None):
        """Разные fieldsets для создания и редактирования"""
        if obj:  # Редактирование существующей страницы
            fieldsets = (
                ('Основная информация', {
                    'fields': ('title', 'slug', 'content', 'excerpt')
                }),
                ('SEO', {
                    'fields': ('meta_title', 'meta_description', 'meta_keywords')
                }),
                ('Отображение', {
                    'fields': ('is_active', 'show_in_header')
                }),
                ('Системные поля (только чтение)', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)  # Свернутый блок
                }),
            )
        else:  # Создание новой страницы
            fieldsets = (
                ('Основная информация', {
                    'fields': ('title', 'slug', 'content', 'excerpt')
                }),
                ('SEO', {
                    'fields': ('meta_title', 'meta_description', 'meta_keywords')
                }),
                ('Отображение', {
                    'fields': ('is_active', 'show_in_header')
                }),
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """Определяем поля только для чтения"""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj:  # При редактировании
            readonly_fields.append('created_at')
            readonly_fields.append('updated_at')

        return readonly_fields
