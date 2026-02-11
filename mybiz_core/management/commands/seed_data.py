# mybiz_core/management/commands/seed_data.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.cache import cache
from mybiz_core.models import Category, Product
from content.models import SiteSettings
from decimal import Decimal
import random
from PIL import Image, ImageDraw, ImageFont
import io

class Command(BaseCommand):
    help = 'Создает 10 категорий и 200 тестовых товаров с изображениями'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Начинаем создание тестовых данных...')

        # Очистка кэша
        self.clear_cache()

        # Удаляем ВСЕ старые товары перед созданием новых
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('🗑️  Все старые товары удалены'))

        # Создание категорий
        categories = self.create_categories()

        # Создание товаров
        self.create_products(categories)

        self.stdout.write(
            self.style.SUCCESS('✅ Тестовые данные успешно созданы!')
        )
        self.stdout.write(f'   📦 Категорий: {len(categories)}')
        self.stdout.write(f'   🛍️  Товаров: 200')

    def clear_cache(self):
        """Очистка кэша настроек сайта"""
        try:
            site_settings = SiteSettings.load()
            if site_settings:
                cache_key = f'site_settings_{site_settings.id}'
                cache.delete(cache_key)
                self.stdout.write(
                    self.style.SUCCESS(f'Кэш настроек сайта очищен: {site_settings.site_name}')
                )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Не удалось очистить кэш настроек: {e}'))

    def create_gradient_image(self, width, height, color1, color2, text=""):
        """Создает градиентное изображение с текстом"""
        img = Image.new('RGB', (width, height), color1)
        draw = ImageDraw.Draw(img)

        # Градиент
        for i in range(height):
            ratio = i / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # Текст
        if text:
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Центрируем текст
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2

            # Тень
            draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 128))
            # Основной текст
            draw.text((x, y), text, font=font, fill=(255, 255, 255))

        return img

    def create_product_image(self, width, height, category_name, product_name):
        """Создает изображение товара с названием категории в левом верхнем углу и названием товара по центру"""
        # Цвета для разных категорий
        category_colors = {
            'Электроника': ((59, 130, 246), (37, 99, 235)),  # Синий
            'Одежда': ((139, 92, 246), (107, 52, 235)),      # Фиолетовый
            'Дом и Сад': ((16, 185, 129), (5, 150, 105)),    # Зеленый
            'Спорт и Отдых': ((239, 68, 68), (202, 38, 38)), # Красный
            'Красота и Здоровье': ((245, 158, 11), (217, 119, 6)), # Оранжевый
            'Книги': ((107, 114, 128), (55, 65, 81)),        # Серый
            'Мебель': ((217, 119, 6), (161, 98, 7)),         # Коричневый
            'Игрушки': ((236, 72, 153), (197, 24, 98)),      # Розовый
            'Продукты': ((132, 204, 22), (101, 163, 13)),    # Лайм
            'Автотовары': ((75, 85, 99), (31, 41, 55)),      # Темно-серый
        }

        color1, color2 = category_colors.get(category_name, ((100, 100, 100), (50, 50, 50)))

        # Создаем изображение
        img = self.create_gradient_image(width, height, color1, color2)
        draw = ImageDraw.Draw(img)

        # Попробуем загрузить шрифты, если не получится - используем стандартные
        try:
            # Мелкий шрифт для категории (левый верхний угол)
            category_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
            # Средний шрифт для "Тестовое изображение"
            label_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            # Большой шрифт для названия товара
            product_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        except:
            # Если шрифт не найден, используем стандартный
            category_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            product_font = ImageFont.load_default()

        # 1. Название категории в левом верхнем углу (мелко, без фона, сдвинуто вправо)
        margin = 20
        category_bbox = draw.textbbox((0, 0), category_name, font=category_font)
        category_height = category_bbox[3] - category_bbox[1]

        # Позиционируем текст категории (немного правее)
        category_x = margin + 10  # Сдвинуто вправо на 10 пикселей
        category_y = margin + 5

        # Тень для текста категории
        draw.text(
            (category_x + 2, category_y + 2),
            category_name,
            font=category_font,
            fill=(0, 0, 0, 180)
        )
        # Основной текст категории (без фона)
        draw.text(
            (category_x, category_y),
            category_name,
            font=category_font,
            fill=(255, 255, 255)
        )

        # 2. "Тестовое изображение" посередине (сверху)
        label_text = "Тестовое изображение"
        label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
        label_width = label_bbox[2] - label_bbox[0]
        label_height = label_bbox[3] - label_bbox[1]

        label_x = (width - label_width) // 2
        label_y = (height // 2) - label_height - 40  # Над центром

        # Тень для текста
        draw.text(
            (label_x + 2, label_y + 2),
            label_text,
            font=label_font,
            fill=(0, 0, 0, 180)
        )
        # Основной текст
        draw.text(
            (label_x, label_y),
            label_text,
            font=label_font,
            fill=(255, 255, 255)
        )

        # 3. Название товара посередине (снизу от "Тестовое изображение")
        # Ограничиваем длину названия товара
        max_product_length = 25
        if len(product_name) > max_product_length:
            product_name_display = product_name[:max_product_length] + "..."
        else:
            product_name_display = product_name

        product_bbox = draw.textbbox((0, 0), product_name_display, font=product_font)
        product_width = product_bbox[2] - product_bbox[0]
        product_height = product_bbox[3] - product_bbox[1]

        product_x = (width - product_width) // 2
        product_y = label_y + label_height + 30  # Под "Тестовое изображение"

        # Тень для текста товара
        draw.text(
            (product_x + 3, product_y + 3),
            product_name_display,
            font=product_font,
            fill=(0, 0, 0, 180)
        )
        # Основной текст товара
        draw.text(
            (product_x, product_y),
            product_name_display,
            font=product_font,
            fill=(255, 255, 255)
        )

        return img

    def save_image_to_model(self, image, filename, model_field):
        """Сохраняет изображение в модель Django"""
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)
        model_field.save(filename, ContentFile(img_io.read()), save=True)

    def create_categories(self):
        """Создает 10 категорий с изображениями"""
        self.stdout.write('📂 Создание категорий...')

        categories_data = [
            {
                'name': 'Электроника',
                'slug': 'electronics',
                'description': 'Современные гаджеты, смартфоны, ноутбуки и аксессуары.',
                'meta_title': 'Электроника - Купить в интернет-магазине',
                'meta_description': 'Широкий выбор электроники по выгодным ценам.',
                'meta_keywords': 'электроника, гаджеты, смартфоны, ноутбуки, техника',
            },
            {
                'name': 'Одежда',
                'slug': 'clothing',
                'description': 'Модная одежда для мужчин и женщин. Всегда в тренде.',
                'meta_title': 'Одежда - Стильные вещи в интернет-магазине',
                'meta_description': 'Стильная и удобная одежда для любого случая.',
                'meta_keywords': 'одежда, стиль, мода, мужская, женская, одежда онлайн',
            },
            {
                'name': 'Дом и Сад',
                'slug': 'home-garden',
                'description': 'Все для дома, сада, ремонта и уюта.',
                'meta_title': 'Дом и Сад - Товары для дома и сада',
                'meta_description': 'Товары для уюта, ремонта и садоводства.',
                'meta_keywords': 'дом, сад, интерьер, ремонт, садоводство, товары для дома',
            },
            {
                'name': 'Спорт и Отдых',
                'slug': 'sports-recreation',
                'description': 'Оборудование для спорта, фитнеса и активного отдыха.',
                'meta_title': 'Спорт и Отдых - Спортивные товары',
                'meta_description': 'Спортивные товары и экипировка для отдыха.',
                'meta_keywords': 'спорт, отдых, тренажеры, инвентарь, фитнес, активный отдых',
            },
            {
                'name': 'Красота и Здоровье',
                'slug': 'beauty-health',
                'description': 'Косметика, парфюмерия и товары для здоровья.',
                'meta_title': 'Красота и Здоровье - Косметика и уход',
                'meta_description': 'Продукты и аксессуары для красоты и здоровья.',
                'meta_keywords': 'красота, здоровье, косметика, уход, парфюмерия',
            },
            {
                'name': 'Книги',
                'slug': 'books',
                'description': 'Книги на любой вкус: художественная литература, учебники, детские книги.',
                'meta_title': 'Книги - Купить книги онлайн',
                'meta_description': 'Широкий выбор книг по доступным ценам.',
                'meta_keywords': 'книги, литература, учебники, детские книги, книги онлайн',
            },
            {
                'name': 'Мебель',
                'slug': 'furniture',
                'description': 'Качественная мебель для дома и офиса.',
                'meta_title': 'Мебель - Купить мебель для дома',
                'meta_description': 'Стильная и удобная мебель для любого интерьера.',
                'meta_keywords': 'мебель, диваны, столы, стулья, шкафы, мебель для дома',
            },
            {
                'name': 'Игрушки',
                'slug': 'toys',
                'description': 'Игрушки для детей всех возрастов.',
                'meta_title': 'Игрушки - Детские игрушки',
                'meta_description': 'Безопасные и качественные игрушки для детей.',
                'meta_keywords': 'игрушки, детские, развивающие, конструкторы, куклы',
            },
            {
                'name': 'Продукты',
                'slug': 'food',
                'description': 'Продукты питания, напитки и товары для кухни.',
                'meta_title': 'Продукты - Продукты питания онлайн',
                'meta_description': 'Качественные продукты питания и напитки.',
                'meta_keywords': 'продукты, еда, напитки, продукты питания, онлайн',
            },
            {
                'name': 'Автотовары',
                'slug': 'auto',
                'description': 'Товары для автомобилей и автолюбителей.',
                'meta_title': 'Автотовары - Товары для автомобиля',
                'meta_description': 'Аксессуары и запчасти для вашего автомобиля.',
                'meta_keywords': 'автотовары, автоаксессуары, запчасти, автомобиль',
            }
        ]

        categories = []
        for data in categories_data:
            # Создаем или получаем категорию
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults=data
            )

            # Создаем изображение для категории
            if not category.image:
                img = self.create_gradient_image(
                    400, 300,
                    (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150)),
                    (random.randint(20, 100), random.randint(20, 100), random.randint(20, 100)),
                    data['name']
                )
                filename = f"category_{category.slug}.jpg"
                self.save_image_to_model(img, filename, category.image)
                category.save()

            if created:
                self.stdout.write(f'  ✅ Создана категория: {category.name}')
            else:
                self.stdout.write(f'  ℹ️  Категория уже существует: {category.name}')

            categories.append(category)

        return categories

    def create_products(self, categories):
        """Создает 200 товаров с изображениями"""
        self.stdout.write('🛍️  Создание товаров...')

        # Префиксы для названий товаров
        product_prefixes = {
            'Электроника': ['Смартфон', 'Ноутбук', 'Планшет', 'Наушники', 'Часы', 'Камера', 'Колонка', 'Роутер'],
            'Одежда': ['Футболка', 'Джинсы', 'Куртка', 'Платье', 'Рубашка', 'Шорты', 'Свитер', 'Пальто'],
            'Дом и Сад': ['Лампа', 'Ковер', 'Шторы', 'Посуда', 'Инструмент', 'Семена', 'Горшок', 'Кресло'],
            'Спорт и Отдых': ['Мяч', 'Ролики', 'Велосипед', 'Рюкзак', 'Палатка', 'Спальник', 'Коврик', 'Гантели'],
            'Красота и Здоровье': ['Крем', 'Шампунь', 'Парфюм', 'Маска', 'Скраб', 'Лосьон', 'Зубная паста', 'Дезодорант'],
            'Книги': ['Роман', 'Учебник', 'Детская книга', 'Комикс', 'Энциклопедия', 'Блокнот', 'Альбом', 'Календарь'],
            'Мебель': ['Стул', 'Стол', 'Диван', 'Кровать', 'Шкаф', 'Тумба', 'Полка', 'Кресло'],
            'Игрушки': ['Конструктор', 'Кукла', 'Машинка', 'Пазл', 'Мягкая игрушка', 'Набор', 'Робот', 'Пистолет'],
            'Продукты': ['Шоколад', 'Кофе', 'Чай', 'Молоко', 'Хлеб', 'Сыр', 'Колбаса', 'Сок'],
            'Автотовары': ['Шины', 'Аккумулятор', 'Масло', 'Щетки', 'Коврики', 'Чехлы', 'Огнетушитель', 'Аптечка'],
        }

        # Описания для товаров
        descriptions = [
            'Высокое качество по доступной цене.',
            'Популярный товар среди наших клиентов.',
            'Новинка сезона с отличными характеристиками.',
            'Проверенный временем и покупателями товар.',
            'Идеальный выбор для повседневного использования.',
            'Стильный дизайн и надежность в каждой детали.',
            'Произведено с использованием современных технологий.',
            'Гарантия качества от производителя.',
            'Отличное соотношение цены и качества.',
            'Рекомендуем к покупке!',
        ]

        # Бренды
        brands = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E', 'Premium', 'Eco', 'Pro', 'Max', 'Plus']

        created_count = 0
        for category in categories:
            # Создаем 20 товаров для каждой категории
            for i in range(20):
                # Генерируем уникальные данные
                prefix = random.choice(product_prefixes[category.name])
                model_num = f"{random.randint(100, 999)}{chr(random.randint(65, 90))}"
                name = f"{prefix} {model_num}"
                slug = f"{prefix.lower().replace(' ', '-')}-{model_num}-{random.randint(1000, 9999)}"

                # Генерируем цену в зависимости от категории
                base_price_ranges = {
                    'Электроника': (5000, 100000),
                    'Одежда': (1000, 15000),
                    'Дом и Сад': (500, 20000),
                    'Спорт и Отдых': (1000, 30000),
                    'Красота и Здоровье': (300, 5000),
                    'Книги': (200, 3000),
                    'Мебель': (3000, 50000),
                    'Игрушки': (500, 10000),
                    'Продукты': (100, 2000),
                    'Автотовары': (1000, 40000),
                }
                min_price, max_price = base_price_ranges[category.name]
                price = Decimal(random.randint(min_price, max_price))

                # 30% товаров со скидкой
                discount_price = None
                if random.random() < 0.3:
                    discount = random.randint(10, 40)  # Скидка 10-40%
                    discount_price = price * Decimal((100 - discount) / 100)
                    discount_price = discount_price.quantize(Decimal('0.01'))

                # Генерируем уникальный артикул
                sku = f"{category.slug.upper()[:3]}-{random.randint(10000, 99999)}-{model_num}"

                # Создаем товар
                product = Product(
                    name=name,
                    slug=slug,
                    category=category,
                    description=f'<p>{random.choice(descriptions)}</p><p>Модель: {model_num}</p><p>Гарантия: 12 месяцев</p>',
                    short_description=f'{prefix} высокого качества. Модель {model_num}.',
                    price=price,
                    discount_price=discount_price,
                    sku=sku,
                    brand=random.choice(brands),
                    stock=random.randint(0, 100),
                    in_stock=random.random() < 0.9,  # 90% товаров в наличии
                    is_new=random.random() < 0.2,     # 20% товаров - новинки
                    is_featured=random.random() < 0.15,  # 15% товаров - рекомендуемые
                    is_active=True,
                    rating=round(random.uniform(3.5, 5.0), 1),
                    review_count=random.randint(0, 200),
                )

                # Создаем и сохраняем изображение
                img = self.create_product_image(800, 600, category.name, name)
                filename = f"product_{category.slug}_{i+1}_{random.randint(1000, 9999)}.jpg"
                self.save_image_to_model(img, filename, product.image)
                product.save()

                created_count += 1
                if created_count % 20 == 0:
                    self.stdout.write(f'  ✅ Создано {created_count} товаров...')

        self.stdout.write(f'  ✅ Всего создано товаров: {created_count}')
