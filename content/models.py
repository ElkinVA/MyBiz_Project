# content/models.py
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field
from mybiz_core.validators import validate_image_extension, validate_image_size, validate_image_dimensions
import re
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

logger = logging.getLogger(__name__)


class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Процент (%)'),
        ('fixed', 'Фиксированная сумма (₽)'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    description = CKEditor5Field(verbose_name="Описание", config_name='extends')
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    button_text = models.CharField(max_length=50, blank=True, verbose_name="Текст кнопки")
    button_url = models.CharField(max_length=200, blank=True, verbose_name="URL кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name="Дата обновления")
    image = models.ImageField(
        upload_to='promotions/',
        verbose_name="Изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )
    # ✅ ДОБАВЛЕНО: Тип скидки и значение
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name="Тип скидки"
    )
    discount_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Значение скидки",
        db_index=True
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна", db_index=True)
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала", db_index=True)
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания", db_index=True)

    class Meta:
        verbose_name = "Промо-акция"
        verbose_name_plural = "Промо-акции"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug(self.title)
        super().save(*args, **kwargs)

    def _generate_unique_slug(self, title):
        base_slug = slugify(title, allow_unicode=True)
        slug = base_slug
        counter = 1
        while Promotion.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            if len(slug) > 200:
                slug = slug[:200]
        return slug

    def apply_discount(self, price):
        """
        Применяет скидку к цене.
        
        Args:
            price: Исходная цена (Decimal)
            
        Returns:
            Decimal: Цена со скидкой
        """
        from decimal import Decimal
        
        if not self.discount_value or self.discount_value <= 0:
            return price
            
        if self.discount_type == 'percent':
            # Процентная скидка: цена - (цена * процент / 100)
            discount_amount = price * (self.discount_value / Decimal('100'))
        else:
            # Фиксированная скидка: цена - сумма
            discount_amount = self.discount_value
        
        final_price = price - discount_amount
        # Цена не может быть отрицательной
        return max(final_price, Decimal('0'))


class SiteSettings(models.Model):
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
    )

    # ===== ПОЛЯ С ВИЗУАЛЬНЫМ РЕДАКТОРОМ =====
    site_name = models.CharField(
        max_length=200,
        default="MyBiz",
        verbose_name="Название сайта",
        help_text="Название сайта"
    )
    site_tagline = models.CharField(
        max_length=200,
        blank=True,
        default="Лучшие товары по доступным ценам",
        verbose_name="Слоган сайта",
        help_text="Краткий слоган"
    )
    hero_heading_prefix = models.CharField(
        max_length=100,
        blank=True,
        default="Добро пожаловать в",
        verbose_name="Префикс заголовка (hero)",
        help_text="Текст перед названием сайта в главном баннере"
    )

    # ===== ОСТАЛЬНЫЕ ПОЛЯ =====
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

    # ===== ЦВЕТОВЫЕ ПОЛЯ =====
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
    # ✅ ДОБАВЛЕНО: Поле border_color
    border_color = models.CharField(
        max_length=7,
        default='#e5e7eb',
        verbose_name="Цвет границ",
        help_text="Цвет границ элементов"
    )

    # ----- Поля главной страницы -----
    welcome_text = CKEditor5Field(
        blank=True,
        default='Современная витрина качественных товаров. Мы тщательно отбираем каждый продукт, чтобы предложить вам лучшее сочетание цены и качества.',
        verbose_name='Приветственный текст',
        help_text='Основной текст под заголовком на главной (поддерживает форматирование)',
        config_name='extends'
    )
    hero_subtitle = models.CharField(
        max_length=200,
        blank=True,
        default='Лучшие товары по доступным ценам',
        verbose_name='Подзаголовок Hero',
        help_text='Отображается под названием сайта на главной. Если пусто – используется site_tagline'
    )
    promotions_title = models.CharField(
        max_length=200,
        blank=True,
        default='Специальные предложения',
        verbose_name='Заголовок блока акций',
        help_text='Заголовок секции акций'
    )
    promotions_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default='Не упустите возможность приобрести товары по выгодным ценам',
        verbose_name='Подзаголовок блока акций'
    )
    featured_products_title = models.CharField(
        max_length=200,
        blank=True,
        default='Популярные товары',
        verbose_name='Заголовок блока популярных товаров',
        help_text='Заголовок секции популярных товаров'
    )
    featured_products_subtitle = models.CharField(
        max_length=300,
        blank=True,
        default='Самые востребованные товары среди наших покупателей',
        verbose_name='Подзаголовок блока популярных товаров'
    )

    # ===== КОНТАКТЫ =====
    contact_email = models.EmailField(blank=True, verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Контактный телефон")
    contact_address = models.TextField(blank=True, verbose_name="Контактный адрес")
    working_hours = models.CharField(max_length=100, blank=True, verbose_name="Время работы")

    # ===== СОЦИАЛЬНЫЕ СЕТИ =====
    telegram_url = models.URLField(blank=True, verbose_name="Telegram")
    telegram_visible = models.BooleanField(default=True, verbose_name="Показывать Telegram")
    vk_url = models.URLField(blank=True, verbose_name="VK")
    vk_visible = models.BooleanField(default=True, verbose_name="Показывать VK")
    max_url = models.URLField(blank=True, verbose_name="MAX")
    max_visible = models.BooleanField(default=True, verbose_name="Показывать MAX")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    instagram_visible = models.BooleanField(default=True, verbose_name="Показывать Instagram")

    # ===== SEO =====
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Мета-заголовок")
    meta_description = models.TextField(blank=True, verbose_name="Мета-описание")
    meta_keywords = models.TextField(blank=True, verbose_name="Мета-ключевые слова")

    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # ✅ ИСПРАВЛЕНО: Безопасная установка pk=1
        if not self.pk and SiteSettings.objects.exists():
            existing = SiteSettings.objects.first()
            if existing:
                self.pk = existing.pk
            else:
                self.pk = 1
        else:
            self.pk = 1

        if self.color_scheme != 'custom':
            colors = SiteSettings.get_scheme_colors_by_name(self.color_scheme)
            for field_name, color_value in colors.items():
                if hasattr(self, field_name):
                    setattr(self, field_name, color_value)

        self._validate_hex_colors()
        return super().save(*args, **kwargs)

    def _validate_hex_colors(self):
        """✅ ИСПРАВЛЕНО: Валидация с нормализацией цветов"""
        hex_fields = [
            'primary_color', 'secondary_color', 'accent_color',
            'text_color', 'background_color', 'header_bg_color',
            'footer_bg_color', 'hero_bg_color', 'border_color'
        ]
        for field_name in hex_fields:
            color = getattr(self, field_name, '')
            if color:
                # Нормализация короткого формата
                color = color.lstrip('#')
                if len(color) == 3:
                    color = ''.join([c*2 for c in color])
                    setattr(self, field_name, f'#{color}')
                elif not re.match(r'^[A-Fa-f0-9]{6}$', color):
                    raise ValidationError(f'Поле {field_name}: неверный формат HEX цвета')

    @classmethod
    def load(cls):
        """
        Загружает настройки сайта.
        ✅ ИСПРАВЛЕНО: Использует first() вместо жесткой привязки к id=1
        """
        cache_key = 'site_settings'
        obj = cache.get(cache_key)
        
        if obj is None:
            obj = cls.objects.first()
            if not obj:
                # Создаем настройки по умолчанию если их нет
                obj = cls.objects.create(
                    site_name='MyBiz Витрина',
                    site_tagline='Лучшие товары по доступным ценам',
                    contact_email='info@mybiz.ru',
                    contact_phone='+7 (999) 123-45-67',
                    contact_address='Москва, ул. Примерная, д. 1',
                    working_hours='Пн-Пт: 9:00-18:00, Сб: 10:00-16:00',
                    color_scheme='wood',
                )
            cache.set(cache_key, obj, 600)
        
        return obj

    def get_visible_social_links(self):
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
        schemes = {
            'wood': {
                'primary_color': '#2E5C44',
                'secondary_color': '#4F3A2B',
                'accent_color': '#D9734C',
                'text_color': '#1E2B26',
                'background_color': '#F3F0E9',
                'header_bg_color': '#FFFFFF',
                'footer_bg_color': '#2C4238',
                'hero_bg_color': '#DFD9CE',
                'border_color': '#e5e7eb',
            },
            'coffee': {
                'primary_color': '#87492E',
                'secondary_color': '#684E39',
                'accent_color': '#E6B17E',
                'text_color': '#342015',
                'background_color': '#FCF5E8',
                'header_bg_color': '#FFFFFF',
                'footer_bg_color': '#583C2B',
                'hero_bg_color': '#F0E2D3',
                'border_color': '#e5e7eb',
            },
            'flower': {
                'primary_color': '#8F2E55',
                'secondary_color': '#624766',
                'accent_color': '#F9A26C',
                'text_color': '#2D232E',
                'background_color': '#FEF6F9',
                'header_bg_color': '#FFFFFF',
                'footer_bg_color': '#663A5F',
                'hero_bg_color': '#FCE4E4',
                'border_color': '#e5e7eb',
            },
            'vintage': {
                'primary_color': '#5F4F3F',
                'secondary_color': '#5F4A3A',
                'accent_color': '#B95C3C',
                'text_color': '#31261D',
                'background_color': '#EEE7DF',
                'header_bg_color': '#F8F1E8',
                'footer_bg_color': '#53453A',
                'hero_bg_color': '#DBCFC2',
                'border_color': '#e5e7eb',
            },
            'pastel': {
                'primary_color': '#2E5454',
                'secondary_color': '#7A4F4F',
                'accent_color': '#5E4563',
                'text_color': '#202A33',
                'background_color': '#F9F6F0',
                'header_bg_color': '#FFFFFF',
                'footer_bg_color': '#38434D',
                'hero_bg_color': '#E2F0F0',
                'border_color': '#e5e7eb',
            },
            'custom': {}
        }
        return schemes.get(scheme_name, schemes['wood'])

    def clear_cache(self):
        cache.delete('site_settings')
        cache.delete('active_promotions')
        cache.delete('header_pages')
        cache.delete('visible_social_links')


@receiver(post_save, sender=SiteSettings)
def clear_site_settings_cache(sender, instance, **kwargs):
    cache_keys = ['site_settings', 'active_promotions', 'header_pages', 'visible_social_links']
    for key in cache_keys:
        cache.delete(key)
    logger.info(f"Кэш настроек сайта очищен: {instance}")


@receiver([post_save, post_delete], sender=Promotion)
def clear_promotions_cache(sender, **kwargs):
    cache.delete('active_promotions')


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class StockNotification(models.Model):
    product = models.ForeignKey('mybiz_core.Product', on_delete=models.CASCADE, verbose_name="Товар")
    email = models.EmailField(verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    is_notified = models.BooleanField(default=False, verbose_name="Уведомление отправлено")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'email'], name='unique_product_email')
        ]
        verbose_name = "Запрос о поступлении"
        verbose_name_plural = "Запросы о поступлении"

    def __str__(self):
        return f"{self.email} - {self.product.name}"
