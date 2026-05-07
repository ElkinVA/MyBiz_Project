# content/admin.py
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, Promotion, StockNotification, NewsletterSubscriber
from .forms import SiteSettingsForm


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    save_on_top = False  # Убираем дублирование кнопок, форма не слишком длинная

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return HttpResponseRedirect(
            reverse('admin:content_sitesettings_change', args=[obj.id])
        )

    def response_change(self, request, obj):
        """
        Переопределяем поведение после сохранения.
        Добавляем сообщение об успешном сохранении через Django messages framework.
        """
        from django.contrib import messages
        messages.success(request, '✅ Настройки сайта успешно сохранены!')
        return super().response_change(request, obj)

    fieldsets = (
        ('📋 Основные настройки', {
            'fields': ('favicon',),
            'classes': ('collapse',),
            'description': 'Базовая информация о сайте'
        }),
        ('🎨 Цвета и схемы', {
            'fields': (
                'color_scheme',
                ('primary_color', 'secondary_color', 'accent_color'),
                ('text_color', 'background_color', 'border_color'),
                ('header_footer_bg_color', 'header_footer_text_color'),
            ),
            'classes': ('collapse',),
            'description': 'Выберите готовую цветовую схему или настройте цвета вручную. Изменение цветов переключает на пользовательскую схему.'
        }),
        ('🖥️ Шапка сайта (Header)', {
            'fields': (
                'site_name',
                'site_tagline',
                'logo',
            ),
            'classes': ('collapse',),
            'description': 'Название, слоган, логотип шапки'
        }),
        ('🖼️ Hero-секция', {
            'fields': (
                ('hero_image', 'hero_bg_color'),
                ('hero_heading_prefix', 'hero_subtitle'),
            ),
            'classes': ('collapse',),
            'description': 'Главный баннер и его фон'
        }),
        ('📝 Тексты главной страницы', {
            'fields': ('welcome_text',),
            'classes': ('collapse',)
        }),
        ('🛍️ Блок товаров', {
            'fields': ('featured_products_title', 'featured_products_subtitle'),
            'classes': ('collapse',)
        }),
        ('🏷️ Блок акций', {
            'fields': ('promotions_title', 'promotions_subtitle'),
            'classes': ('collapse',)
        }),
        ('📞 Контакты', {
            'fields': ('contact_phone', 'contact_email', 'contact_address', 'working_hours'),
            'classes': ('collapse',)
        }),
        ('🔗 Социальные сети', {
            'fields': (
                ('telegram_url', 'telegram_visible'),
                ('vk_url', 'vk_visible'),
                ('instagram_url', 'instagram_visible'),
                ('max_url', 'max_visible'),
            ),
            'classes': ('collapse',)
        }),
        ('🦶 Подвал сайта (Footer)', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'Цвета подвала теперь настраиваются в разделе «Цвета и схемы»'
        }),
        ('📊 SEO настройки', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['updated_at']

    class Media:
        css = {
            'all': (
                'admin/css/color-scheme.css',
                'admin/css/color-picker.css',
                'admin/css/color-fields-compact.css',
                'admin/css/admin-common.css',
            )
        }
        js = (
            'admin/js/color-scheme.js',
            'admin/js/color-picker.js',
            'admin/js/image-preview.js',
            'admin/js/contrast-checker.js',
        )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'start_date', 'end_date', 'created_at']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-start_date']
    list_per_page = 25
    actions = ['activate_promotions', 'deactivate_promotions']

    fieldsets = (
        ('📋 Основная информация', {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        ('🔗 Кнопка и ссылка', {
            'fields': ('button_text', 'button_url'),
            'classes': ('collapse',)
        }),
        ('💰 Скидка', {
            'fields': ('discount_type', 'discount_value'),
            'classes': ('wide',)
        }),
        ('🖼️ Изображение', {
            'fields': ('image',)
        }),
        ('📅 Период действия', {
            'fields': ('start_date', 'end_date', 'is_active'),
            'classes': ('collapse',)
        }),
        ('📊 Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def activate_promotions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} акций активированы', level='success')
    activate_promotions.short_description = '✅ Активировать'

    def deactivate_promotions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} акций деактивированы', level='warning')
    deactivate_promotions.short_description = '❌ Деактивировать'


@admin.register(StockNotification)
class StockNotificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'product', 'is_notified', 'created_at']
    list_filter = ['is_notified', 'created_at', 'product']
    search_fields = ['email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25

    actions = ['send_notification', 'mark_as_notified']

    def has_module_permission(self, request):
        """Скрывает раздел «Запросы о поступлении» со страницы приложений"""
        return False

    def send_notification(self, request, queryset):
        from django.core.mail import send_mail
        from django.conf import settings

        count = 0
        for notification in queryset:
            if not notification.is_notified and notification.product:
                try:
                    send_mail(
                        subject=f'Товар "{notification.product.name}" появился в наличии!',
                        message=f'Здравствуйте!\n\nТовар "{notification.product.name}" теперь доступен для покупки.\n\nПерейдите по ссылке: {notification.product.get_absolute_url()}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notification.email],
                        fail_silently=False,
                    )
                    notification.is_notified = True
                    notification.save()
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Ошибка отправки: {e}', level='error')

        if count > 0:
            self.message_user(request, f'{count} уведомлений отправлено', level='success')
    send_notification.short_description = '📧 Отправить уведомления'

    def mark_as_notified(self, request, queryset):
        queryset.update(is_notified=True)
        self.message_user(request, f'{queryset.count()} записей отмечены как уведомлённые', level='info')
    mark_as_notified.short_description = '✅ Отметить как уведомлённые'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25

    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_subscribers']

    def has_module_permission(self, request):
        """Скрывает раздел «Подписчики» со страницы приложений"""
        return False

    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} подписчиков активированы', level='success')
    activate_subscribers.short_description = '✅ Активировать'

    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} подписчиков деактивированы', level='warning')
    deactivate_subscribers.short_description = '❌ Деактивировать'

    def export_subscribers(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow(['Email', 'Активен', 'Дата подписки'])

        for obj in queryset:
            writer.writerow([obj.email, 'Да' if obj.is_active else 'Нет', obj.created_at.strftime('%d.%m.%Y %H:%M')])

        return response
    export_subscribers.short_description = '📥 Экспорт в CSV'
