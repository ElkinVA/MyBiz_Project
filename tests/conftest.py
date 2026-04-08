"""
Конфигурация pytest для Django проекта MyBiz.
"""
import os
import django
from pathlib import Path

# Настройка Django перед запуском тестов
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Инициализация Django
django.setup()


# Фикстуры для всего проекта
import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from mybiz_core.models import Category, Product
from content.models import SiteSettings, Promotion

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache():
    """Очищает кэш после каждого теста"""
    yield
    cache.clear()


@pytest.fixture
def user(db):
    """Создает обычного пользователя для тестов"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def superuser(db):
    """Создает суперпользователя для тестов"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def category(db):
    """Создает категорию для тестов"""
    return Category.objects.create(
        name='Тестовая категория',
        slug='test-category',
        description='Описание тестовой категории',
        is_active=True
    )


@pytest.fixture
def product(db, category):
    """Создает товар для тестов"""
    return Product.objects.create(
        name='Тестовый товар',
        slug='test-product',
        category=category,
        price=1000.00,
        sku='TEST-001',
        is_active=True,
        in_stock=True,
        stock=10
    )


@pytest.fixture
def site_settings(db):
    """Создает настройки сайта для тестов"""
    return SiteSettings.load()


@pytest.fixture
def promotion(db):
    """Создает промо-акцию для тестов"""
    from io import BytesIO
    from PIL import Image
    
    # Создаем тестовое изображение
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    return Promotion.objects.create(
        title='Тестовая акция',
        slug='test-promotion',
        description='Описание акции',
        is_active=True,
        image__content=img_io,
        image__name='test.jpg'
    )
