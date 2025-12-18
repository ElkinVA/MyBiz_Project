from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from .validators import validate_image_extension, validate_image_size, validate_image_dimensions

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Изображение",
        validators=[
            validate_image_extension,
            validate_image_size,
            validate_image_dimensions,
        ]
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']
        indexes = [
            # Индекс для активных категорий с сортировкой по имени (используется в контекстном процессоре)
            models.Index(fields=['is_active', 'name'], name='category_active_name_idx'),
            # Индекс для сортировки по порядку
            models.Index(fields=['is_active', 'order'], name='category_active_order_idx'),
            # Индекс для быстрого поиска по slug
            models.Index(fields=['slug'], name='category_slug_idx'),
        ]

    def get_absolute_url(self):
        return reverse('mybiz_core:product_list_by_category', args=[self.slug])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название товара")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    stock = models.IntegerField(default=0, verbose_name="Остаток на складе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    sku = models.CharField('Артикул', max_length=100, blank=True)
    brand = models.CharField('Бренд', max_length=200, blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0)
    review_count = models.IntegerField('Количество отзывов', default=0)
    is_new = models.BooleanField('Новинка', default=False)
    in_stock = models.BooleanField('В наличии', default=True)
    discount_price = models.DecimalField('Цена со скидкой', max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Основное изображение",
        validators=[
            validate_image_extension,
            validate_image_size,
            validate_image_dimensions,
        ]
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            # Основные индексы для фильтрации
            models.Index(fields=['category', 'is_active'], name='product_category_active_idx'),
            models.Index(fields=['is_active', 'created_at'], name='product_active_created_idx'),
            # Индексы для дополнительных фильтров
            models.Index(fields=['is_featured', 'is_active'], name='product_featured_active_idx'),
            models.Index(fields=['in_stock', 'is_active'], name='product_stock_active_idx'),
            # Индекс для быстрого поиска по slug
            models.Index(fields=['slug'], name='product_slug_idx'),
            # Индекс для сортировки по цене
            models.Index(fields=['is_active', 'price'], name='product_active_price_idx'),
        ]

    def get_discount_percentage(self):
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return int(discount)
        return 0

    def get_absolute_url(self):
        return reverse('mybiz_core:product_detail', args=[self.slug])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def has_discount(self):
        return self.old_price and self.old_price > self.price
