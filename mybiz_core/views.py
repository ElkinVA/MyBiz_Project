from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.db.models import Q
from .models import Product, Category

@cache_page(60 * 5)
def home(request):
    """Главная страница сайта"""
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')[:8]

    context = {
        'featured_products': featured_products,
        'title': 'Главная',
    }
    return render(request, 'home.html', context)

def product_list(request, category_slug=None):
    """Список товаров с фильтрацией по категории и поиском"""
    category = None
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    products = Product.objects.filter(is_active=True).select_related('category')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Сортировка
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_options.get(sort_by, '-created_at'))

    # Пагинация
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
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'products/product_list.html', context)

@cache_page(60 * 5)
def product_detail(request, product_slug):
    """Детальная страница товара"""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=product_slug,
        is_active=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category')[:4]

    context = {
        'product': product,
        'related_products': related_products,
        'title': product.name,
    }
    return render(request, 'products/product_detail.html', context)

@require_GET
def load_more_products(request):
    """AJAX-подгрузка товаров"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'AJAX request required'}, status=400)

    page = request.GET.get('page', 2)
    category_slug = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    products = Product.objects.filter(is_active=True).select_related('category')

    if category_slug and category_slug != 'all':
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            products = products.filter(category=category)
        except Category.DoesNotExist:
            pass

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )

    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'name_desc': '-name',
        'newest': '-created_at',
    }
    products = products.order_by(sort_options.get(sort_by, '-created_at'))

    paginator = Paginator(products, 12)

    try:
        products_page = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        return JsonResponse({'html': '', 'has_next': False})

    html = render_to_string('products/product_items.html', {'products': products_page})

    return JsonResponse({
        'html': html,
        'has_next': products_page.has_next(),
        'next_page': products_page.next_page_number() if products_page.has_next() else None
    })
