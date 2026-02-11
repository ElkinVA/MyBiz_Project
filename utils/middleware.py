# utils/middleware.py
import hashlib
import time
from django.conf import settings


class CacheBusterMiddleware:
    """Middleware для добавления версии кэша к статическим файлам"""

    def __init__(self, get_response):
        self.get_response = get_response
        # Генерируем уникальную версию при запуске сервера
        self.cache_version = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        """Добавляет версию кэша только для TemplateResponse"""
        if hasattr(response, 'context_data'):
            response.context_data = response.context_data or {}
            response.context_data['CACHE_VERSION'] = self.cache_version
        return response


class NoCacheDebugMiddleware:
    """Middleware для отключения кэширования в режиме отладки"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if settings.DEBUG:
            # Отключаем кэширование в режиме разработки
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
