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
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description', 'price')
        }),
        ('Изображения', {
            'fields': ('image', 'image_preview')
        }),
        ('Дополнительно', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = 'Превью'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Если объект уже существует
            readonly_fields.append('created_at')
            readonly_fields.append('updated_at')
        return readonly_fields
