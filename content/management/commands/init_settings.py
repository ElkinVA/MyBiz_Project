# content/management/commands/init_settings.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.core.files.base import ContentFile
from content.models import SiteSettings
from mybiz_core.models import Category, Product
from pages.models import Page
import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils.text import slugify
from PIL import Image, ImageDraw
import io

class Command(BaseCommand):
    help = 'Инициализирует базовые настройки сайта, тестовые данные и управляет кэшем'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Пропустить создание тестовых данных',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Только очистить кэш (без создания данных)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно пересоздать все данные',
        )

    def handle(self, *args, **options):
        # Если указан флаг --clear-cache, только очищаем кэш
        if options['clear_cache']:
            self.stdout.write("🔄 Очистка кэша...")
            self.clear_all_cache()
            self.stdout.write(self.style.SUCCESS('✅ Кэш успешно очищен'))
            return

        self.stdout.write("🔄 Начинаем инициализацию проекта MyBiz...")

        # 1. Создаем настройки сайта
        self.create_site_settings()

        # 2. Создаем тестовые данные (если не указан --skip-data)
        if not options['skip_data']:
            self.create_test_categories()
            self.create_test_products()
            self.create_test_pages()
            self.stdout.write(self.style.SUCCESS('✅ Тестовые данные созданы'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Создание тестовых данных пропущено'))

        # 3. Очищаем кэш после создания данных
        self.stdout.write("🔄 Очистка кэша...")
        self.clear_all_cache()

        self.stdout.write(self.style.SUCCESS('🎉 Инициализация проекта завершена!'))

    def clear_all_cache(self):
        """Полная очистка кэша сайта"""
        try:
            # Очищаем весь кэш Django
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Кэш Django очищен'))

            # Очищаем кэш настроек сайта через модель
            try:
                site_settings = SiteSettings.load()
                if site_settings:
                    site_settings.clear_cache()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Кэш настроек сайта очищен: {site_settings.site_name}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Не удалось очистить кэш настроек: {e}')
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка при очистке кэша: {e}'))

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
            self.stdout.write(self.style.ERROR(f'❌ Ошибка создания настроек: {e}'))

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
                }
            )
            if created_flag:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {created} категорий'))

    def _create_placeholder_image(self, name):
        """Создает простое тестовое изображение с названием товара"""
        # Создаем изображение 400x400 с градиентом
        img = Image.new('RGB', (400, 400), color=(240, 245, 250))
        draw = ImageDraw.Draw(img)

        # Добавляем текст с названием товара
        draw.text((200, 180), name[:20], fill=(100, 100, 100), anchor="mm")
        draw.text((200, 220), "Тестовое изображение", fill=(150, 150, 150), anchor="mm")

        # Сохраняем в буфер
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f"{slugify(name, allow_unicode=True)}.jpg")

    def create_test_products(self):
        """Создает тестовые товары с уникальными slug и изображениями"""
        # Удаляем старые тестовые товары
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('🗑️ Все старые товары удалены'))

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
        used_slugs = set()  # Для отслеживания использованных slug в рамках одной команды

        for i in range(50):  # Создаем 50 тестовых товаров
            category = random.choice(categories)
            base_name = random.choice(product_names)
            name = f'{base_name} {i+1}'

            # Генерируем уникальный slug с проверкой на конфликты
            base_slug = slugify(name, allow_unicode=True)
            slug = base_slug
            counter = 1

            # Проверяем уникальность в базе данных и в текущем сеансе
            while Product.objects.filter(slug=slug).exists() or slug in used_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
                if len(slug) > 200:
                    slug = slug[:200]

            used_slugs.add(slug)

            price = Decimal(random.randint(1000, 50000))
            # 30% товаров со скидкой
            discount_price = None
            if random.random() < 0.3:
                discount_price = price * Decimal('0.8')

            # Создаем тестовое изображение
            image = self._create_placeholder_image(name)

            product = Product.objects.create(
                name=name,
                slug=slug,  # Уникальный slug
                category=category,
                price=price,
                discount_price=discount_price,
                short_description=f'Тестовый товар {i+1}',
                description=f'<p>Описание тестового товара {i+1}. Высокое качество.</p>',
                sku=f'TEST{i+1:04d}',
                brand=random.choice(['Brand A', 'Brand B', 'Brand C', '']),
                image=image,  # Тестовое изображение
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
