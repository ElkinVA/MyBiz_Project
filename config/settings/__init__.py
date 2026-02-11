"""
Настройки проекта - экспорт основной конфигурации.
"""
import os
import sys  # <-- Добавьте эту строку

# Определяем среду выполнения
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')

# Переопределяем настройки в зависимости от среды
if 'production' in settings_module or os.environ.get('DJANGO_ENV') == 'production':
    try:
        from .production import *
        print("✅ Production настройки загружены")
    except ImportError as e:
        print(f"⚠️ Не удалось загрузить production настройки: {e}. Используются base настройки.")
        from .base import *
elif 'test' in sys.argv:
    # Тестовые настройки
    from .base import *
    # Можно добавить тестовые переопределения
else:
    # По умолчанию development настройки
    try:
        from .development import *
        print("✅ Development настройки загружены")
    except ImportError as e:
        print(f"⚠️ Не удалось загрузить development настройки: {e}. Используются base настройки.")
        from .base import *
