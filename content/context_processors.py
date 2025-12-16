from .models import SiteSettings, Promotion
from pages.models import Page

def site_settings(request):
    """Добавляет настройки сайта и страницы для футера в контекст всех шаблонов"""
    settings = SiteSettings.load()
    footer_pages = Page.get_footer_pages()  # Используем метод модели
    return {
        'site_settings': settings,
        'pages': footer_pages
    }

def promotions(request):
    """Добавляет активные промо-акции в контекст"""
    active_promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')[:3]
    return {'promotions': active_promotions}
