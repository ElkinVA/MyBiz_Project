from .models import SiteSettings, Promotion
from pages.models import Page

def site_settings(request):
    """Добавляет настройки сайта в контекст всех шаблонов"""
    settings = SiteSettings.load()
    return {'site_settings': settings}

def promotions(request):
    """Добавляет активные промо-акции в контекст"""
    active_promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')[:3]
    return {'promotions': active_promotions}

def header_pages(request):
    """Добавляет страницы для шапки сайта"""
    pages = Page.get_header_pages()
    return {'header_pages': pages}
