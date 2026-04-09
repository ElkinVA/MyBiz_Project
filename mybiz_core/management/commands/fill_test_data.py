import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from mybiz_core.models import Category, Product
from content.models import SiteSettings, Promotion
from pages.models import Page
from django.contrib.auth import get_user_model

fake = Faker('ru_RU')

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными (категории, товары, настройки, промо)'

    def add_arguments(self, parser):
        parser.add_argument('--products', type=int, default=50, help='Количество товаров')
        parser.add_argument('--categories', type=int, default=10, help='Количество категорий')

    def handle(self, *args, **options):
        num_products = options['products']
        num_categories = options['categories']

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

        # 2. Создаем категории
        self.stdout.write(f'📂 Создаем {num_categories} категорий...')
        categories = []
        for i in range(num_categories):
            is_parent = random.random() > 0.7  # 30% категорий будут родительскими
            
            name = fake.word().title() + ' ' + fake.word().title()
            slug = slugify(name)
            
            if is_parent or len(categories) < 3:
                # Родительская категория
                cat = Category.objects.create(
                    name=name,
                    slug=slug,
                    description=fake.sentence(),
                    is_active=True,
                    parent=None
                )
            else:
                # Дочерняя категория (выбираем случайного родителя)
                parent = random.choice([c for c in categories if c.parent is None])
                cat = Category.objects.create(
                    name=name,
                    slug=slug,
                    description=fake.sentence(),
                    is_active=True,
                    parent=parent
                )
            categories.append(cat)

        # 3. Создаем товары
        self.stdout.write(f'📦 Создаем {num_products} товаров...')
        products = []
        for i in range(num_products):
            category = random.choice(categories)
            price = round(random.uniform(500, 50000), 2)
            
            # Случайная скидка
            has_discount = random.random() > 0.7
            discount_price = None
            if has_discount:
                discount_percent = random.randint(5, 30)
                discount_price = round(price * (1 - discount_percent / 100), 2)

            product = Product.objects.create(
                name=fake.catch_phrase(),
                category=category,
                short_description=fake.sentence(nb_words=10),
                description=fake.paragraph(nb_sentences=5),
                price=price,
                discount_price=discount_price,
                sku=f'SKU-{random.randint(10000, 99999)}',
                brand=fake.company(),
                stock=random.randint(0, 100),
                is_active=True,
                is_featured=random.random() > 0.8,  # 20% товаров популярные
                is_new=random.random() > 0.8,       # 20% товаров новые
                rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(0, 50),
            )
            products.append(product)

        # 4. Создаем промо-акции
        self.stdout.write('🔥 Создаем промо-акции...')
        titles = ['Летняя распродажа', 'Черная пятница', 'Новогодняя скидка', 'Только сегодня!']
        for title in titles:
            Promotion.objects.create(
                title=title,
                description=fake.paragraph(),
                discount_value=random.randint(10, 50),
                is_active=True,
                start_date=fake.date_this_year(before_today=True),
                end_date=fake.date_this_year(after_today=True),
            )

        # 5. Создаем статические страницы
        self.stdout.write('📄 Создаем статические страницы...')
        pages_data = [
            {'title': 'О нас', 'slug': 'about'},
            {'title': 'Доставка и оплата', 'slug': 'delivery'},
            {'title': 'Контакты', 'slug': 'contacts'},
            {'title': 'Политика конфиденциальности', 'slug': 'privacy'},
        ]
        for page_data in pages_data:
            Page.objects.get_or_create(
                slug=page_data['slug'],
                defaults={
                    'title': page_data['title'],
                    'content': fake.paragraph(nb_sentences=10),
                    'is_active': True,
                }
            )

        # 6. Создаем суперпользователя (если нет)
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            self.stdout.write('👤 Создаем суперпользователя admin/admin...')
            User.objects.create_superuser(
                username='admin',
                email='admin@mybiz.test',
                password='admin',
                is_staff=True
            )
        else:
            self.stdout.write(self.style.WARNING('Пользователь admin уже существует.'))

        self.stdout.write(self.style.SUCCESS(f'✅ Готово! Создано: {Category.objects.count()} категорий, {Product.objects.count()} товаров.'))
        self.stdout.write(self.style.SUCCESS('🔐 Логин администратора: admin / admin'))
