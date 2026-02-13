# mybiz_core/management/commands/seed_data.py
import os
import random
import io
import shutil
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from PIL import Image, ImageDraw, ImageFont

from mybiz_core.models import Category, Product
from content.models import SiteSettings


class Command(BaseCommand):
    help = 'Создает 10 категорий и 200 тестовых товаров с изображениями'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('🔄 Начинаем создание тестовых данных...')

        # 1. Удаляем все старые медиафайлы
        self.delete_all_media_files()

        # 2. Полностью очищаем кэш Django
        self.clear_cache()

        # 3. Удаляем ВСЕ старые товары перед созданием новых
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('🗑️  Все старые товары удалены'))

        # 4. Создание категорий (всегда с новыми изображениями)
        categories = self.create_categories()

        # 5. Создание товаров (200 штук)
        self.create_products(categories)

        self.stdout.write(
            self.style.SUCCESS('✅ Тестовые данные успешно созданы!')
        )
        self.stdout.write(f'   📦 Категорий: {len(categories)}')
        self.stdout.write(f'   🛍️  Товаров: {Product.objects.filter(is_active=True).count()}')

    def delete_all_media_files(self):
        """Полное удаление всех сгенерированных изображений и кэша миниатюр."""
        self.stdout.write("🧹 Очистка старых медиафайлов...")

        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')
        categories_dir = os.path.join(media_root, 'categories')
        cache_dir = os.path.join(media_root, 'cache')

        if os.path.exists(products_dir):
            for filename in os.listdir(products_dir):
                file_path = os.path.join(products_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        self.stdout.write(f"  🗑️ Удалён: products/{filename}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Ошибка удаления {filename}: {e}"))

        if os.path.exists(categories_dir):
            for filename in os.listdir(categories_dir):
                file_path = os.path.join(categories_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        self.stdout.write(f"  🗑️ Удалён: categories/{filename}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Ошибка удаления {filename}: {e}"))

        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                self.stdout.write("  🗑️ Удалён кэш миниатюр (cache/)")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Ошибка удаления кэша: {e}"))

        self.stdout.write(self.style.SUCCESS("✅ Все старые медиафайлы удалены"))

    def clear_cache(self):
        """Полная очистка всех кэшей Django."""
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Весь кэш Django очищен'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️ Не удалось очистить кэш: {e}'))

    # -------------------------------------------------------------------------
    # Методы для создания изображений
    # -------------------------------------------------------------------------
    def create_gradient_image(self, width, height, color1, color2, text=""):
        """Создаёт градиентное изображение с текстом (автомасштабирование шрифта)."""
        img = Image.new('RGB', (width, height), color1)
        draw = ImageDraw.Draw(img)

        for i in range(height):
            ratio = i / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        if text:
            margin = 30
            max_width = width - 2 * margin
            font_size = 40

            display_text = text
            font = None

            while font_size >= 12:
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
                    break
                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width <= max_width:
                    break
                font_size -= 2

            if font is None:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = max(margin, (width - text_width) // 2)
            y = max(margin, (height - text_height) // 2)

            draw.text((x + 2, y + 2), display_text, font=font, fill=(0, 0, 0, 128))
            draw.text((x, y), display_text, font=font, fill=(255, 255, 255))

        return img

    def create_product_image(self, size, category_name, product_name):
        """
        Создаёт квадратное изображение товара size x size.
        Категория — в правом верхнем углу с отступом, всегда в кадре.
        """
        width = height = size

        # Цвета для категорий
        category_colors = {
            'Электроника': ((59, 130, 246), (37, 99, 235)),
            'Одежда': ((139, 92, 246), (107, 52, 235)),
            'Дом и Сад': ((16, 185, 129), (5, 150, 105)),
            'Спорт и Отдых': ((239, 68, 68), (202, 38, 38)),
            'Красота и Здоровье': ((245, 158, 11), (217, 119, 6)),
            'Книги': ((107, 114, 128), (55, 65, 81)),
            'Мебель': ((217, 119, 6), (161, 98, 7)),
            'Игрушки': ((236, 72, 153), (197, 24, 98)),
            'Продукты': ((132, 204, 22), (101, 163, 13)),
            'Автотовары': ((75, 85, 99), (31, 41, 55)),
        }

        color1, color2 = category_colors.get(category_name, ((100, 100, 100), (50, 50, 50)))

        img = self.create_gradient_image(width, height, color1, color2)
        draw = ImageDraw.Draw(img)

        # Шрифты
        try:
            label_font = ImageFont.truetype("DejaVuSans.ttf", int(size * 0.05))      # 30px при 600px
            product_font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(size * 0.06)) # 36px при 600px
        except IOError:
            label_font = ImageFont.load_default()
            product_font = ImageFont.load_default()

        # ----- 1. КАТЕГОРИЯ — ПРАВЫЙ ВЕРХНИЙ УГОЛ -----
        right_margin = int(size * 0.05)   # 30px при 600px
        top_margin = int(size * 0.03)     # 18px при 600px
        max_cat_width = width - right_margin

        display_cat = category_name
        font_size = 24
        category_font = None

        # Подбираем размер шрифта, чтобы текст поместился по ширине
        while font_size >= 8:
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
                break
            bbox = draw.textbbox((0, 0), display_cat, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_cat_width:
                category_font = font
                break
            font_size -= 2

        # Если всё ещё не влезает — обрезаем текст
        if category_font is None:
            category_font = ImageFont.load_default()
            while len(display_cat) > 0:
                bbox = draw.textbbox((0, 0), display_cat, font=category_font)
                text_width = bbox[2] - bbox[0]
                if text_width <= max_cat_width:
                    break
                display_cat = display_cat[:-4] + "…"

        # Финальные размеры
        bbox = draw.textbbox((0, 0), display_cat, font=category_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Позиция: правый край текста на отступе от правого края
        x = width - right_margin - text_width
        y = top_margin

        # Тень
        draw.text(
            (x + 2, y + 2),
            display_cat,
            font=category_font,
            fill=(0, 0, 0, 180)
        )
        # Основной текст
        draw.text(
            (x, y),
            display_cat,
            font=category_font,
            fill=(255, 255, 255)
        )

        # Отладка (можно удалить)
        print(f"🖼️ Категория '{display_cat}' (шрифт {font_size}px) — x={x}, ширина={text_width}")

        # ----- 2. МЕТКА "ТЕСТОВОЕ ИЗОБРАЖЕНИЕ" — ЦЕНТР -----
        label_text = "Тестовое изображение"
        bbox = draw.textbbox((0, 0), label_text, font=label_font)
        label_width = bbox[2] - bbox[0]
        label_height = bbox[3] - bbox[1]

        label_x = (width - label_width) // 2
        label_y = (height // 2) - label_height - 20

        draw.text(
            (label_x + 2, label_y + 2),
            label_text,
            font=label_font,
            fill=(0, 0, 0, 180)
        )
        draw.text(
            (label_x, label_y),
            label_text,
            font=label_font,
            fill=(255, 255, 255)
        )

        # ----- 3. НАЗВАНИЕ ТОВАРА — ПОД МЕТКОЙ -----
        max_product_length = 25
        if len(product_name) > max_product_length:
            product_name_display = product_name[:max_product_length] + "…"
        else:
            product_name_display = product_name

        bbox = draw.textbbox((0, 0), product_name_display, font=product_font)
        product_width = bbox[2] - bbox[0]
        product_height = bbox[3] - bbox[1]

        product_x = (width - product_width) // 2
        product_y = label_y + label_height + 20

        draw.text(
            (product_x + 3, product_y + 3),
            product_name_display,
            font=product_font,
            fill=(0, 0, 0, 180)
        )
        draw.text(
            (product_x, product_y),
            product_name_display,
            font=product_font,
            fill=(255, 255, 255)
        )

        return img

    def save_image_to_model(self, image, filename, model_field):
        """Сохраняет изображение в поле модели Django."""
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)
        model_field.save(filename, ContentFile(img_io.read()), save=True)

    # -------------------------------------------------------------------------
    # Создание категорий
    # -------------------------------------------------------------------------
    def create_categories(self):
        """Создаёт 10 категорий с изображениями (всегда пересоздаёт картинки)."""
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
            category, created = Category.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'meta_title': data['meta_title'],
                    'meta_description': data['meta_description'],
                    'meta_keywords': data['meta_keywords'],
                    'is_active': True,
                }
            )

            # Всегда создаём новое изображение (старые файлы удалены)
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
                self.stdout.write(f'  🔄 Обновлена категория: {category.name} (изображение пересоздано)')

            categories.append(category)

        return categories

    # -------------------------------------------------------------------------
    # Создание товаров
    # -------------------------------------------------------------------------
    def create_products(self, categories):
        """Создаёт 200 тестовых товаров (по 20 на категорию)."""
        self.stdout.write('🛍️  Создание товаров...')

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

        brands = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E', 'Premium', 'Eco', 'Pro', 'Max', 'Plus']

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

        created_count = 0
        for category in categories:
            for i in range(20):
                try:
                    prefix = random.choice(product_prefixes[category.name])
                    model_num = f"{random.randint(100, 999)}{chr(random.randint(65, 90))}"
                    name = f"{prefix} {model_num}"

                    base_slug = f"{prefix.lower().replace(' ', '-')}-{model_num}-{random.randint(1000, 9999)}"
                    slug = base_slug
                    counter = 1
                    while Product.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    min_price, max_price = base_price_ranges[category.name]
                    price = Decimal(random.randint(min_price, max_price))

                    discount_price = None
                    if random.random() < 0.3:
                        discount = random.randint(10, 40)
                        discount_price = price * Decimal((100 - discount) / 100)
                        discount_price = discount_price.quantize(Decimal('0.01'))

                    base_sku = f"{category.slug.upper()[:3]}-{random.randint(10000, 99999)}-{model_num}"
                    sku = base_sku
                    counter = 1
                    while Product.objects.filter(sku=sku).exists():
                        sku = f"{base_sku}-{counter}"
                        counter += 1

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
                        in_stock=random.random() < 0.9,
                        is_new=random.random() < 0.2,
                        is_featured=random.random() < 0.15,
                        is_active=True,
                        rating=round(random.uniform(3.5, 5.0), 1),
                        review_count=random.randint(0, 200),
                    )

                    img = self.create_product_image(600, category.name, name)
                    filename = f"product_{category.slug}_{i+1}_{random.randint(1000, 9999)}.jpg"
                    self.save_image_to_model(img, filename, product.image)

                    product.save()
                    created_count += 1

                    if created_count % 20 == 0:
                        self.stdout.write(f'  ✅ Создано {created_count} товаров...')

                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Дубликат (пропуск): {name} — {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Ошибка при создании товара {name}: {e}'))

        self.stdout.write(f'  ✅ Всего создано товаров: {created_count}')
