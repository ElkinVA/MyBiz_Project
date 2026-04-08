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
                config_name='extends',  # 👈 расширенный редактор
                attrs={'class': 'django_ckeditor_5'}
            ),
        }


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = ('title', 'slug', 'show_in_header', 'show_in_footer', 'is_active', 'created_at')
    list_filter = ('is_active', 'show_in_header', 'show_in_footer')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)
    save_on_top = True  # 👈 Кнопки сохранения сверху
