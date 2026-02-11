# mybiz_core/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product


def home(request):
    """Главная страница"""
    # Получаем featured_products из базы данных
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    )[:8]  # Ограничиваем 8 товарами

    # Получаем общее количество активных товаров
    total_products = Product.objects.filter(is_active=True).count()

    context = {
        'featured_products': featured_products,
        'total_products': total_products,
        # promotions и header_pages уже добавлены через context_processors
    }

    return render(request, 'home.html', context)


def product_list(request, category_slug=None):
    """Список товаров с фильтрацией по категории"""
    # ИСПРАВЛЕНО: убрана сортировка по 'order'
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)

    # Фильтрация по категории
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)

    # Поиск по названию
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )

    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass

    # Фильтрация по наличию
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products = products.filter(in_stock=True)

    # Фильтрация по новинкам
    is_new = request.GET.get('is_new')
    if is_new == 'true':
        products = products.filter(is_new=True)

    # Фильтрация по скидкам
    has_discount = request.GET.get('has_discount')
    if has_discount == 'true':
        products = products.filter(discount_price__isnull=False)

    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')

    # Пагинация
    paginator = Paginator(products, 12)  # 12 товаров на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'current_category': current_category,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_products': products.count(),
    }

    # ИСПРАВЛЕНО: правильный путь к шаблону
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk, slug):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk,
        slug=slug,
        is_active=True
    )

    # Похожие товары (из той же категории)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)

def about(request):
    """Страница 'О нас'"""
    site_settings = SiteSettings.load()
    return render(request, 'mybiz_core/about.html', {
        'site_settings': site_settings,
    })

def contact(request):
    """Страница 'Контакты'"""
    site_settings = SiteSettings.load()
    return render(request, 'mybiz_core/contact.html', {
        'site_settings': site_settings,
    })


# Обработчики ошибок
def bad_request(request, exception=None):
    return render(request, '400.html', status=400)


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


def server_error(request, exception=None):
    return render(request, '500.html', status=500)
