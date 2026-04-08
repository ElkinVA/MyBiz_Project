# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ==============================================================================
# НАСТРОЙКИ АДМИНКИ
# ==============================================================================
admin.site.site_title = "Администрирование MyBiz"
admin.site.site_header = "Панель управления MyBiz"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path('admin/', admin.site.urls),
    # ✅ ВАЖНО: Подключение URL для CKEditor 5 (загрузка файлов)
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # Основные приложения
    path('', include('mybiz_core.urls', namespace='mybiz_core')),
    path('', include('pages.urls', namespace='pages')),
    path('', include('content.urls', namespace='content')),
]

# ==============================================================================
# МЕДИА И СТАТИКА (только для DEBUG=True)
# ==============================================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# ==============================================================================
# ОБРАБОТЧИКИ ОШИБОК
# ==============================================================================
handler400 = 'mybiz_core.views.bad_request'
handler403 = 'mybiz_core.views.permission_denied'
handler404 = 'mybiz_core.views.page_not_found'
handler500 = 'mybiz_core.views.server_error'
