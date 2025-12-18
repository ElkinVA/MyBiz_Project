# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# =========== НАСТРОЙКИ АДМИНКИ ===========
admin.site.site_title = "Администрирование"
admin.site.site_header = "Администрирование"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mybiz_core.urls', namespace='mybiz_core')),
    path('', include('pages.urls', namespace='pages')),
]

# Добавляем обработку медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
