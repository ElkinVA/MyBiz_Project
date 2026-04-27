# mybiz_core/context_processors.py
"""
Контекст-процессоры для mybiz_core приложения
"""
from django.core.cache import cache
from .models import Category, Product
from pages.models import Page


def categories(request):
    """
    Добавляет все активные категории в контекст
    Доступно на всём сайте
    """
    cache_key = 'all_active_categories'
    categories_list = cache.get(cache_key)

    if categories_list is None:
        categories_list = list(Category.objects.filter(is_active=True).order_by('name'))
        cache.set(cache_key, categories_list, 300)

    return {
        'categories': categories_list,
    }


def admin_dashboard_stats(request):
    """
    Добавляет статистику в контекст админ-панели
    Кэширует данные на 5 минут для производительности
    """
    if not request.path.startswith('/admin/'):
        return {}

    stats = cache.get('admin_dashboard_stats')

    if not stats:
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'inactive_products': Product.objects.filter(is_active=False).count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_pages': Page.objects.filter(is_active=True).count(),  # ← добавлено
        }

        # Кэширование на 5 минут
        cache.set('admin_dashboard_stats', stats, 300)

    return stats


def admin_user_info(request):
    """
    Добавляет информацию о пользователе в контекст админки
    """
    if not request.path.startswith('/admin/'):
        return {}

    return {
        'user_username': request.user.get_username() if request.user.is_authenticated else '',
        'user_is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
        'user_is_staff': request.user.is_staff if request.user.is_authenticated else False,
    }
