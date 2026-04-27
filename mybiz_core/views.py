# mybiz_core/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product
from services.product_services import ProductService


def home(request):
    """Главная страница"""
    featured_products = ProductService.get_featured_products()
    total_products = Product.objects.filter(is_active=True).count()

    context = {
        'featured_products': featured_products,
        'total_products': total_products,
    }
    return render(request, 'home.html', context)


def product_list(request, category_slug=None):
    """Список товаров с фильтрацией по категории (из URL или GET-параметра)"""
    categories = Category.objects.filter(is_active=True).prefetch_related('children')

    # Поддержка выбора категории через GET-параметр 'category'
    if not category_slug:
        category_slug = request.GET.get('category')

    filters = {}
    if category_slug:
        filters['category_slug'] = category_slug
    search_query = request.GET.get('q')
    filters['min_price'] = request.GET.get('min_price')
    filters['max_price'] = request.GET.get('max_price')
    filters['in_stock'] = request.GET.get('in_stock') == 'true'
    filters['is_new'] = request.GET.get('is_new') == 'true'
    filters['has_discount'] = request.GET.get('has_discount') == 'true'

    products = ProductService.search_products(search_query or '', filters)

    sort_by = request.GET.get('sort', 'newest')
    products = ProductService.sort_products(products, sort_by)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)

    context = {
        'categories': categories,
        'current_category': current_category,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_products': products.count(),
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk, slug):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        pk=pk,
        slug=slug,
        is_active=True
    )

    related_products = ProductService.get_related_products(product)

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


# Обработчики ошибок
def bad_request(request, exception=None):
    return render(request, '400.html', status=400)

def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)

def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)

def server_error(request, exception=None):
    return render(request, '500.html', status=500)
