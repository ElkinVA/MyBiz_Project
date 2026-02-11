from django.http import JsonResponse
from django.views.decorators.http import require_GET
from content.models import SiteSettings
import time

# Глобальная переменная для отслеживания времени последнего изменения
LAST_UPDATE_TIME = {}

@require_GET
def check_color_update(request):
    """API endpoint для проверки обновлений цветов"""
    global LAST_UPDATE_TIME

    try:
        settings = SiteSettings.load()
        current_time = settings.updated_at.timestamp()

        # Проверяем, было ли обновление
        last_time = LAST_UPDATE_TIME.get('site_settings', 0)

        if current_time > last_time:
            LAST_UPDATE_TIME['site_settings'] = current_time
            return JsonResponse({
                'needs_update': True,
                'last_update': current_time,
                'colors': {
                    'primary': settings.primary_color,
                    'secondary': settings.secondary_color,
                    'accent': settings.accent_color,
                }
            })
        else:
            return JsonResponse({
                'needs_update': False,
                'last_update': last_time
            })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'needs_update': False
        }, status=500)
