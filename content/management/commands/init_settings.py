# content/management/commands/init_settings.py - объединенный файл
from django.core.management.base import BaseCommand
from content.models import SiteSettings
from mybiz_core.models import Category, Product
from pages.models import Page
import random
from decimal import Decimal
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Инициализирует базовые настройки сайта и тестовые данные'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Пропустить создание тестовых данных',
        )

    def handle(self, *args, **options):
        self.stdout.write("Начинаем инициализацию проекта MyBiz...")

        # 1. Создаем настройки сайта
        self.create_site_settings()

        if not options['skip_data']:
            # 2. Создаем тестовые данные
            self.create_test_categories()
            self.create_test_products()
            self.create_test_pages()
            self.stdout.write(self.style.SUCCESS('✅ Тестовые данные созданы'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Создание тестовых данных пропущено'))

        self.stdout.write(self.style.SUCCESS('🎉 Инициализация проекта завершена!'))

    def create_site_settings(self):
        """Создает или обновляет настройки сайта"""
        try:
            settings = SiteSettings.load()

            # Обновляем только если это новая запись
            if settings._state.adding:
                settings.site_name = 'MyBiz Витрина'
                settings.site_tagline = 'Лучшие товары по доступным ценам'
                settings.contact_email = 'info@mybiz.ru'
                settings.contact_phone = '+7 (999) 123-45-67'
                settings.contact_address = 'Москва, ул. Примерная, д. 1'
                settings.working_hours = 'Пн-Пт: 9:00-18:00, Сб: 10:00-16:00'
                settings.telegram_url = 'https://t.me/mybiz'
                settings.vk_url = 'https://vk.com/mybiz'
                settings.max_url = 'https://max.mail.ru/'
                settings.instagram_url = 'https://instagram.com/mybiz'
                settings.meta_description = 'Интернет-магазин качественных товаров'
                settings.meta_keywords = 'магазин, товары, купить, онлайн, доставка'
                settings.color_scheme = 'wood'
                settings.save()

                self.stdout.write(self.style.SUCCESS('✓ Настройки сайта созданы'))
            else:
                self.stdout.write(self.style.WARNING('✓ Настройки сайта уже существуют'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка создания настроек: {e}'))

    def create_test_categories(self):
        """Создает тестовые категории"""
        categories_data = [
            {'name': 'Электроника', 'slug': 'electronics'},
            {'name': 'Смартфоны', 'slug': 'smartphones'},
            {'name': 'Ноутбуки', 'slug': 'laptops'},
            {'name': 'Одежда', 'slug': 'clothing'},
            {'name': 'Обувь', 'slug': 'shoes'},
            {'name': 'Книги', 'slug': 'books'},
            {'name': 'Спорт', 'slug': 'sports'},
            {'name': 'Красота', 'slug': 'beauty'},
        ]

        created = 0
        for cat_data in categories_data:
            category, created_flag = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': f'Категория {cat_data["name"]}. Широкий выбор товаров.',
                    'is_active': True,
                    'order': created + 1
                }
            )
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {created} категорий'))

    def create_test_products(self):
        """Создает тестовые товары"""
        # Удаляем старые тестовые товары (опционально)
        Product.objects.all().delete()

        categories = Category.objects.all()
        if not categories:
            self.stdout.write(self.style.WARNING('⚠️ Нет категорий для создания товаров'))
            return

        product_names = [
            'Смартфон', 'Ноутбук', 'Наушники', 'Часы', 'Планшет',
            'Футболка', 'Джинсы', 'Куртка', 'Кроссовки', 'Рюкзак',
            'Книга', 'Игра', 'Косметика', 'Аксессуар', 'Техника'
        ]

        created = 0
        for i in range(50):  # Создаем 50 тестовых товаров
            category = random.choice(categories)
            name = f'{random.choice(product_names)} {i+1}'
            price = Decimal(random.randint(1000, 50000))

            # 30% товаров со скидкой
            discount_price = None
            if random.random() < 0.3:
                discount_price = price * Decimal('0.8')

            product = Product.objects.create(
                name=name,
                category=category,
                price=price,
                discount_price=discount_price,
                short_description=f'Тестовый товар {i+1}',
                description=f'<p>Описание тестового товара {i+1}. Высокое качество.</p>',
                sku=f'TEST{i+1:04d}',
                brand=random.choice(['Brand A', 'Brand B', 'Brand C', '']),
                rating=Decimal(random.randint(30, 50)) / 10,
                review_count=random.randint(0, 100),
                is_new=random.random() < 0.2,
                in_stock=random.random() < 0.8,
                stock=random.randint(0, 100) if random.random() < 0.8 else 0,
                is_active=True,
                is_featured=random.random() < 0.3,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {created} тестовых товаров'))

    def create_test_pages(self):
        """Создает тестовые страницы"""
        pages_data = [
            {
                'title': 'О компании',
                'slug': 'about',
                'content': '<h2>О компании MyBiz</h2><p>Мы - современная компания.</p>',
                'excerpt': 'Информация о компании',
                'show_in_header': True,
            },
            {
                'title': 'Доставка',
                'slug': 'delivery',
                'content': '<h2>Условия доставки</h2><p>Быстрая доставка по России.</p>',
                'excerpt': 'Информация о доставке',
                'show_in_header': True,
            },
            {
                'title': 'Контакты',
                'slug': 'contacts',
                'content': '<h2>Наши контакты</h2><p>Свяжитесь с нами.</p>',
                'excerpt': 'Контактная информация',
                'show_in_header': False,
            },
        ]

        created = 0
        for page_data in pages_data:
            page, created_flag = Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content'],
                    'excerpt': page_data['excerpt'],
                    'show_in_header': page_data['show_in_header'],
                    'is_active': True,
                }
            )
            if created_flag:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {created} тестовых страниц'))
