"""
Сервисный слой для бизнес-логики проекта MyBiz.
Здесь размещается вся бизнес-логика, отделенная от views.
"""
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

from mybiz_core.models import Category, Product
from content.models import SiteSettings, Promotion, NewsletterSubscriber, StockNotification

logger = logging.getLogger(__name__)
User = get_user_model()


class CategoryService:
    """Сервис для работы с категориями"""

    @staticmethod
    def get_active_categories():
        """Получает все активные категории с оптимизацией"""
        cache_key = 'active_categories'
        categories = cache.get(cache_key)
        
        if categories is None:
            categories = list(
                Category.objects.filter(is_active=True)
                .prefetch_related('children')
                .order_by('name')
            )
            cache.set(cache_key, categories, 300)
        
        return categories

    @staticmethod
    def get_category_with_products(category_slug):
        """Получает категорию с товарами"""
        from django.shortcuts import get_object_or_404
        
        category = get_object_or_404(
            Category.objects.select_related('parent'),
            slug=category_slug,
            is_active=True
        )
        
        return category

    @staticmethod
    def clear_cache():
        """Очищает кэш категорий"""
        cache.delete('active_categories')


class ProductService:
    """Сервис для работы с товарами"""

    @staticmethod
    def get_featured_products(limit=8):
        """Получает рекомендуемые товары"""
        cache_key = 'featured_products'
        products = cache.get(cache_key)
        
        if products is None:
            products = list(
                Product.objects.filter(
                    is_active=True,
                    is_featured=True
                ).select_related('category')[:limit]
            )
            cache.set(cache_key, products, 300)
        
        return products

    @staticmethod
    def get_new_products(limit=8):
        """Получает новые товары"""
        cache_key = 'new_products'
        products = cache.get(cache_key)
        
        if products is None:
            week_ago = timezone.now() - timedelta(days=7)
            products = list(
                Product.objects.filter(
                    is_active=True,
                    is_new=True,
                    created_at__gte=week_ago
                ).select_related('category')[:limit]
            )
            cache.set(cache_key, products, 300)
        
        return products

    @staticmethod
    def search_products(query, filters=None):
        """
        Поиск товаров с фильтрацией.
        
        Args:
            query: Поисковый запрос
            filters: dict с фильтрами (min_price, max_price, category_slug, in_stock, etc.)
        
        Returns:
            QuerySet товаров
        """
        from django.db.models import Q
        
        products = Product.objects.filter(is_active=True).select_related('category')
        
        # Поиск по названию и описанию
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(sku__icontains=query)
            )
        
        # Применение фильтров
        if filters:
            if 'min_price' in filters and filters['min_price']:
                products = products.filter(price__gte=filters['min_price'])
            
            if 'max_price' in filters and filters['max_price']:
                products = products.filter(price__lte=filters['max_price'])
            
            if 'category_slug' in filters and filters['category_slug']:
                products = products.filter(category__slug=filters['category_slug'])
            
            if 'in_stock' in filters and filters['in_stock']:
                products = products.filter(in_stock=True, stock__gt=0)
            
            if 'has_discount' in filters and filters['has_discount']:
                products = products.filter(discount_price__isnull=False)
            
            if 'is_new' in filters and filters['is_new']:
                products = products.filter(is_new=True)
        
        return products

    @staticmethod
    def sort_products(products, sort_by='newest'):
        """
        Сортировка товаров.
        
        Args:
            products: QuerySet товаров
            sort_by: поле для сортировки
        
        Returns:
            Отсортированный QuerySet
        """
        sort_mapping = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'popular': '-rating',
            'name_asc': 'name',
            'name_desc': '-name',
        }
        
        order_field = sort_mapping.get(sort_by, '-created_at')
        return products.order_by(order_field)

    @staticmethod
    def get_related_products(product, limit=4):
        """Получает похожие товары из той же категории"""
        return Product.objects.filter(
            category=product.category,
            is_active=True
        ).select_related('category').exclude(pk=product.pk)[:limit]

    @staticmethod
    def clear_cache():
        """Очищает кэш товаров"""
        cache.delete_many(['featured_products', 'new_products'])


class SiteSettingsService:
    """Сервис для работы с настройками сайта"""

    @staticmethod
    def load():
        """Загружает настройки сайта с кэшированием"""
        cache_key = 'site_settings'
        settings = cache.get(cache_key)
        
        if settings is None:
            settings = SiteSettings.load()
            cache.set(cache_key, settings, 600)
        
        return settings

    @staticmethod
    def clear_cache():
        """Очищает кэш настроек"""
        cache.delete('site_settings')


class PromotionService:
    """Сервис для работы с промо-акциями"""

    @staticmethod
    def get_active_promotions():
        """Получает активные промо-акции"""
        cache_key = 'active_promotions'
        promotions = cache.get(cache_key)
        
        if promotions is None:
            today = timezone.now().date()
            promotions = list(
                Promotion.objects.filter(
                    is_active=True,
                    start_date__lte=today
                ).filter(
                    models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)
                ).order_by('-created_at')
            )
            cache.set(cache_key, promotions, 300)
        
        return promotions

    @staticmethod
    def clear_cache():
        """Очищает кэш промо-акций"""
        cache.delete('active_promotions')


class NewsletterService:
    """Сервис для работы с рассылкой"""

    @staticmethod
    @transaction.atomic
    def subscribe(email):
        """
        Подписывает email на рассылку.
        
        Returns:
            tuple: (subscriber, created)
        """
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
        
        return subscriber, created

    @staticmethod
    def get_subscribers_count():
        """Получает количество активных подписчиков"""
        return NewsletterSubscriber.objects.filter(is_active=True).count()


class StockNotificationService:
    """Сервис для уведомлений о поступлении товаров"""

    @staticmethod
    @transaction.atomic
    def notify_product_arrival(product):
        """
        Отправляет уведомления о поступлении товара.
        
        Args:
            product: Товар, который поступил в продажу
        """
        notifications = StockNotification.objects.filter(
            product=product,
            is_notified=False
        ).select_related('product')
        
        for notification in notifications:
            # TODO: Реализовать отправку email
            logger.info(
                f"Отправка уведомления для {notification.email} "
                f"о товаре {product.name}"
            )
            notification.is_notified = True
            notification.notified_at = timezone.now()
            notification.save()

    @staticmethod
    @transaction.atomic
    def create_notification(product, email):
        """
        Создает уведомление о поступлении товара.
        
        Args:
            product: Товар
            email: Email для уведомления
        
        Returns:
            tuple: (notification, created)
        """
        notification, created = StockNotification.objects.get_or_create(
            product=product,
            email=email,
            defaults={'is_notified': False}
        )
        
        return notification, created
