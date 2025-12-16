from .models import SiteSettings, Promotion
from pages.models import Page

def site_settings(request):
    """Добавляет настройки сайта в контекст всех шаблонов"""
    settings = SiteSettings.load()
    # Добавляем страницы для футера
    footer_pages = Page.objects.filter(is_active=True)[:4]
    return {
        'site_settings': settings,
        'pages': footer_pages
    }

def site_settings(request):
    """Добавляет настройки сайта в контекст всех шаблонов"""
    settings = SiteSettings.load()
    return {'site_settings': settings}

def promotions(request):
    """Добавляет активные промо-акции в контекст"""
    active_promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')[:3]
    return {'promotions': active_promotions}
