# config/settings/production.py
"""
Настройки для продакшена.
Этот файл загружается, когда DJANGO_SETTINGS_MODULE указывает на config.settings.production
ВАЖНО: Все чувствительные данные должны быть заданы через переменные окружения!
"""
import os
import warnings
from pathlib import Path

# Импортируем необходимые настройки из base
from .base import *

# ==============================================================================
# ПРОВЕРКА ОКРУЖЕНИЯ
# ==============================================================================
# Проверяем, что не запускаем в режиме разработки
if DEBUG:
    raise ValueError("DEBUG must be False in production environment!")

# Проверяем обязательные переменные окружения
required_env_vars = [
    'SECRET_KEY',
    'DB_NAME',
    'DB_USER',
    'DB_PASSWORD',
    'ALLOWED_HOSTS',
]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables in production: {missing_vars}\n"
        "Пожалуйста, установите эти переменные в вашем production окружении."
    )

# ==============================================================================
# БАЗОВЫЕ НАСТРОЙКИ
# ==============================================================================
# ✅ ИСПРАВЛЕНО: Валидация SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError(
        "SECRET_KEY must be set and at least 50 characters long in production!"
    )

# SECURITY WARNING: debug всегда False в продакшене
DEBUG = False

# Домены, с которых может работать приложение
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ['ALLOWED_HOSTS'].split(',')
    if host.strip()
]

# Список доверенных источников для CSRF
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
if not CSRF_TRUSTED_ORIGINS and not DEBUG:
    warnings.warn("CSRF_TRUSTED_ORIGINS is empty. Set it in production to avoid CSRF errors.")

# ==============================================================================
# БАЗА ДАННЫХ
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', 600)),  # Уменьшаем нагрузку на БД
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSLMODE', 'require'),
        },
        # ✅ ДОБАВЛЕНО: Pool settings для production
        'ATOMIC_REQUESTS': True,
    }
}

# ==============================================================================
# СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ
# ==============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')

# Медиа файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# Оптимизация статики с Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ ДОБАВЛЕНО: Ограничения на размер загружаемых файлов
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# ==============================================================================
# КЭШИРОВАНИЕ И СЕССИИ
# ==============================================================================
# Настройки Redis
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,  # секунд
            'SOCKET_TIMEOUT': 5,  # секунд
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': int(os.environ.get('REDIS_MAX_CONNECTIONS', 100)),
        },
        'KEY_PREFIX': os.environ.get('CACHE_KEY_PREFIX', 'mybiz'),
        # ✅ ДОБАВЛЕНО: Timeout для кэша
        'TIMEOUT': 300,
    }
}

# Используем кэш для сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# НАСТРОЙКИ БЕЗОПАСНОСТИ
# ==============================================================================
# HTTPS настройки
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# ✅ ИСПРАВЛЕНО: HSTS PRELOAD только если домен в preload list
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'

# Дополнительные заголовки безопасности
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Если приложение за reverse proxy (nginx, apache)
if os.environ.get('BEHIND_REVERSE_PROXY', 'False').lower() == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# Настройки CSRF
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# ЛОГИРОВАНИЕ
# ==============================================================================
# Создаем директорию для логов, если её нет
LOG_DIR = BASE_DIR / 'logs'
try:
    LOG_DIR.mkdir(exist_ok=True)
except (PermissionError, OSError):
    pass  # Логирование будет работать без файла

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django_error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['file', 'error_file', 'console'],
        'level': 'WARNING',
    },
}

# ==============================================================================
# EMAIL НАСТРОЙКИ
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes', 'on')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Таймауты для email
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 30))

# ==============================================================================
# ПРОИЗВОДИТЕЛЬНОСТЬ И ОПТИМИЗАЦИЯ
# ==============================================================================
# Конфигурация шаблонов для продакшена
for template in TEMPLATES:
    if template['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
        template['OPTIONS']['debug'] = False
        # Для продакшена можно использовать кэширование шаблонов
        template['OPTIONS']['loaders'] = [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ]

# ✅ ИСПРАВЛЕНО: GZipMiddleware в правильном месте
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # ← Перемещён выше
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

# Отключаем отслеживание миграций
MIGRATION_MODULES = {}

# ==============================================================================
# НАСТРОЙКИ ПРИЛОЖЕНИЯ
# ==============================================================================
# Отключаем debug toolbar и другие инструменты разработки
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')
if 'django_extensions' in INSTALLED_APPS:
    INSTALLED_APPS.remove('django_extensions')

# Убираем middleware для отладки
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# ==============================================================================
# КОНЕЧНЫЕ ПРОВЕРКИ
# ==============================================================================
# Убеждаемся, что все критические настройки верны
if DEBUG:
    print("WARNING: DEBUG is True in production settings!")
if SECRET_KEY.startswith('django-insecure-'):
    print("WARNING: Using insecure default secret key in production!")
if not ALLOWED_HOSTS:
    print("WARNING: ALLOWED_HOSTS is empty in production!")

print(f"Production settings loaded successfully for hosts: {ALLOWED_HOSTS}")
# ==============================================================================
# БЕЗОПАСНОСТЬ ПРОДАКШЕН
# ==============================================================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
