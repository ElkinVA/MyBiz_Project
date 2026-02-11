# content/management/commands/init_settings.py
from django.core.management.base import BaseCommand
from content.models import SiteSettings


class Command(BaseCommand):
    help = 'Инициализирует или обновляет настройки сайта'

    def handle(self, *args, **options):
        # Пытаемся получить существующие настройки
        try:
            settings = SiteSettings.load()
            self.stdout.write(self.style.WARNING('Настройки сайта уже существуют'))
            self.stdout.write(f'ID: {settings.id}')
            self.stdout.write(f'Название сайта: {settings.site_name}')
            self.stdout.write(f'Текущая цветовая схема: {settings.color_scheme}')
        except Exception as e:
            # Если настроек нет, создаем новые
            settings = SiteSettings.objects.create(
                site_name='MyBiz Витрина',
                site_tagline='Лучшие товары по доступным ценам',
                contact_email='info@mybiz.ru',
                contact_phone='+7 (999) 123-45-67',
                contact_address='Москва, ул. Примерная, д. 1',
                working_hours='Пн-Пт: 9:00-18:00, Сб: 10:00-16:00',
                telegram_url='https://t.me/mybiz',
                telegram_visible=True,
                vk_url='https://vk.com/mybiz',
                vk_visible=True,
                max_url='https://max.mail.ru/',
                max_visible=True,
                instagram_url='https://instagram.com/mybiz',
                instagram_visible=True,
                meta_title='MyBiz - Интернет-магазин',
                meta_description='Интернет-магазин качественных товаров',
                meta_keywords='магазин, товары, купить, онлайн, доставка',
                color_scheme='wood',
            )
            self.stdout.write(self.style.SUCCESS('✓ Настройки сайта созданы'))
            self.stdout.write(f'ID: {settings.id}')
            self.stdout.write(f'Название сайта: {settings.site_name}')
            self.stdout.write(f'Цветовая схема: {settings.color_scheme}')
            self.stdout.write(self.style.SUCCESS('✓ Применена цветовая схема "Дерево" по умолчанию'))
