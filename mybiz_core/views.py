from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from .models import Product, Category
import json

def home(request):
    """Главная страница сайта"""
    # Получаем последние активные товары для главной страницы
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    context = {
        'featured_products': featured_products,
        'title': 'Главная',
    }
    return render(request, 'home.html', context)

def product_list(request, category_slug=None):
    """Список товаров с возможностью фильтрации по категории"""
    category = None

    # ИСПРАВЛЕНИЕ: Всегда инициализируем products
    products = Product.objects.filter(is_active=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    # Пагинация - 12 товаров на страницу
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'products': products_page,
        'title': category.name if category else 'Все товары',
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)

    # Получаем похожие товары из той же категории
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'title': product.name,
    }
    return render(request, 'products/product_detail.html', context)

@require_GET
def load_more_products(request):
    """AJAX-представление для подгрузки товаров (кнопка 'Показать ещё')"""
    # Проверяем, является ли запрос AJAX
    # Способ 1: Через headers (для современных клиентов)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Способ 2: Через META (для старых клиентов и тестов Django)
    if not is_ajax:
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    # Способ 3: Для отладки и тестов - параметр ?debug=ajax
    debug_mode = request.GET.get('debug') == 'ajax'

    if is_ajax or debug_mode:
        page = request.GET.get('page', 2)  # По умолчанию загружаем вторую страницу
        category_slug = request.GET.get('category', None)

        products = Product.objects.filter(is_active=True)

        if category_slug and category_slug != 'all':
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                products = products.filter(category=category)
            except Category.DoesNotExist:
                category = None

        paginator = Paginator(products, 12)

        try:
            products_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger):
            return JsonResponse({'html': '', 'has_next': False, 'next_page': None})

        # Рендерим только HTML с товарами
        html = render_to_string('products/product_items.html', {'products': products_page})

        return JsonResponse({
            'html': html,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None
        })

    # Если запрос не AJAX, возвращаем ошибку 400
    return JsonResponse({
        'error': 'This endpoint requires an AJAX request',
        'detail': 'Set X-Requested-With header to XMLHttpRequest'
    }, status=400)
