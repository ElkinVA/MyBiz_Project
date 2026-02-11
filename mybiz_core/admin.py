# mybiz_core/admin.py

from django.contrib import admin
from django.db.models import Count, Q
from .models import Category, Product
from django.utils.html import format_html

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_products_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        # Используем annotate для подсчета товаров в одной выборке
        queryset = super().get_queryset(request)
        return queryset.annotate(
            active_products_count=Count('products', filter=Q(products__is_active=True))
        )

    def get_products_count(self, obj):
        # Используем аннотированное поле вместо отдельного запроса
        return obj.active_products_count

    get_products_count.short_description = 'Количество активных товаров'
    get_products_count.admin_order_field = 'active_products_count' # Позволяет сортировать по этому полю

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('get_discount_percentage_display',) # Добавляем поле как readonly
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'short_description', 'image')
        }),
        ('Цены', {
            'fields': ('price', 'discount_price', 'get_discount_percentage_display')
        }),
        ('Дополнительно', {
            'fields': ('brand', 'stock', 'is_active', 'is_featured'),
            'classes': ('collapse',) # Сворачиваемая секция
        }),
    )

    def get_discount_percentage_display(self, obj):
        # Метод для отображения процента скидки в админке
        percentage = obj.get_discount_percentage()
        if percentage > 0:
            return format_html('<span style="color:red;">{}%</span>', percentage)
        return '-'

    get_discount_percentage_display.short_description = 'Скидка (%)'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
