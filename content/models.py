# content/models.py
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from mybiz_core.validators import validate_image_extension, validate_image_size, validate_image_dimensions
import re
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    description = CKEditor5Field(verbose_name="Описание", config_name='default')
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    button_text = models.CharField(max_length=50, blank=True, verbose_name="Текст кнопки")
    button_url = models.CharField(max_length=200, blank=True, verbose_name="URL кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    image = models.ImageField(
        upload_to='promotions/',
        verbose_name="Изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )

    class Meta:
        verbose_name = "Промо-акция"
        verbose_name_plural = "Промо-акции"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def _generate_unique_slug(self, title):
        """Генерирует уникальный slug"""
        base_slug = slugify(title, allow_unicode=True)
        slug = base_slug
        counter = 1

        while Promotion.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

            if len(slug) > 200:
                slug = slug[:200]

        return slug


class SiteSettings(models.Model):
    # Выбор цветовой схемы
    COLOR_SCHEME_CHOICES = [
        ('wood', '🌳 Дерево - Натуральные экологичные тона'),
        ('coffee', '☕ Кофе - Теплые уютные оттенки'),
        ('flower', '🌺 Цветок - Яркая сбалансированная палитра'),
        ('vintage', '📻 Винтаж - Классические приглушенные тона'),
        ('pastel', '🎨 Пастель - Мягкие нежные цвета'),
        ('custom', '✏️ Пользовательская тема - Настройте цвета вручную'),
    ]

    color_scheme = models.CharField(
        max_length=20,
        choices=COLOR_SCHEME_CHOICES,
        default='wood',
        verbose_name="Цветовая схема сайта",
        help_text="Выберите одну из 5 готовых профессиональных схем или настройте вручную"
    )

    # Основные настройки сайта
    site_name = models.CharField(max_length=100, default="MyBiz", verbose_name="Название сайта")
    site_tagline = models.CharField(max_length=200, blank=True, verbose_name="Слоган сайта")

    favicon = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name="Фавикон",
        validators=[validate_image_extension, validate_image_size]
    )

    logo = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name="Логотип",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )

    hero_image = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name="Главное изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )

    # Цветовая палитра
    primary_color = models.CharField(
        max_length=7,
        default='#3b82f6',
        verbose_name="Основной цвет (Primary)",
        help_text="Основной цвет бренда"
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#8b5cf6',
        verbose_name="Вторичный цвет (Secondary)",
        help_text="Дополнительный цвет"
    )
    accent_color = models.CharField(
        max_length=7,
        default='#10b981',
        verbose_name="Акцентный цвет (Accent)",
        help_text="Цвет для кнопок и важных элементов"
    )
    text_color = models.CharField(
        max_length=7,
        default='#1f2937',
        verbose_name="Цвет текста",
        help_text="Основной цвет текста"
    )
    background_color = models.CharField(
        max_length=7,
        default='#f9fafb',
        verbose_name="Цвет фона",
        help_text="Фоновый цвет сайта"
    )
    header_bg_color = models.CharField(
        max_length=7,
        default='#ffffff',
        verbose_name="Фон шапки",
        help_text="Фон верхней части сайта"
    )
    footer_bg_color = models.CharField(
        max_length=7,
        default='#111827',
        verbose_name="Фон подвала",
        help_text="Фон нижней части сайта"
    )
    hero_bg_color = models.CharField(
        max_length=7,
        default='#eff6ff',
        verbose_name="Фон герой-секции",
        help_text="Фоновый цвет главного баннера на главной странице"
    )

    # Контактная информация
    contact_email = models.EmailField(blank=True, verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Контактный телефон")
    contact_address = models.TextField(blank=True, verbose_name="Контактный адрес")
    working_hours = models.CharField(max_length=100, blank=True, verbose_name="Время работы")

    # Социальные сети с видимостью
    telegram_url = models.URLField(blank=True, verbose_name="Telegram")
    telegram_visible = models.BooleanField(default=True, verbose_name="Показывать Telegram")
    vk_url = models.URLField(blank=True, verbose_name="VK")
    vk_visible = models.BooleanField(default=True, verbose_name="Показывать VK")
    max_url = models.URLField(blank=True, verbose_name="MAX")
    max_visible = models.BooleanField(default=True, verbose_name="Показывать MAX")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    instagram_visible = models.BooleanField(default=True, verbose_name="Показывать Instagram")

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Мета-заголовок")
    meta_description = models.TextField(blank=True, verbose_name="Мета-описание")
    meta_keywords = models.TextField(blank=True, verbose_name="Мета-ключевые слова")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Singleton pattern - обновляем существующую запись или создаем новую
        if SiteSettings.objects.exists() and not self.pk:
            # Обновляем существующую запись вместо создания новой
            existing = SiteSettings.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':
                    setattr(existing, field.name, getattr(self, field.name))

            # Применяем цветовую схему для существующей записи
            if existing.color_scheme != 'custom':
                colors = SiteSettings.get_scheme_colors_by_name(existing.color_scheme)
                for field_name, color_value in colors.items():
                    if hasattr(existing, field_name):
                        setattr(existing, field_name, color_value)

            # Валидация HEX цветов
            existing._validate_hex_colors()

            # Сохраняем через прямой вызов родительского метода save
            return super(SiteSettings, existing).save(*args, **kwargs)

        # Применяем цветовую схему при сохранении
        if self.color_scheme != 'custom':
            colors = SiteSettings.get_scheme_colors_by_name(self.color_scheme)
            for field_name, color_value in colors.items():
                if hasattr(self, field_name):
                    setattr(self, field_name, color_value)

        # Валидация HEX цветов
        self._validate_hex_colors()

        super().save(*args, **kwargs)

    def _validate_hex_colors(self):
        """Валидация HEX цветов"""
        hex_fields = ['primary_color', 'secondary_color', 'accent_color',
                     'text_color', 'background_color', 'header_bg_color',
                     'footer_bg_color', 'hero_bg_color']

        for field_name in hex_fields:
            color = getattr(self, field_name, '')
            if color and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
                raise ValidationError(f'Поле {field_name}: неверный формат HEX цвета')

    @classmethod
    def load(cls):
        """Загружает или создает настройки сайта"""
        obj, created = cls.objects.get_or_create(
            defaults={
                'site_name': 'MyBiz Витрина',
                'site_tagline': 'Лучшие товары по доступным ценам',
                'contact_email': 'info@mybiz.ru',
                'contact_phone': '+7 (999) 123-45-67',
                'contact_address': 'Москва, ул. Примерная, д. 1',
                'working_hours': 'Пн-Пт: 9:00-18:00, Сб: 10:00-16:00',
                'color_scheme': 'wood',
            }
        )
        return obj

    def get_visible_social_links(self):
        """Возвращает список видимых социальных сетей"""
        social_links = []

        if self.telegram_url and self.telegram_visible:
            social_links.append({
                'name': 'Telegram',
                'url': self.telegram_url,
                'icon': 'telegram',
                'title': 'Telegram'
            })

        if self.vk_url and self.vk_visible:
            social_links.append({
                'name': 'VK',
                'url': self.vk_url,
                'icon': 'vk',
                'title': 'ВКонтакте'
            })

        if self.max_url and self.max_visible:
            social_links.append({
                'name': 'MAX',
                'url': self.max_url,
                'icon': 'max',
                'title': 'MAX (Мессенджер Mail.ru)'
            })

        if self.instagram_url and self.instagram_visible:
            social_links.append({
                'name': 'Instagram',
                'url': self.instagram_url,
                'icon': 'instagram',
                'title': 'Instagram'
            })

        return social_links

    @staticmethod
    def get_scheme_colors_by_name(scheme_name):
        """Возвращает цвета для указанной схемы"""
        schemes = {
            'wood': {
                'primary_color': '#2e8b57',
                'secondary_color': '#8b7355',
                'accent_color': '#d2691e',
                'text_color': '#2f4f4f',
                'background_color': '#f5f5f5',
                'header_bg_color': '#ffffff',
                'footer_bg_color': '#556b2f',
                'hero_bg_color': '#8fbc8f',
            },
            'coffee': {
                'primary_color': '#6f4e37',
                'secondary_color': '#8b7355',
                'accent_color': '#d2691e',
                'text_color': '#3e2723',
                'background_color': '#fff8e1',
                'header_bg_color': '#5d4037',
                'footer_bg_color': '#3e2723',
                'hero_bg_color': '#a1887f',
            },
            'flower': {
                'primary_color': '#e91e63',
                'secondary_color': '#9c27b0',
                'accent_color': '#ff9800',
                'text_color': '#5d4037',
                'background_color': '#fff3e0',
                'header_bg_color': '#fce4ec',
                'footer_bg_color': '#9c27b0',
                'hero_bg_color': '#f8bbd0',
            },
            'vintage': {
                'primary_color': '#8d6e63',
                'secondary_color': '#a1887f',
                'accent_color': '#5d4037',
                'text_color': '#4e342e',
                'background_color': '#efebe9',
                'header_bg_color': '#d7ccc8',
                'footer_bg_color': '#5d4037',
                'hero_bg_color': '#bcaaa4',
            },
            'pastel': {
                'primary_color': '#f8bbd0',
                'secondary_color': '#c5cae9',
                'accent_color': '#80deea',
                'text_color': '#546e7a',
                'background_color': '#fce4ec',
                'header_bg_color': '#f3e5f5',
                'footer_bg_color': '#b39ddb',
                'hero_bg_color': '#e1bee7',
            },
            'custom': {}
        }
        return schemes.get(scheme_name, schemes['wood'])

    def clear_cache(self):
        from django.core.cache import cache
        cache.delete('site_settings')
        cache.delete('active_promotions')
        cache.delete('header_pages')
        cache.delete('visible_social_links')

@receiver(post_save, sender=SiteSettings)
def clear_site_settings_cache(sender, instance, **kwargs):
    """Очищает кэш настроек сайта при сохранении"""
    from django.core.cache import cache
    cache_keys = ['site_settings', 'active_promotions', 'header_pages', 'visible_social_links']
    for key in cache_keys:
        cache.delete(key)
    logger.info(f"Кэш настроек сайта очищен: {instance}")
