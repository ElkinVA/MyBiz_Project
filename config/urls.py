# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.contrib import messages

# =========== НАСТРОЙКИ АДМИНКИ ===========
admin.site.site_title = "Администрирование MyBiz"
admin.site.site_header = "Панель управления MyBiz"
admin.site.index_title = "Управление сайтом"

# Заглушки для форм (временно)
@csrf_protect
def contact_form_placeholder(request):
    """Временная заглушка для формы контактов"""
    if request.method == 'POST':
        messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect('/')

@csrf_protect
def newsletter_subscribe_placeholder(request):
    """Временная заглушка для формы подписки"""
    if request.method == 'POST':
        messages.success(request, 'Вы успешно подписались на рассылку!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mybiz_core.urls', namespace='mybiz_core')),
    path('', include('pages.urls', namespace='pages')),
    path('contact/', contact_form_placeholder, name='contact_form'),
    path('newsletter/subscribe/', newsletter_subscribe_placeholder, name='newsletter_subscribe'),
]

# Добавляем обработку медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug toolbar
try:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
except ImportError:
    pass  # debug_toolbar не установлен

# Обработчики ошибок
handler400 = 'mybiz_core.views.bad_request'
handler403 = 'mybiz_core.views.permission_denied'
handler404 = 'mybiz_core.views.page_not_found'
handler500 = 'mybiz_core.views.server_error'
