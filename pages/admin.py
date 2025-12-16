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
    list_display = ('title', 'slug', 'is_active', 'show_in_header', 'created_at')  # Добавили show_in_header
    list_filter = ('is_active', 'show_in_header', 'created_at')  # Добавили фильтр
    search_fields = ('title', 'content', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Отображение', {
            'fields': ('is_active', 'show_in_header')  # Добавили show_in_header
        }),
        ('Дополнительно', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Если объект уже существует
            readonly_fields.append('created_at')
            readonly_fields.append('updated_at')
        return readonly_fields
