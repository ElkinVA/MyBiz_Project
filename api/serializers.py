"""
REST API serializers для MyBiz проекта.
"""
from rest_framework import serializers
from mybiz_core.models import Category, Product
from content.models import Promotion, SiteSettings


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий"""
    products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent',
            'image', 'meta_title', 'meta_description',
            'is_active', 'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    """Упрощенный сериалайзер для списка категорий"""
    products_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'products_count']


class ProductSerializer(serializers.ModelSerializer):
    """Сериалайзер для товаров"""
    category = CategoryListSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    display_price = serializers.ReadOnlyField()
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_id',
            'short_description', 'description', 'price', 'discount_price',
            'display_price', 'discount_percentage', 'sku', 'brand',
            'image', 'rating', 'review_count', 'is_new', 'in_stock',
            'stock', 'is_active', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()


class ProductListSerializer(serializers.ModelSerializer):
    """Упрощенный сериалайзер для списка товаров"""
    category = CategoryListSerializer(read_only=True)
    display_price = serializers.ReadOnlyField()
    discount_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'price', 'discount_price',
            'display_price', 'discount_percentage', 'sku', 'image',
            'rating', 'is_new', 'in_stock', 'is_featured'
        ]
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()


class PromotionSerializer(serializers.ModelSerializer):
    """Сериалайзер для промо-акций"""
    class Meta:
        model = Promotion
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'button_text', 'button_url', 'is_active', 'start_date',
            'end_date', 'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Сериалайзер для настроек сайта"""
    social_links = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_tagline', 'color_scheme',
            'favicon', 'logo', 'hero_image',
            'primary_color', 'secondary_color', 'accent_color',
            'text_color', 'background_color', 'header_bg_color',
            'footer_bg_color', 'hero_bg_color', 'border_color',
            'welcome_text', 'hero_subtitle',
            'promotions_title', 'promotions_subtitle',
            'featured_products_title', 'featured_products_subtitle',
            'contact_email', 'contact_phone', 'contact_address',
            'working_hours', 'social_links',
            'meta_title', 'meta_description', 'meta_keywords'
        ]
    
    def get_social_links(self, obj):
        return obj.get_visible_social_links()
