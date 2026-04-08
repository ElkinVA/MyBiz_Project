# mybiz_core/admin.py
from django.contrib import admin
from django.db.models import Count, Q, F
from django.utils.html import format_html
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from django.core.cache import cache
from .models import Category, Product


class ProductForm(forms.ModelForm):
    """Форма для товара с CKEditor"""

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': CKEditor5Widget(config_name='extends'),
            'short_description': forms.Textarea(attrs={'rows': 3}),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    list_display = ['name', 'slug', 'products_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description', 'slug']
    search_help_text = 'Поиск по названию, описанию или slug категории'
    list_select_related = ['parent']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('📁 Основная информация', {
            'fields': ('name', 'slug', 'parent', 'description'),
            'classes': ('wide',)
        }),
        ('📊 SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('⚙️ Статус', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
        ('📅 Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def products_count(self, obj):
        """Количество товаров в категории"""
        cache_key = f'category_{obj.pk}_products_count'
        count = cache.get(cache_key)
        if count is None:
            count = obj.products_count
            cache.set(cache_key, count, 300)
        return count
    products_count.short_description = 'Товаров'
    products_count.admin_order_field = 'products_count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    form = ProductForm

    # Улучшенное отображение списка
    list_display = [
        'display_product_card',
        'category',
        'display_price',
        'is_active',
        'is_featured',
        'stock_status',
        'created_at'
    ]

    # Улучшенные фильтры
    list_filter = [
        ('category', admin.RelatedOnlyFieldListFilter),
        ('is_active', admin.BooleanFieldListFilter),
        ('is_featured', admin.BooleanFieldListFilter),
        ('is_new', admin.BooleanFieldListFilter),
        ('in_stock', admin.BooleanFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    ]

    # Поиск с дополнительными полями
    search_fields = ['name', 'brand', 'sku', 'short_description']
    search_help_text = 'Поиск по названию, бренду, артикулу или описанию'

    # Предзаполненные поля
    prepopulated_fields = {'slug': ('name',)}

    # Автозаполнение для ForeignKey
    autocomplete_fields = ['category']

    # Read-only поля - ТОЛЬКО существующие в модели
    readonly_fields = ['created_at', 'updated_at']

    # Группировка полей
    fieldsets = (
        ('📦 Основная информация', {
            'fields': ('name', 'slug', 'category', 'brand'),
            'classes': ('wide',)
        }),
        ('💰 Цена и скидки', {
            'fields': ('price', 'discount_price'),
            'classes': ('wide', 'collapse')
        }),
        ('📝 Описания', {
            'fields': ('short_description', 'description'),
            'classes': ('wide',)
        }),
        ('📊 Статус и наличие', {
            'fields': ('is_active', 'is_featured', 'is_new', 'in_stock', 'stock'),
            'classes': ('wide', 'collapse')
        }),
        ('🖼️ Изображения', {
            'fields': ('image',),
            'classes': ('wide', 'collapse')
        }),
        ('📈 Рейтинги', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('📅 Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Действия в списке
    actions = [
        'make_featured',
        'make_not_featured',
        'activate_products',
        'deactivate_products',
        'export_selected_products'
    ]

    ordering = ['-created_at']
    list_per_page = 25
    list_select_related = ['category']
    date_hierarchy = 'created_at'

    # Методы для отображения
    def display_product_card(self, obj):
        """Отображение товара с изображением"""
        if obj.image:
            return format_html(
                '<div style="display:flex;align-items:center;gap:10px;">'
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:6px;">'
                '<span>{}</span></div>',
                obj.image.url,
                obj.name
            )
        return obj.name
    display_product_card.short_description = 'Товар'

    def display_price(self, obj):
        """Отображение цены со скидкой"""
        if obj.discount_price:
            return format_html(
                '<span style="color: #ef4444; font-weight: bold;">{} ₽</span> '
                '<span style="color: #9ca3af; text-decoration: line-through;">{} ₽</span>',
                obj.discount_price,
                obj.price
            )
        return format_html('<span>{} ₽</span>', obj.price)
    display_price.short_description = 'Цена'

    def stock_status(self, obj):
        """Статус наличия"""
        if obj.in_stock and obj.stock > 10:
            return format_html(
                '<span style="color: #10b981;">● В наличии ({})</span>',
                obj.stock
            )
        elif obj.in_stock and obj.stock > 0:
            return format_html(
                '<span style="color: #f59e0b;">● Мало ({})</span>',
                obj.stock
            )
        return format_html('<span style="color: #ef4444;">● Нет в наличии</span>')
    stock_status.short_description = 'Статус'

    # Массовые действия
    def make_featured(self, request, queryset):
        """Отметить как популярные"""
        queryset.update(is_featured=True)
        self.message_user(
            request,
            f'{queryset.count()} товаров отмечены как популярные',
            level='success'
        )
    make_featured.short_description = '⭐ Отметить как популярные'

    def make_not_featured(self, request, queryset):
        """Убрать из популярных"""
        queryset.update(is_featured=False)
        self.message_user(
            request,
            f'{queryset.count()} товаров убраны из популярных',
            level='info'
        )
    make_not_featured.short_description = '⭐ Убрать из популярных'

    def activate_products(self, request, queryset):
        """Активировать товары"""
        queryset.update(is_active=True)
        self.message_user(
            request,
            f'{queryset.count()} товаров активированы',
            level='success'
        )
    activate_products.short_description = '✅ Активировать'

    def deactivate_products(self, request, queryset):
        """Деактивировать товары"""
        queryset.update(is_active=False)
        self.message_user(
            request,
            f'{queryset.count()} товаров деактивированы',
            level='warning'
        )
    deactivate_products.short_description = '❌ Деактивировать'

    def export_selected_products(self, request, queryset):
        """Экспорт в CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        response.write('\ufeff')  # BOM для Excel

        writer = csv.writer(response)
        writer.writerow(['Название', 'Артикул', 'Цена', 'Цена со скидкой', 'Категория', 'Наличие'])

        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.sku,
                obj.price,
                obj.discount_price or '',
                obj.category.name if obj.category else '',
                'Да' if obj.in_stock else 'Нет'
            ])

        return response
    export_selected_products.short_description = '📥 Экспорт в CSV'
