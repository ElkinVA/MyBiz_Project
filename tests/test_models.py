"""
Тесты для моделей mybiz_core.
"""
import pytest
from django.db import IntegrityError
from django.utils.text import slugify
from mybiz_core.models import Category, Product


@pytest.mark.django_db
class TestCategoryModel:
    """Тесты модели Category"""

    def test_category_creation(self, category):
        """Проверка создания категории"""
        assert category.name == 'Тестовая категория'
        assert category.slug == 'test-category'
        assert category.is_active is True
        assert str(category) == 'Тестовая категория'

    def test_category_slug_unique(self):
        """Проверка уникальности slug"""
        Category.objects.create(
            name='Категория 1',
            slug='unique-slug',
            is_active=True
        )
        with pytest.raises(IntegrityError):
            Category.objects.create(
                name='Категория 2',
                slug='unique-slug',
                is_active=True
            )

    def test_category_get_absolute_url(self, category):
        """Проверка генерации URL категории"""
        url = category.get_absolute_url()
        assert url == '/products/category/test-category/'

    def test_category_products_count_empty(self, category):
        """Проверка подсчета товаров в пустой категории"""
        assert category.products_count == 0

    def test_category_products_count_with_products(self, category, product):
        """Проверка подсчета товаров в категории с товарами"""
        assert category.products_count == 1

    def test_category_get_descendants_ids(self, category):
        """Проверка получения ID дочерних категорий"""
        child = Category.objects.create(
            name='Дочерняя категория',
            slug='child-category',
            parent=category,
            is_active=True
        )
        grandchild = Category.objects.create(
            name='Внучатая категория',
            slug='grandchild-category',
            parent=child,
            is_active=True
        )
        
        descendants_ids = category.get_descendants_ids()
        assert child.pk in descendants_ids
        assert grandchild.pk in descendants_ids


@pytest.mark.django_db
class TestProductModel:
    """Тесты модели Product"""

    def test_product_creation(self, product, category):
        """Проверка создания товара"""
        assert product.name == 'Тестовый товар'
        assert product.slug == 'test-product'
        assert product.category == category
        assert product.price == 1000.00
        assert product.sku == 'TEST-001'
        assert str(product) == 'Тестовый товар'

    def test_product_get_absolute_url(self, product):
        """Проверка генерации URL товара"""
        url = product.get_absolute_url()
        assert f'/products/{product.pk}/test-product/' in url

    def test_product_display_price_without_discount(self, product):
        """Проверка отображаемой цены без скидки"""
        assert product.display_price == product.price

    def test_product_display_price_with_discount(self, product):
        """Проверка отображаемой цены со скидкой"""
        product.discount_price = 800.00
        product.save()
        assert product.display_price == 800.00

    def test_product_get_discount_percentage_no_discount(self, product):
        """Проверка процента скидки без скидки"""
        assert product.get_discount_percentage() == 0

    def test_product_get_discount_percentage_with_discount(self, product):
        """Проверка процента скидки со скидкой"""
        product.price = 1000.00
        product.discount_price = 750.00
        product.save()
        assert product.get_discount_percentage() == 25

    def test_product_slug_unique(self, category):
        """Проверка уникальности slug товара"""
        Product.objects.create(
            name='Товар 1',
            slug='unique-product',
            category=category,
            price=500.00,
            sku='UNIQUE-001',
            is_active=True
        )
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Товар 2',
                slug='unique-product',
                category=category,
                price=600.00,
                sku='UNIQUE-002',
                is_active=True
            )

    def test_product_sku_unique(self, category):
        """Проверка уникальности SKU товара"""
        Product.objects.create(
            name='Товар 1',
            slug='product-1',
            category=category,
            price=500.00,
            sku='UNIQUE-SKU',
            is_active=True
        )
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Товар 2',
                slug='product-2',
                category=category,
                price=600.00,
                sku='UNIQUE-SKU',
                is_active=True
            )

    def test_product_is_featured_default(self, product):
        """Проверка значения is_featured по умолчанию"""
        assert product.is_featured is False

    def test_product_is_new_default(self, product):
        """Проверка значения is_new по умолчанию"""
        assert product.is_new is False
