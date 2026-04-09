from django.apps import AppConfig


class MempalaceIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mempalace_integration'
    verbose_name = 'Интеграция MemPalace'
    
    def ready(self):
        # Импортируем сигналы при загрузке приложения
        try:
            from . import signals
        except ImportError:
            pass
