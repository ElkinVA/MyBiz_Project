from django.core.cache import cache
from .models import SiteSettings
from pages.models import Page
import logging

logger = logging.getLogger(__name__)

def site_settings(request):
    """Добавляет настройки сайта в контекст всех шаблонов с кэшированием"""
    cache_key = 'site_settings'
    settings = cache.get(cache_key)

    if not settings:
        try:
            settings = SiteSettings.load()
            cache.set(cache_key, settings, 300)
        except Exception as e:
            logger.error(f"Failed to load site settings: {e}")
            # Возвращаем объект-заглушку
            settings = type('obj', (object,), {
                'site_name': 'MyBiz',
                'site_tagline': '',
                'contact_email': '',
                'contact_phone': '',
                'contact_address': '',
                'get_visible_social_links': lambda: [],
            })()

    return {
        'site_settings': settings,
    }

def promotions(request):
    """Добавляет активные промо-акции в контекст"""
    from .models import Promotion
    cache_key = 'active_promotions'
    promotions = cache.get(cache_key)

    if not promotions:
        promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')[:3]
        cache.set(cache_key, promotions, 300)

    return {'promotions': promotions}

def header_pages(request):
    """Добавляет страницы для шапки сайта"""
    cache_key = 'header_pages'
    pages = cache.get(cache_key)

    if not pages:
        pages = Page.get_header_pages()
        cache.set(cache_key, pages, 300)

    return {'header_pages': pages}
