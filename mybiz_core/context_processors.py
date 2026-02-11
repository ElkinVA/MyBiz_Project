# mybiz_core/context_processors.py
from django.core.cache import cache
from .models import Category
import logging

logger = logging.getLogger(__name__)

def categories(request):
    """Добавляет категории в контекст всех шаблонов с кэшированием"""
    cache_key = 'categories'
    categories_list = cache.get(cache_key)

    if not categories_list:
        try:
            # ИСПРАВЛЕНО: убрана сортировка по несуществующему полю 'order'
            categories_list = Category.objects.filter(
                is_active=True
            ).prefetch_related('children')
            cache.set(cache_key, categories_list, 300)
        except Exception as e:
            logger.error(f"Failed to load categories: {e}")
            categories_list = []

    return {
        'categories': categories_list,
    }
