from django.test import TestCase
from django.urls import reverse
from .models import Category, Product
from decimal import Decimal

class BasicSiteTest(TestCase):
    """Базовые тесты для проверки работы сайта"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            is_active=True
        )

        self.product = Product.objects.create(
            name="Тестовый товар",
            slug="test-product",
            description="Описание товара",
            price=Decimal('1000.00'),
            category=self.category,
            is_active=True,
            in_stock=True
        )

    def test_home_page(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('mybiz_core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_product_list(self):
        """Тест страницы товаров"""
        response = self.client.get(reverse('mybiz_core:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')

    def test_product_detail(self):
        """Тест детальной страницы товара"""
        response = self.client.get(reverse('mybiz_core:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')

    def test_category_page(self):
        """Тест страницы категории"""
        response = self.client.get(reverse('mybiz_core:product_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
