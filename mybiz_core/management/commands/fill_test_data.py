import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from mybiz_core.models import Category, Product
from content.models import SiteSettings, Promotion
from pages.models import Page
from django.contrib.auth import get_user_model

# Реальные названия категорий и товаров для реалистичного наполнения
CATEGORIES_DATA = [
    {
        'name': 'Электроника',
        'products': [
            ('Телевизор Samsung 55" UE55AU7100', 'Современный 4K Smart TV с диагональю 55 дюймов'),
            ('Наушники Sony WH-1000XM5', 'Беспроводные наушники с шумоподавлением'),
            ('Планшет iPad Air 2024', 'Мощный планшет от Apple с чипом M2'),
            ('Яндекс Станция Макс', 'Умная колонка с Алисой и отличным звуком'),
            ('Фотоаппарат Canon EOS R6', 'Профессиональная беззеркальная камера'),
            ('Smart-часы Apple Watch Series 9', 'Фитнес-трекер и уведомления на запястье'),
            ('Портативная колонка JBL Flip 6', 'Компактная водонепроницаемая колонка'),
            ('Электронная книга PocketBook Touch', 'Чтение книг с комфортом для глаз'),
        ]
    },
    {
        'name': 'Бытовая техника',
        'products': [
            ('Холодильник Bosch Serie 6', 'Двухкамерный холодильник с No Frost'),
            ('Стиральная машина LG F2J3', 'Загрузка 6 кг, прямое привод'),
            ('Микроволновка Panasonic GT', 'СВЧ-печь с грилем и конвекцией'),
            ('Пылесос Dyson V15 Detect', 'Беспроводной пылесос с лазером'),
            ('Кофемашина DeLonghi Magnifica', 'Автоматическая кофемашина для дома'),
            ('Тостер Tefal Express', 'Быстрый тостер с регулировкой степени прожарки'),
            ('Утюг Philips Azur', 'Паровой утюг с керамической подошвой'),
            ('Чайник Bosch TWK8613', 'Электрический чайник с контролем температуры'),
        ]
    },
    {
        'name': 'Компьютеры и ноутбуки',
        'products': [
            ('MacBook Pro 14" M3', 'Профессиональный ноутбук Apple'),
            ('ASUS ROG Strix G16', 'Игровой ноутбук с RTX 4060'),
            ('ПК Intel i7 Gaming', 'Игровой компьютер для любых задач'),
            ('Монитор Dell UltraSharp 27"', '4K монитор для работы и дизайна'),
            ('Клавиатура Logitech MX Keys', 'Беспроводная клавиатура для офиса'),
            ('Мышь Razer DeathAdder V3', 'Игровая мышь с высокой точностью'),
            ('SSD Samsung 980 PRO 1TB', 'Быстрый NVMe накопитель'),
            ('Оперативная память Kingston 32GB', 'DDR5 память для ПК'),
        ]
    },
    {
        'name': 'Телефоны и смартфоны',
        'products': [
            ('iPhone 15 Pro Max', 'Флагманский смартфон Apple'),
            ('Samsung Galaxy S24 Ultra', 'Android-флагман с S Pen'),
            ('Google Pixel 8 Pro', 'Чистый Android и лучшая камера'),
            ('Xiaomi Redmi Note 13', 'Бюджетный смартфон с AMOLED'),
            ('OnePlus 12', 'Мощный флагман с быстрой зарядкой'),
            ('Realme GT Neo 5', 'Игровой смартфон по доступной цене'),
            ('Honor Magic6 Pro', 'Премиум смартфон с отличной камерой'),
            ('Nothing Phone (2)', 'Стильный смартфон с Glyph Interface'),
        ]
    },
    {
        'name': 'Одежда и обувь',
        'products': [
            ('Кроссовки Nike Air Max 90', 'Классические кроссовки для города'),
            ('Джинсы Levi\'s 501 Original', 'Легендарные прямые джинсы'),
            ('Футболка Uniqlo Cotton', 'Базовая хлопковая футболка'),
            ('Куртка The North Face', 'Тёплая зимняя куртка'),
            ('Ботинки Timberland Classic', 'Знаменитые жёлтые ботинки'),
            ('Худи Adidas Originals', 'Спортивное худи с логотипом'),
            ('Рюкзак Fjallraven Kanken', 'Шведский рюкзак для города'),
            ('Шапка Woolrich', 'Шерстяная шапка для холодов'),
        ]
    },
    {
        'name': 'Дом и сад',
        'products': [
            ('Диван IKEA Klippan', 'Компактный двухместный диван'),
            ('Лампа IKEA Melodi', 'Настольная лампа с тёплым светом'),
            ('Комнатное растение Монстера', 'Популярное тропическое растение'),
            ('Набор посуды Luminarc', 'Обеденный сервиз на 6 персон'),
            ('Плед шерстяной Merino', 'Тёплый плед из натуральной шерсти'),
            ('Картина постер "Горы"', 'Декор для стены в скандинавском стиле'),
            ('Ваза керамическая белая', 'Минималистичная ваза для цветов'),
            ('Свечи ароматические набор', 'Набор свечей с разными ароматами'),
        ]
    },
    {
        'name': 'Спорт и отдых',
        'products': [
            ('Велосипед горный Trek Marlin', 'Надёжный маунтинбайк для трейлов'),
            ('Гантели разборные 20 кг', 'Регулируемые гантели для дома'),
            ('Коврик для йоги Manduka', 'Профессиональный коврик для йоги'),
            ('Фитбол Gym Ball 65 см', 'Мяч для фитнеса и упражнений'),
            ('Беговая дорожка DFC', 'Домашняя дорожка для бега'),
            ('Палатка кемпинговая 4 места', 'Просторная палатка для походов'),
            ('Спальный мешок Tramp', 'Тёплый мешок для кемпинга'),
            ('Рюкзак туристический 60L', 'Вместительный рюкзак для путешествий'),
        ]
    },
    {
        'name': 'Книги',
        'products': [
            ('"1984" Джордж Оруэлл', 'Классика антиутопии'),
            ('"Атомные привычки" Джеймс Клир', 'Бестселлер по саморазвитию'),
            ('"Дюна" Фрэнк Герберт', 'Эпическая научная фантастика'),
            ('"Sapiens" Юваль Ной Харари', 'Краткая история человечества'),
            ('"Мастер и Маргарита" Булгаков', 'Великий русский роман'),
            ('"Гарри Поттер" Дж. К. Роулинг', 'Волшебная серия книг'),
            ('"Чистый код" Роберт Мартин', 'Для программистов'),
            ('"Думай медленно" Даниэль Канеман', 'Психология принятия решений'),
        ]
    },
    {
        'name': 'Детские товары',
        'products': [
            ('Конструктор LEGO Star Wars', 'Набор для фанатов Звёздных войн'),
            ('Кукла Barbie Dreamhouse', 'Большой дом для куклы'),
            ('Машинка Hot Wheels трек', 'Гоночный трек для машинок'),
            ('Настольная игра Монополия', 'Классическая экономическая игра'),
            ('Плюшевый мишка Teddy', 'Мягкая игрушка для детей'),
            ('Развивающий коврик Fisher-Price', 'Для самых маленьких'),
            ('Детский велосипед Puky', 'Немецкий качественный велосипед'),
            ('Набор для рисования Crayola', 'Большой набор красок и карандашей'),
        ]
    },
    {
        'name': 'Красота и здоровье',
        'products': [
            ('Электрическая зубная щётка Oral-B', 'Щётка с технологией 3D'),
            ('Фен Dyson Supersonic', 'Профессиональный фен для волос'),
            ('Крем La Roche-Posay', 'Увлажняющий крем для лица'),
            ('Витамины Solgar комплекс', 'Набор витаминов для здоровья'),
            ('Тонометр Omron автомат', 'Точный измеритель давления'),
            ('Массажёр для шеи Xiaomi', 'Расслабляющий массажёр'),
            ('Парфюм Chanel Coco Mademoiselle', 'Известный женский аромат'),
            ('Набор косметики Clinique', 'Подарочный набор ухода'),
        ]
    },
]


def generate_unique_slug(model, name, original_slug=None):
    """Генерирует уникальный slug, добавляя суффикс при коллизии."""
    if original_slug is None:
        slug = slugify(name)
    else:
        slug = original_slug
    
    # Если slug пустой (например, для русских слов), используем транслит
    if not slug:
        slug = f"item-{random.randint(1000, 9999)}"
    
    base_slug = slug
    counter = 1
    
    # Проверяем существование такого slug
    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


class Command(BaseCommand):
    help = 'Заполняет базу данных реалистичными тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить базу перед заполнением')
        parser.add_argument('--products-per-category', type=int, default=5, help='Количество товаров в каждой категории')

    def handle(self, *args, **options):
        clear_db = options['clear']
        products_per_category = options['products_per_category']

        # Опционально очищаем базу
        if clear_db:
            self.stdout.write(self.style.WARNING('🗑️ Очищаем базу данных...'))
            Product.objects.all().delete()
            Category.objects.all().delete()
            Promotion.objects.all().delete()
            Page.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ База очищена'))

        # 1. Создаем настройки сайта (Синглтон)
        self.stdout.write('🎨 Создаем настройки сайта...')
        settings, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'MyBiz Test Shop',
                'site_tagline': 'Лучший тестовый магазин на Django',
                'contact_email': 'info@mybiz-test.ru',
                'contact_phone': '+7 (999) 000-00-00',
                'contact_address': 'г. Москва, ул. Тестовая, д. 1',
                'primary_color': '#4F46E5',
                'secondary_color': '#10B981',
            }
        )
        if not created:
            self.stdout.write(self.style.WARNING('Настройки сайта уже существовали.'))

        # 2. Создаем категории и товары
        self.stdout.write(f'📂 Создаем {len(CATEGORIES_DATA)} категорий с товарами...')
        
        for category_data in CATEGORIES_DATA:
            category_name = category_data['name']
            products_list = category_data['products']
            
            # Создаём категорию
            category_slug = slugify(category_name)
            category, created = Category.objects.get_or_create(
                slug=category_slug,
                defaults={
                    'name': category_name,
                    'description': f'Товары категории "{category_name}" - большой выбор, качественные бренды, выгодные цены.',
                    'is_active': True,
                    'parent': None,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Категория: {category_name}')
            else:
                self.stdout.write(f'  ~ Категория: {category_name} (уже существует)')
            
            # Создаём товары для категории
            for product_name, product_desc in products_list[:products_per_category]:
                product_slug = slugify(product_name)
                
                # Генерируем цену от 500 до 50000 руб
                price = round(random.uniform(500, 50000), 2)
                
                # Случайная скидка (30% товаров)
                has_discount = random.random() > 0.7
                discount_price = None
                if has_discount:
                    discount_percent = random.randint(5, 30)
                    discount_price = round(price * (1 - discount_percent / 100), 2)
                
                # Случайный бренд
                brands = ['Samsung', 'Apple', 'Sony', 'LG', 'Bosch', 'Philips', 'Xiaomi', 'Huawei', 'Nike', 'Adidas']
                brand = random.choice(brands)
                
                product, created = Product.objects.get_or_create(
                    slug=product_slug,
                    defaults={
                        'name': product_name,
                        'category': category,
                        'short_description': product_desc,
                        'description': f'{product_desc}. {'Высокое качество, гарантия производителя, быстрая доставка.' if not has_discount else 'Специальное предложение! Скидка ' + str(int((1 - discount_price/price)*100)) + '%.'}',
                        'price': price,
                        'discount_price': discount_price,
                        'sku': f'SKU-{random.randint(10000, 99999)}',
                        'brand': brand,
                        'stock': random.randint(5, 100),
                        'is_active': True,
                        'is_featured': random.random() > 0.8,
                        'is_new': random.random() > 0.8,
                        'rating': round(random.uniform(4.0, 5.0), 1),
                        'review_count': random.randint(0, 50),
                    }
                )
                
                if created:
                    status = '✓'
                else:
                    status = '~'
                discount_mark = f' 🔥 -{int((1 - discount_price/price)*100)}%' if discount_price else ''
                self.stdout.write(f'    {status} Товар: {product_name}{discount_mark}')

        # 3. Создаем промо-акции
        self.stdout.write('\n🔥 Создаем промо-акции...')
        promotions_data = [
            ('Летняя распродажа', 'Скидки до 50% на летний ассортимент!', 30),
            ('Черная пятница', 'Грандиозные скидки на всё!', 50),
            ('Новогодняя акция', 'Подарки себе и близким со скидкой!', 25),
            ('Распродажа электроники', 'Техника по лучшим ценам!', 20),
        ]
        
        from datetime import date, timedelta
        today = date.today()
        
        for title, description, discount in promotions_data:
            Promotion.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'discount_value': discount,
                    'is_active': True,
                    'start_date': today - timedelta(days=30),
                    'end_date': today + timedelta(days=60),
                }
            )
            self.stdout.write(f'  ✓ Акция: {title}')

        # 4. Создаем статические страницы
        self.stdout.write('\n📄 Создаем статические страницы...')
        pages_data = [
            {'title': 'О нас', 'slug': 'about', 'content': 'Мы — команда энтузиастов, создавшая этот магазин для вас. Наша миссия — предоставить лучшие товары по доступным ценам.'},
            {'title': 'Доставка и оплата', 'slug': 'delivery', 'content': 'Доставляем по всей России. Курьерская доставка, пункты выдачи, почта. Оплата картой, наличными, рассрочка.'},
            {'title': 'Контакты', 'slug': 'contacts', 'content': 'Телефон: +7 (999) 000-00-00\nEmail: info@mybiz-test.ru\nАдрес: г. Москва, ул. Тестовая, д. 1'},
            {'title': 'Политика конфиденциальности', 'slug': 'privacy', 'content': 'Мы уважаем вашу конфиденциальность и защищаем персональные данные в соответствии с законодательством.'},
            {'title': 'Возврат товара', 'slug': 'returns', 'content': 'Вы можете вернуть товар в течение 14 дней. Товар должен быть в оригинальной упаковке и не иметь следов использования.'},
        ]
        
        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults={
                    'title': page_data['title'],
                    'content': page_data['content'],
                    'is_active': True,
                }
            )
            status = '✓' if created else '~'
            self.stdout.write(f'  {status} Страница: {page_data["title"]}')

        # 5. Создаем суперпользователя (если нет)
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            self.stdout.write('\n👤 Создаем суперпользователя admin/admin...')
            User.objects.create_superuser(
                username='admin',
                email='admin@mybiz.test',
                password='admin',
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('  ✓ Пользователь admin создан'))
        else:
            self.stdout.write(self.style.WARNING('\n~ Пользователь admin уже существует.'))

        # Итоговая статистика
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Готово!'))
        self.stdout.write(f'📊 Создано:')
        self.stdout.write(f'   • Категорий: {Category.objects.count()}')
        self.stdout.write(f'   • Товаров: {Product.objects.count()}')
        self.stdout.write(f'   • Акций: {Promotion.objects.count()}')
        self.stdout.write(f'   • Страниц: {Page.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\n🔐 Логин администратора: admin / admin'))
        self.stdout.write('='*50)
