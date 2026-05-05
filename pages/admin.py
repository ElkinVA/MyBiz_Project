# pages/admin.py
from django.contrib import admin, messages
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Page


class PageAdminForm(forms.ModelForm):
    """Форма для редактирования страниц с валидацией"""
    
    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'content': CKEditor5Widget(
                config_name='extends',
                attrs={'class': 'django_ckeditor_5'}
            ),
        }
    
    def clean_meta_description(self):
        """Валидация длины мета-описания (рекомендуется до 160 символов)"""
        meta_description = self.cleaned_data.get('meta_description', '')
        if meta_description and len(meta_description) > 160:
            raise forms.ValidationError(
                f"Мета-описание слишком длинное ({len(meta_description)} символов). "
                f"Рекомендуемая длина до 160 символов для оптимального отображения в поисковых системах."
            )
        return meta_description


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    
    # === Список страниц (changelist) ===
    list_display = (
        'title_with_status',
        'slug_link',
        'display_header',
        'display_footer',
        'status_badge',
        'created_at',
        'view_on_site_link',
    )
    
    list_filter = (
        'is_active',
        'show_in_header',
        'show_in_footer',
        ('created_at', admin.DateFieldListFilter),
    )
    
    search_fields = (
        'title',
        'content',
        'meta_title',
        'meta_description',
    )
    
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('title',)
    save_on_top = True
    date_hierarchy = 'created_at'
    
    # === Группировка полей в форме редактирования ===
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'slug', 'content', 'excerpt'),
            'description': 'Базовая информация о странице'
        }),
        ('Отображение', {
            'fields': ('show_in_header', 'show_in_footer', 'is_active'),
            'description': 'Настройки отображения страницы на сайте'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'description': 'Поисковая оптимизация (мета-теги)',
            'classes': ('collapse',)  # Сворачиваемая секция
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Системная информация (только для чтения)',
            'classes': ('collapse', 'readonly',)
        }),
    )
    
    # === Поля только для чтения ===
    readonly_fields = ('created_at', 'updated_at')
    
    # === Массовые действия ===
    actions = [
        'activate_pages',
        'deactivate_pages',
        'toggle_header_visibility',
        'toggle_footer_visibility',
        'export_selected_pages',
    ]
    
    # === Кастомные методы отображения ===
    
    def title_with_status(self, obj):
        """Заголовок с индикатором статуса"""
        status_icon = "✅" if obj.is_active else "❌"
        return format_html("{} <strong>{}</strong>", status_icon, obj.title)
    title_with_status.short_description = "Заголовок"
    title_with_status.admin_order_field = 'title'
    
    def slug_link(self, obj):
        """Slug с ссылкой на редактирование"""
        url = reverse('admin:pages_page_change', args=[obj.pk])
        return format_html('<a href="{}" style="color: #666;">{}</a>', url, obj.slug)
    slug_link.short_description = "URL"
    
    def display_header(self, obj):
        """Отображение в шапке с цветным бейджем"""
        if obj.show_in_header:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 3px;">✓ В шапке</span>'
            )
        return format_html(
            '<span style="background: #f8f9fa; color: #6c757d; padding: 2px 8px; border-radius: 3px;">—</span>'
        )
    display_header.short_description = "Шапка"
    display_header.admin_order_field = 'show_in_header'
    
    def display_footer(self, obj):
        """Отображение в подвале с цветным бейджем"""
        if obj.show_in_footer:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 3px;">✓ В подвале</span>'
            )
        return format_html(
            '<span style="background: #f8f9fa; color: #6c757d; padding: 2px 8px; border-radius: 3px;">—</span>'
        )
    display_footer.short_description = "Подвал"
    display_footer.admin_order_field = 'show_in_footer'
    
    def status_badge(self, obj):
        """Цветной бейдж статуса активности"""
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
                'АКТИВНА'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
            'НЕАКТИВНА'
        )
    status_badge.short_description = "Статус"
    status_badge.admin_order_field = 'is_active'
    
    def view_on_site_link(self, obj):
        """Ссылка на просмотр страницы на сайте"""
        if obj.is_active:
            url = obj.get_absolute_url()
            return format_html(
                '<a href="{}" target="_blank" style="color: #007bff; text-decoration: none;">↗ Открыть</a>',
                url
            )
        return format_html(
            '<span style="color: #6c757d;">⊘ Скрыта</span>'
        )
    view_on_site_link.short_description = "Просмотр"
    
    # === Массовые действия (реализация) ===
    
    @admin.action(description='Активировать выбранные страницы')
    def activate_pages(self, request, queryset):
        """Активирует выбранные страницы"""
        updated = queryset.update(is_active=True)
        self.clear_cache()
        message = f"Активировано {updated} стр." if updated > 1 else "Страница активирована"
        self.message_user(request, message, level=messages.SUCCESS)
    
    @admin.action(description='Деактивировать выбранные страницы')
    def deactivate_pages(self, request, queryset):
        """Деактивирует выбранные страницы"""
        updated = queryset.update(is_active=False)
        self.clear_cache()
        message = f"Деактивировано {updated} стр." if updated > 1 else "Страница деактивирована"
        self.message_user(request, message, level=messages.WARNING)
    
    @admin.action(description='Переключить отображение в шапке')
    def toggle_header_visibility(self, request, queryset):
        """Переключает отображение в шапке для выбранных страниц"""
        count = 0
        for page in queryset:
            page.show_in_header = not page.show_in_header
            page.save(update_fields=['show_in_header'])
            count += 1
        self.clear_cache()
        message = f"Обновлено отображение в шапке для {count} стр."
        self.message_user(request, message, level=messages.INFO)
    
    @admin.action(description='Переключить отображение в подвале')
    def toggle_footer_visibility(self, request, queryset):
        """Переключает отображение в подвале для выбранных страниц"""
        count = 0
        for page in queryset:
            page.show_in_footer = not page.show_in_footer
            page.save(update_fields=['show_in_footer'])
            count += 1
        self.clear_cache()
        message = f"Обновлено отображение в подвале для {count} стр."
        self.message_user(request, message, level=messages.INFO)
    
    @admin.action(description='Экспортировать выбранные страницы')
    def export_selected_pages(self, request, queryset):
        """Экспортирует информацию о выбранных страницах"""
        from io import StringIO
        import csv
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Заголовок', 'Slug', 'Активна', 'В шапке', 'В подвале', 'Создана'])
        
        for page in queryset:
            writer.writerow([
                page.id,
                page.title,
                page.slug,
                'Да' if page.is_active else 'Нет',
                'Да' if page.show_in_header else 'Нет',
                'Да' if page.show_in_footer else 'Нет',
                page.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        response = self.create_csv_response(output.getvalue(), 'pages_export.csv')
        return response
    
    def create_csv_response(self, csv_data, filename):
        """Создаёт HTTP-ответ с CSV файлом"""
        from django.http import HttpResponse
        response = HttpResponse(csv_data, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write('\ufeff')  # BOM для корректного отображения кириллицы в Excel
        return response
    
    # === Вспомогательные методы ===
    
    def clear_cache(self):
        """Очищает кэш страниц"""
        from django.core.cache import cache
        cache.delete('header_pages')
        cache.delete('footer_pages')
    
    def get_queryset(self, request):
        """Добавляет статистику в queryset"""
        qs = super().get_queryset(request)
        return qs
    
    def changelist_view(self, request, extra_context=None):
        """Добавляет контекст со статистикой"""
        extra_context = extra_context or {}
        extra_context['page_stats'] = {
            'total': Page.objects.count(),
            'active': Page.objects.filter(is_active=True).count(),
            'inactive': Page.objects.filter(is_active=False).count(),
            'in_header': Page.objects.filter(show_in_header=True, is_active=True).count(),
            'in_footer': Page.objects.filter(show_in_footer=True, is_active=True).count(),
        }
        return super().changelist_view(request, extra_context=extra_context)
    
    # === Медиа (подключение дополнительных стилей) ===
    class Media:
        css = {
            'all': ('admin/css/pages_admin.css',)
        }
