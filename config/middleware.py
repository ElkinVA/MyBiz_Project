from django.utils.deprecation import MiddlewareMixin

class CustomMiddleware(MiddlewareMixin):
    """Базовая кастомная middleware"""

    def process_request(self, request):
        # Добавляем пользовательские заголовки
        request.META['X-MyBiz-Version'] = '1.0.0'
        return None

    def process_response(self, request, response):
        # Добавляем security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        return response
