# pages/models.py
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse


class Page(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL", blank=True)
    content = CKEditor5Field(verbose_name="Содержание", config_name='default')
    excerpt = models.TextField(blank=True, verbose_name="Краткое описание")

    meta_title = models.CharField(max_length=200, blank=True, verbose_name="Мета-заголовок")
    meta_description = models.TextField(blank=True, verbose_name="Мета-описание")
    meta_keywords = models.TextField(blank=True, verbose_name="Мета-ключевые слова")

    show_in_header = models.BooleanField(default=False, verbose_name="Показывать в шапке")
    show_in_footer = models.BooleanField(default=False, verbose_name="Показывать в подвале")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ['title']  # Убрал 'order', так как этого поля нет

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

        while Page.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

            if len(slug) > 200:
                slug = slug[:200]

        return slug

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'page_slug': self.slug})

    @classmethod
    def get_header_pages(cls):
        """Возвращает страницы для шапки сайта"""
        return cls.objects.filter(show_in_header=True, is_active=True).order_by('title')
