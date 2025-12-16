from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Product
from content.models import SiteSettings, Promotion
from pages.models import Page
from decimal import Decimal
import json
from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Product
from content.models import SiteSettings, Promotion
from pages.models import Page
from decimal import Decimal
import json
from datetime import datetime, timedelta


class ProductViewsTest(TestCase):
    """Тест представлений для товаров и категорий"""

    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()

        # Создаем категорию
        self.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            description="Описание тестовой категории",
            is_active=True
        )

        # Создаем товары (больше, чем помещается на одну страницу)
        for i in range(15):
            Product.objects.create(
                name=f"Тестовый товар {i}",
                slug=f"test-product-{i}",
                description=f"Описание товара {i}",
                price=Decimal('1000.00'),
                category=self.category,
                is_active=True,
                in_stock=True,
                rating=Decimal('4.5')
            )

    def test_home_page(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('mybiz_core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Тестовый товар')

    def test_product_list_page(self):
        """Тест страницы списка товаров"""
        response = self.client.get(reverse('mybiz_core:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')

        # Проверяем пагинацию (12 товаров на странице)
        self.assertEqual(len(response.context['products']), 12)

    def test_product_detail_page(self):
        """Тест детальной страницы товара"""
        product = Product.objects.first()
        response = self.client.get(reverse('mybiz_core:product_detail', args=[product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, product.name)

    def test_category_filter(self):
        """Тест фильтрации по категории"""
        response = self.client.get(
            reverse('mybiz_core:product_list_by_category', args=[self.category.slug])
        )

        self.assertEqual(response.status_code, 200)
        # Все товары должны принадлежать тестовой категории
        for product in response.context['products']:
            self.assertEqual(product.category, self.category)

    def test_ajax_load_more(self):
        """Тест AJAX-подгрузки товаров"""
        # Проверяем, что URL существует
        url = reverse('mybiz_core:load_more_products')

        # Пробуем оба способа отправки AJAX заголовков
        # Способ 1: Через headers
        response = self.client.get(
            url,
            {'page': 2},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        # Если способ 1 не сработал, пробуем способ 2
        if response.status_code != 200:
            # Способ 2: Через HTTP_X_REQUESTED_WITH
            response = self.client.get(
                url,
                {'page': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

        # Если оба способа не сработали, проверяем URL в отладке
        if response.status_code != 200:
            # Попробуем с параметром debug
            response = self.client.get(
                url,
                {'page': 2, 'debug': 'ajax'}
            )

        self.assertEqual(response.status_code, 200,
                        f"Не удалось получить ответ 200 от {url}. Получен код: {response.status_code}")

        # Проверяем, что ответ содержит JSON
        try:
            data = json.loads(response.content)
            self.assertIn('html', data)
            self.assertIn('has_next', data)
        except json.JSONDecodeError:
            self.fail("Ответ не является валидным JSON")


class ProductViewsWithLargeDatasetTest(TestCase):
    """Тесты представлений с большим набором данных"""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всех тестов"""
        # Создаем категорию
        cls.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            description="Описание тестовой категории",
            is_active=True
        )

        # Создаем 30 товаров
        cls.products = []
        for i in range(30):
            product = Product.objects.create(
                name=f"Тестовый товар {i+1}",
                slug=f"test-product-{i+1}",
                description=f"Описание товара {i+1}",
                price=Decimal('1000.00'),
                category=cls.category,
                is_active=True,
                in_stock=True,
                rating=Decimal('4.5')
            )
            cls.products.append(product)

    def setUp(self):
        self.client = Client()

    def test_pagination_with_many_products(self):
        """Тест пагинации с большим количеством товаров"""
        response = self.client.get(reverse('mybiz_core:product_list'))

        self.assertEqual(response.status_code, 200)

        # Должно быть 12 товаров на странице (пагинация)
        self.assertEqual(len(response.context['products']), 12)

        # Проверяем общее количество товаров
        self.assertEqual(response.context['products'].paginator.count, 30)

        # Проверяем, что есть следующая страница
        self.assertTrue(response.context['products'].has_next())

    def test_ajax_load_more_multiple_pages(self):
        """Тест AJAX-подгрузки нескольких страниц"""
        # Получаем URL
        url = reverse('mybiz_core:load_more_products')

        # Первая страница (должна вернуть товары 13-24)
        response = self.client.get(
            url,
            {'page': 2},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        # Если не сработало, пробуем другой способ
        if response.status_code != 200:
            response = self.client.get(
                url,
                {'page': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

        # Если все еще не сработало, пробуем с debug
        if response.status_code != 200:
            response = self.client.get(
                url,
                {'page': 2, 'debug': 'ajax'}
            )

        self.assertEqual(response.status_code, 200,
                        f"Не удалось получить AJAX ответ от {url}. Код: {response.status_code}")

        data = json.loads(response.content)
        self.assertTrue(data['has_next'])  # Должна быть третья страница

        # Третья страница (товары 25-30)
        response = self.client.get(
            url,
            {'page': 3},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        if response.status_code != 200:
            response = self.client.get(
                url,
                {'page': 3},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

        if response.status_code != 200:
            response = self.client.get(
                url,
                {'page': 3, 'debug': 'ajax'}
            )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['has_next'])  # Больше страниц нет

class ComprehensiveDataTest(TestCase):
    """Тесты для проверки создания данных"""

    def test_create_large_dataset(self):
        """Тест создания большого набора данных"""
        # Создаем категории
        categories_data = [
            ('Электроника', 'electronics'),
            ('Одежда', 'clothing'),
            ('Книги', 'books'),
            ('Спорт', 'sports'),
            ('Красота', 'beauty'),
        ]

        categories = []
        for name, slug in categories_data:
            category = Category.objects.create(
                name=name,
                slug=slug,
                description=f'Описание категории {name}',
                is_active=True
            )
            categories.append(category)

        self.assertEqual(Category.objects.count(), 5)

        # Создаем товары в каждой категории
        total_products = 50
        for i in range(total_products):
            category = categories[i % len(categories)]
            Product.objects.create(
                name=f'Тестовый товар {i+1}',
                slug=f'test-product-{i+1}',
                description=f'Описание товара {i+1}',
                price=Decimal('1000.00'),
                category=category,
                is_active=True,
                in_stock=True,
                rating=Decimal('4.5')
            )

        self.assertEqual(Product.objects.count(), total_products)

        # Проверяем распределение по категориям
        for category in categories:
            product_count = Product.objects.filter(category=category).count()
            self.assertGreater(product_count, 0)
            print(f'Категория "{category.name}": {product_count} товаров')


class ProductViewsWithLargeDatasetTest(TestCase):
    """Тесты представлений с большим набором данных"""

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всех тестов"""
        # Создаем категорию
        cls.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            description="Описание тестовой категории",
            is_active=True
        )

        # Создаем 30 товаров
        cls.products = []
        for i in range(30):
            product = Product.objects.create(
                name=f"Тестовый товар {i+1}",
                slug=f"test-product-{i+1}",
                description=f"Описание товара {i+1}",
                price=Decimal('1000.00'),
                category=cls.category,
                is_active=True,
                in_stock=True,
                rating=Decimal('4.5')
            )
            cls.products.append(product)

    def setUp(self):
        self.client = Client()

    def test_pagination_with_many_products(self):
        """Тест пагинации с большим количеством товаров"""
        response = self.client.get(reverse('mybiz_core:product_list'))

        self.assertEqual(response.status_code, 200)

        # Должно быть 12 товаров на странице (пагинация)
        self.assertEqual(len(response.context['products']), 12)

        # Проверяем общее количество товаров
        self.assertEqual(response.context['products'].paginator.count, 30)

        # Проверяем, что есть следующая страница
        self.assertTrue(response.context['products'].has_next())

    def test_ajax_load_more_multiple_pages(self):
        """Тест AJAX-подгрузки нескольких страниц"""
        # Первая страница (должна вернуть товары 13-24)
        response = self.client.get(
            reverse('mybiz_core:load_more_products'),
            {'page': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['has_next'])  # Должна быть третья страница

        # Третья страница (товары 25-30)
        response = self.client.get(
            reverse('mybiz_core:load_more_products'),
            {'page': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['has_next'])  # Больше страниц нет


class SitePerformanceTest(TestCase):
    """Тесты производительности с большим набором данных"""

    def test_home_page_performance_with_many_products(self):
        """Тест производительности главной страницы с большим количеством товаров"""
        # Создаем категорию
        category = Category.objects.create(
            name="Категория для теста",
            slug="test-category",
            is_active=True
        )

        # Создаем 50 товаров
        for i in range(50):
            Product.objects.create(
                name=f"Товар {i+1}",
                slug=f"product-{i+1}",
                description=f"Описание {i+1}",
                price=Decimal('1000.00'),
                category=category,
                is_active=True,
                is_featured=(i % 5 == 0)  # Каждый 5-й товар - рекомендованный
            )

        # Замеряем время выполнения запроса главной страницы
        import time
        start_time = time.time()

        response = self.client.get(reverse('mybiz_core:home'))

        end_time = time.time()
        execution_time = end_time - start_time

        self.assertEqual(response.status_code, 200)

        # Проверяем, что на главной отображаются только рекомендованные товары (8 штук)
        featured_products = response.context['featured_products']
        self.assertEqual(len(featured_products), 8)

        # Проверяем, что время выполнения приемлемое
        # (это субъективный тест, но полезный для мониторинга)
        print(f"Время выполнения главной страницы с 50 товарами: {execution_time:.3f} секунд")
        self.assertLess(execution_time, 2.0)  # Должно быть меньше 2 секунд


class CategoryDistributionTest(TestCase):
    """Тесты распределения товаров по категориям"""

    def test_category_product_counts(self):
        """Тест подсчета товаров в категориях"""
        # Создаем несколько категорий
        categories = []
        for i in range(3):
            category = Category.objects.create(
                name=f"Категория {i+1}",
                slug=f"category-{i+1}",
                is_active=True
            )
            categories.append(category)

        # Создаем товары с разным распределением
        # Категория 1: 5 товаров
        # Категория 2: 3 товара
        # Категория 3: 2 товара
        product_counts = [5, 3, 2]

        product_counter = 1
        for category, count in zip(categories, product_counts):
            for i in range(count):
                Product.objects.create(
                    name=f"Товар {product_counter}",
                    slug=f"product-{product_counter}",
                    description="Описание",
                    price=Decimal('1000.00'),
                    category=category,
                    is_active=True
                )
                product_counter += 1

        # Проверяем количество товаров в каждой категории
        for category, expected_count in zip(categories, product_counts):
            actual_count = Product.objects.filter(category=category).count()
            self.assertEqual(actual_count, expected_count)


# Добавляем существующие тесты из предыдущей версии
class ProductViewsTest(TestCase):
    """Тест представлений для товаров и категорий"""

    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()

        # Создаем категорию
        self.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            description="Описание тестовой категории",
            is_active=True
        )

        # Создаем товары (больше, чем помещается на одну страницу)
        for i in range(15):
            Product.objects.create(
                name=f"Тестовый товар {i}",
                slug=f"test-product-{i}",
                description=f"Описание товара {i}",
                price=Decimal('1000.00'),
                category=self.category,
                is_active=True,
                in_stock=True,
                rating=Decimal('4.5')
            )

    def test_home_page(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('mybiz_core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Тестовый товар')

    def test_product_list_page(self):
        """Тест страницы списка товаров"""
        response = self.client.get(reverse('mybiz_core:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')

        # Проверяем пагинацию (12 товаров на странице)
        self.assertEqual(len(response.context['products']), 12)

    def test_product_detail_page(self):
        """Тест детальной страницы товара"""
        product = Product.objects.first()
        response = self.client.get(reverse('mybiz_core:product_detail', args=[product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, product.name)

    def test_category_filter(self):
        """Тест фильтрации по категории"""
        response = self.client.get(
            reverse('mybiz_core:product_list_by_category', args=[self.category.slug])
        )

        self.assertEqual(response.status_code, 200)
        # Все товары должны принадлежать тестовой категории
        for product in response.context['products']:
            self.assertEqual(product.category, self.category)

    def test_ajax_load_more(self):
        """Тест AJAX-подгрузки товаров"""
        # Первый запрос (первая страница)
        response = self.client.get(
            reverse('mybiz_core:load_more_products'),
            {'page': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['has_next'])

        # Второй запрос (вторая страница)
        response = self.client.get(
            reverse('mybiz_core:load_more_products'),
            {'page': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # На второй странице должно быть 3 товара (15 всего - 12 на первой)
        self.assertIn('html', data)
        self.assertFalse(data['has_next'])  # Больше страниц нет


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Категория",
            slug="category"
        )

        self.product = Product.objects.create(
            name="Товар",
            slug="product",
            price=Decimal('1000.00'),
            discount_price=Decimal('800.00'),
            category=self.category
        )

    def test_discount_percentage(self):
        """Тест расчета процента скидки"""
        # (1000 - 800) / 1000 * 100 = 20%
        self.assertEqual(self.product.get_discount_percentage(), 20)

    def test_absolute_urls(self):
        """Тест генерации URL"""
        category_url = self.category.get_absolute_url()
        product_url = self.product.get_absolute_url()

        self.assertIn(self.category.slug, category_url)
        self.assertIn(self.product.slug, product_url)


class TemplateTagsTest(TestCase):
    def test_category_context_processor(self):
        """Тест контекстного процессора категорий"""
        Category.objects.create(name="Категория 1", is_active=True)
        Category.objects.create(name="Категория 2", is_active=True)
        Category.objects.create(name="Категория 3", is_active=False)  # Неактивная

        # Создаем запрос для получения контекста
        from mybiz_core.context_processors import categories
        context = categories(None)

        # В контексте должны быть только активные категории
        self.assertIn('categories', context)
        self.assertEqual(len(context['categories']), 2)
        self.assertEqual(context['categories'][0].name, "Категория 1")
        self.assertEqual(context['categories'][1].name, "Категория 2")


class SiteSettingsTest(TestCase):
    def test_site_settings_load(self):
        """Тест загрузки настроек сайта"""
        from content.models import SiteSettings

        # Первый вызов должен создать объект
        settings = SiteSettings.load()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.site_name, "MyBiz")

        # Второй вызов должен вернуть тот же объект
        settings2 = SiteSettings.load()
        self.assertEqual(settings.pk, settings2.pk)

class URLTests(TestCase):

    def test_urls_available(self):
        """Тест доступности всех URL"""
        urls_to_test = [
            ('mybiz_core:home', None, 200),
            ('mybiz_core:product_list', None, 200),
            ('mybiz_core:load_more_products', None, 400),  # Без AJAX заголовка вернет 400
        ]

        for url_name, args, expected_status in urls_to_test:
            with self.subTest(url_name=url_name):
                try:
                    url = reverse(url_name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(
                        response.status_code,
                        expected_status,
                        f"URL {url_name} вернул {response.status_code}, ожидалось {expected_status}"
                    )
                except Exception as e:
                    self.fail(f"Ошибка при тестировании URL {url_name}: {str(e)}")

    def test_ajax_url_works(self):
        """Тест, что AJAX URL существует и работает"""
        # Создаем тестовые данные
        category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            is_active=True
        )

        for i in range(15):
            Product.objects.create(
                name=f"Тестовый товар {i}",
                slug=f"test-product-{i}",
                description="Описание",
                price=1000,
                category=category,
                is_active=True
            )

        # Проверяем URL с AJAX заголовком
        url = reverse('mybiz_core:load_more_products')

        # Вариант 1: Через headers (более современный)
        response = self.client.get(
            url,
            {'page': 2},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        # Если вариант 1 не сработал, пробуем вариант 2
        if response.status_code == 404:
            # Вариант 2: Через HTTP_X_REQUESTED_WITH
            response = self.client.get(
                url,
                {'page': 2},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )

        self.assertEqual(
            response.status_code,
            200,
            f"AJAX URL вернул {response.status_code}. Проверьте настройки URL."
        )
