# mybiz_core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'created_at', 'image_preview')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'created_at', 'updated_at')

    def get_fieldsets(self, request, obj=None):
        """Определяем разные fieldsets для создания и редактирования"""
        if obj:  # Редактирование существующего товара
            fieldsets = (
                ('Основная информация', {
                    'fields': ('name', 'slug', 'category', 'description', 'price', 'discount_price')
                }),
                ('Изображения', {
                    'fields': ('image', 'image_preview')
                }),
                ('Статус и наличие', {
                    'fields': ('is_active', 'in_stock', 'is_new', 'is_featured')
                }),
                ('Дополнительная информация', {
                    'fields': ('sku', 'brand', 'short_description', 'old_price', 'stock')
                }),
                ('Рейтинги', {
                    'fields': ('rating', 'review_count')
                }),
                ('Системные поля (только чтение)', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)  # Сворачиваемый блок
                }),
            )
        else:  # Создание нового товара
            fieldsets = (
                ('Основная информация', {
                    'fields': ('name', 'slug', 'category', 'description', 'price', 'discount_price')
                }),
                ('Изображения', {
                    'fields': ('image',)
                }),
                ('Статус и наличие', {
                    'fields': ('is_active', 'in_stock', 'is_new', 'is_featured')
                }),
                ('Дополнительная информация', {
                    'fields': ('sku', 'brand', 'short_description', 'old_price', 'stock')
                }),
                ('Рейтинги', {
                    'fields': ('rating', 'review_count')
                }),
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        """Определяем поля только для чтения"""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj:  # При редактировании
            readonly_fields.append('created_at')
            readonly_fields.append('updated_at')

        readonly_fields.append('image_preview')
        return readonly_fields

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Превью'
