from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    image = models.ImageField(upload_to='promotions/', verbose_name="Изображение")
    description = RichTextField(verbose_name="Описание")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    button_text = models.CharField(max_length=50, blank=True, verbose_name="Текст кнопки")
    button_url = models.CharField(max_length=200, blank=True, verbose_name="URL кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    start_date = models.DateField(blank=True, null=True, verbose_name="Дата начала")
    end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Промо-акция"
        verbose_name_plural = "Промо-акции"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="MyBiz", verbose_name="Название сайта")
    site_tagline = models.CharField(max_length=200, blank=True, verbose_name="Слоган сайта")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Логотип")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Фавикон")
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Главное изображение")

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

    # Контактная информация
    contact_email = models.EmailField(blank=True, verbose_name="Контактный email")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Контактный телефон")
    contact_address = models.TextField(blank=True, verbose_name="Контактный адрес")
    working_hours = models.CharField(max_length=100, blank=True, verbose_name="Время работы")

    # Социальные сети
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter")

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
        # Разрешаем только одну запись настроек
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
