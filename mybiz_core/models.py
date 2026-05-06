# mybiz_core/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from .validators import validate_image_extension, validate_image_size, validate_image_dimensions
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models import Q, Count


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
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Автоматически генерирует slug из name если slug пустой"""
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug:
                base_slug = 'category'
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mybiz_core:product_list_by_category', kwargs={'category_slug': self.slug})

    def get_descendants_ids(self):
        """Возвращает список ID всех дочерних категорий (рекурсивно)"""
        ids = []
        for child in self.children.all():
            ids.append(child.pk)
            ids.extend(child.get_descendants_ids())
        return ids   # ← больше нет return внутри цикла

    @property
    def products_count(self):
        cache_key = f'category_{self.pk}_products_count'
        count = cache.get(cache_key)
        if count is None:
            category_ids = [self.pk]
            category_ids.extend(self.get_descendants_ids())
            count = Product.objects.filter(
                category_id__in=category_ids,
                is_active=True
            ).count()
            cache.set(cache_key, count, 300)
        return count

    def clear_cache(self):
        cache.delete('categories')


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
    # Единственное объявление price
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", db_index=True)
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
        blank=True,
        null=True,
        verbose_name="Изображение",
        validators=[validate_image_extension, validate_image_size, validate_image_dimensions]
    )
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, verbose_name="Рейтинг")
    review_count = models.IntegerField(default=0, verbose_name="Количество отзывов")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    stock = models.IntegerField(default=0, verbose_name="Остаток на складе")
    is_active = models.BooleanField(default=True, verbose_name="Активен", db_index=True)
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Дата создания", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mybiz_core:product_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def get_discount_percentage(self):
        if self.discount_price and self.price > 0:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return int(discount)
        return 0

    @property
    def display_price(self):
        return self.discount_price if self.discount_price else self.price


# Сигналы для очистки кэша
@receiver([post_save, post_delete], sender=Category)
def clear_categories_cache(sender, instance, **kwargs):
    cache.delete('categories')
    if instance and instance.pk:
        cache.delete(f'category_{instance.pk}_products_count')


@receiver([post_save, post_delete], sender=Product)
def clear_products_cache(sender, instance, **kwargs):
    cache.delete('featured_products')
    cache.delete('new_products')
    if instance and instance.category_id:
        cache.delete(f'category_{instance.category_id}_products_count')
