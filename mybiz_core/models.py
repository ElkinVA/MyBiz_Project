# mybiz_core/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from .validators import validate_image_extension, validate_image_size, validate_image_dimensions


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская категория"
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Мета-заголовок")
    meta_description = models.TextField(blank=True, verbose_name="Мета-описание")
    meta_keywords = models.TextField(blank=True, verbose_name="Мета-ключевые слова")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # ИСПРАВЛЕНО: используем правильное имя URL
        return reverse('mybiz_core:product_list_by_category', kwargs={'category_slug': self.slug})

    @property
    def products_count(self):
        """Количество товаров в категории (включая подкатегории)"""
        count = self.products.filter(is_active=True).count()
        for child in self.children.all():
            count += child.products_count
        return count


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Категория"
    )
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    description = CKEditor5Field(verbose_name="Описание", config_name='default')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Цена со скидкой"
    )
    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Бренд")
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="Рейтинг")
    review_count = models.IntegerField(default=0, verbose_name="Количество отзывов")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    stock = models.IntegerField(default=0, verbose_name="Остаток на складе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mybiz_core:product_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_discount_percentage(self):
        """Возвращает процент скидки"""
        if self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return int(discount)
        return 0

    @property
    def display_price(self):
        """Возвращает отображаемую цену (со скидкой если есть)"""
        return self.discount_price if self.discount_price else self.price
