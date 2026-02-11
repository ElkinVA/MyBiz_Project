# config/settings/development.py
"""
Настройки для разработки.
Этот файл загружается, когда DJANGO_SETTINGS_MODULE указывает на config.settings.development
"""
import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Укажите хосты, с которых можно обращаться к сайту во время разработки
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Используем SQLite для разработки, как указано в .env и base.py
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        # Учет других параметров, если они указаны (хотя для sqlite не обязательны)
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Куда collectstatic будет собирать файлы

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cache
# Для разработки часто используют dummy cache, чтобы видеть изменения сразу
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache', # Отключает кэш
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG', # Выводить все сообщения уровня DEBUG и выше в консоль
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email backend for development (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Whitenoise для раздачи статики (удобно для разработки, если нужно протестировать)
# Убедитесь, что 'whitenoise.middleware.WhiteNoiseMiddleware' уже добавлен в base.py
# MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware') # Не добавляем дважды!
