# content/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from django.utils.http import url_has_allowed_host_and_scheme
from .models import NewsletterSubscriber, SiteSettings, StockNotification, Promotion
from mybiz_core.models import Product
import logging

logger = logging.getLogger(__name__)


def get_safe_redirect_url(request, default='/'):
    redirect_to = request.META.get('HTTP_REFERER', default)
    if not url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        redirect_to = default
    return redirect_to


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Введите корректный email адрес.')
                return redirect(get_safe_redirect_url(request))
            try:
                sub, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                if created:
                    messages.success(request, 'Вы успешно подписались на рассылку!')
                else:
                    if not sub.is_active:
                        sub.is_active = True
                        sub.save()
                        messages.success(request, 'Подписка восстановлена!')
                    else:
                        messages.info(request, 'Этот email уже подписан на рассылку.')
            except Exception as e:
                logger.error(f"Ошибка подписки: {e}")
                messages.error(request, 'Произошла ошибка. Попробуйте позже.')
        else:
            messages.error(request, 'Введите корректный email.')
        return redirect(get_safe_redirect_url(request))
    return redirect(get_safe_redirect_url(request))


def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if not all([name, email, message]):
            messages.error(request, 'Пожалуйста, заполните все поля.')
            return redirect(get_safe_redirect_url(request))
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Введите корректный email адрес.')
            return redirect(get_safe_redirect_url(request))
        settings_obj = SiteSettings.load()
        to_email = settings_obj.contact_email or settings.DEFAULT_FROM_EMAIL or 'admin@localhost'
        subject = f'Сообщение от {name} с сайта {settings_obj.site_name}'
        body = f"Имя: {name}\nEmail: {email}\nСообщение:\n{message}"
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL or 'noreply@mybiz.ru',
                [to_email],
                fail_silently=False,
            )
            messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
        except Exception as e:
            logger.error(f"Ошибка отправки письма: {e}")
            messages.error(request, 'Не удалось отправить сообщение. Попробуйте позже.')
        return redirect(get_safe_redirect_url(request))
    return redirect(get_safe_redirect_url(request))


def stock_notify(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        email = request.POST.get('email', '').strip()
        if email:
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Введите корректный email адрес.')
                return redirect(get_safe_redirect_url(request))
            try:
                notification, created = StockNotification.objects.get_or_create(
                    product=product,
                    email=email,
                    defaults={'is_notified': False}
                )
                if created:
                    messages.success(
                        request,
                        f'Мы уведомим вас на {email}, когда товар "{product.name}" поступит в продажу.'
                    )
                else:
                    if notification.is_notified:
                        messages.info(request, 'Вы уже получили уведомление о поступлении этого товара.')
                    else:
                        messages.info(request, 'Вы уже подписаны на уведомление о поступлении этого товара.')
            except Exception as e:
                logger.error(f"Ошибка создания уведомления: {e}")
                messages.error(request, 'Произошла ошибка. Попробуйте позже.')
        else:
            messages.error(request, 'Введите корректный email.')
        return redirect(get_safe_redirect_url(request))
    return redirect(get_safe_redirect_url(request))


class PromotionListView(ListView):
    model = Promotion
    template_name = 'promotions/promotion_list.html'
    context_object_name = 'promotions'
    paginate_by = 9

    def get_queryset(self):
        return Promotion.objects.filter(is_active=True).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Акции и предложения'
        return context
