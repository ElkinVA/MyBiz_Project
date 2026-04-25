# content/context_processors.py
from django.core.cache import cache
from .models import SiteSettings
from pages.models import Page
import logging

logger = logging.getLogger(__name__)


def _is_admin_request(request):
    return request.path.startswith('/admin/')


def site_settings(request):
    if _is_admin_request(request):
        return {'site_settings': None}
    cache_key = 'site_settings'
    settings = cache.get(cache_key)
    if not settings:
        try:
            settings = SiteSettings.load()
            cache.set(cache_key, settings, 300)
        except Exception as e:
            logger.error(f"Failed to load site settings: {e}")
            settings = SiteSettings(
                site_name='MyBiz',
                site_tagline='Лучшие товары по доступным ценам',
                contact_email='',
                contact_phone='',
                contact_address='',
                primary_color='#3b82f6',
                secondary_color='#8b5cf6',
                accent_color='#10b981',
                text_color='#1f2937',
                background_color='#f9fafb',
                header_bg_color='#ffffff',
                footer_bg_color='#111827',
                hero_bg_color='#eff6ff',
                border_color='#e5e7eb',
            )
    return {'site_settings': settings}


def promotions(request):
    if _is_admin_request(request):
        return {'promotions': []}
    from .models import Promotion
    cache_key = 'active_promotions'
    promotions_list = cache.get(cache_key)
    if not promotions_list:
        promotions_list = Promotion.objects.filter(is_active=True).order_by('-created_at')[:3]
        cache.set(cache_key, promotions_list, 300)
    return {'promotions': promotions_list}


def header_pages(request):
    if _is_admin_request(request):
        return {'header_pages': []}
    cache_key = 'header_pages'
    pages = cache.get(cache_key)
    if not pages:
        pages = Page.get_header_pages()
        cache.set(cache_key, pages, 300)
    return {'header_pages': pages}


def footer_pages(request):
    """Возвращает информацию о наличии страниц privacy и offer для футера."""
    if _is_admin_request(request):
        return {'footer_pages': {'privacy': False, 'offer': False}}
    cache_key = 'footer_pages_existence'
    existence = cache.get(cache_key)
    if existence is None:
        existence = {
            'privacy': Page.objects.filter(slug='privacy', is_active=True).exists(),
            'offer': Page.objects.filter(slug='offer', is_active=True).exists(),
        }
        cache.set(cache_key, existence, 300)
    return {'footer_pages': existence}
