from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField

class Page(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', unique=True, max_length=200)
    content = RichTextField('Содержание', blank=True)
    excerpt = models.TextField('Краткое описание', blank=True)
    meta_title = models.CharField('Мета-заголовок', max_length=200, blank=True)
    meta_description = models.TextField('Мета-описание', blank=True)
    meta_keywords = models.TextField('Мета-ключевые слова', blank=True)
    is_active = models.BooleanField('Активно', default=True)
    show_in_header = models.BooleanField('Показывать в шапке', default=False)  # НОВОЕ ПОЛЕ
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    @classmethod
    def get_header_pages(cls):
        """Возвращает страницы для отображения в шапке"""
        return cls.objects.filter(is_active=True, show_in_header=True).order_by('title')

    @classmethod
    def get_footer_pages(cls):
        """Возвращает страницы для отображения в футере"""
        return cls.objects.filter(is_active=True)[:4]

    class Meta:
        verbose_name = 'SEO-страница'
        verbose_name_plural = 'SEO-страницы'
        ordering = ['title']

    def get_absolute_url(self):
        return reverse('pages:page_detail', args=[self.slug])

    def __str__(self):
        return self.title
