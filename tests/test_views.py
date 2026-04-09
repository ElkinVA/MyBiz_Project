"""
Тесты для views mybiz_core.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from mybiz_core.models import Category, Product

User = get_user_model()


@pytest.mark.django_db
class TestHomeView:
    """Тесты главной страницы"""

    def test_home_view_status_code(self, client):
        """Проверка статуса главной страницы"""
        response = client.get(reverse('mybiz_core:home'))
        assert response.status_code == 200

    def test_home_view_template_used(self, client):
        """Проверка используемого шаблона"""
        response = client.get(reverse('mybiz_core:home'))
        # Проверяем, что шаблон home.html использовался для рендеринга
        assert 'home.html' in [t.name for t in response.templates]

    def test_home_view_context_featured_products(self, client, product):
        """Проверка контекста с рекомендуемыми товарами"""
        product.is_featured = True
        product.save()
        
        response = client.get(reverse('mybiz_core:home'))
        assert 'featured_products' in response.context
        assert product in response.context['featured_products']


@pytest.mark.django_db
class TestProductListView:
    """Тесты списка товаров"""

    def test_product_list_view_status_code(self, client):
        """Проверка статуса страницы списка товаров"""
        response = client.get(reverse('mybiz_core:product_list'))
        assert response.status_code == 200

    def test_product_list_view_with_category(self, client, category, product):
        """Проверка фильтрации по категории"""
        response = client.get(
            reverse('mybiz_core:product_list_by_category', 
                   kwargs={'category_slug': category.slug})
        )
        assert response.status_code == 200
        assert product in response.context['products']

    def test_product_list_view_search(self, client, product):
        """Проверка поиска товаров"""
        response = client.get(f"{reverse('mybiz_core:product_list')}?q={product.name}")
        assert response.status_code == 200
        assert product in response.context['products']

    def test_product_list_view_filter_price(self, client, product):
        """Проверка фильтрации по цене"""
        response = client.get(
            f"{reverse('mybiz_core:product_list')}?min_price=500&max_price=1500"
        )
        assert response.status_code == 200
        assert product in response.context['products']

    def test_product_list_view_filter_in_stock(self, client, product):
        """Проверка фильтрации по наличию"""
        response = client.get(
            f"{reverse('mybiz_core:product_list')}?in_stock=true"
        )
        assert response.status_code == 200

    def test_product_list_view_sorting(self, client, product):
        """Проверка сортировки товаров"""
        response = client.get(
            f"{reverse('mybiz_core:product_list')}?sort=price_asc"
        )
        assert response.status_code == 200
        assert response.context['sort_by'] == 'price_asc'


@pytest.mark.django_db
class TestProductDetailView:
    """Тесты детальной страницы товара"""

    def test_product_detail_view_status_code(self, client, product):
        """Проверка статуса страницы товара"""
        response = client.get(
            reverse('mybiz_core:product_detail', 
                   kwargs={'pk': product.pk, 'slug': product.slug})
        )
        assert response.status_code == 200

    def test_product_detail_view_context(self, client, product):
        """Проверка контекста страницы товара"""
        response = client.get(
            reverse('mybiz_core:product_detail', 
                   kwargs={'pk': product.pk, 'slug': product.slug})
        )
        assert response.context['product'] == product

    def test_product_detail_view_related_products(self, client, product, category):
        """Проверка похожих товаров"""
        related_product = Product.objects.create(
            name='Похожий товар',
            slug='related-product',
            category=category,
            price=1200.00,
            sku='RELATED-001',
            is_active=True
        )
        
        response = client.get(
            reverse('mybiz_core:product_detail', 
                   kwargs={'pk': product.pk, 'slug': product.slug})
        )
        assert 'related_products' in response.context


@pytest.mark.django_db
class TestErrorViews:
    """Тесты страниц ошибок"""

    def test_404_view(self, client):
        """Проверка страницы 404"""
        response = client.get('/nonexistent-page/')
        assert response.status_code == 404
