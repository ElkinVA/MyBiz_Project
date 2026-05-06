# config/settings/base.py
"""
Базовые настройки для проекта MyBiz.
Этот файл импортируется из development.py и production.py
"""
import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured
import warnings

# ==============================================================================
# БАЗОВЫЕ ПУТИ
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# БЕЗОПАСНОСТЬ
# ==============================================================================
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# ✅ ИСПРАВЛЕНО: Безопасная обработка SECRET_KEY
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key-change-in-production-abc123xyz789'
        warnings.warn("⚠️ Используется insecure SECRET_KEY для разработки!")
    else:
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable must be set in production!"
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# ✅ ИСПРАВЛЕНО: host → origin в list comprehension
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# ==============================================================================
# ПРИЛОЖЕНИЯ
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Сторонние приложения
    'rest_framework',        # ← добавлен DRF
    'django_filters',
    'django_ckeditor_5',
    'sorl.thumbnail',
    'auditlog',
    # Локальные приложения
    'mybiz_core',
    'content',
    'pages',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ==============================================================================
# ШАБЛОНЫ
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Контекст-процессоры проекта
                'content.context_processors.site_settings',
                'content.context_processors.promotions',
                'content.context_processors.header_pages',
                'content.context_processors.footer_pages',
                'mybiz_core.context_processors.categories',
                # Контекст-процессоры админки
                'mybiz_core.context_processors.admin_dashboard_stats',
                'mybiz_core.context_processors.admin_user_info',
            ],
        },
    },
]

# ==============================================================================
# WSGI
# ==============================================================================
WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# БАЗА ДАННЫХ
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'timeout': 20,
        },
    }
}

# ==============================================================================
# ПАРОЛИ
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# ИНТЕРНАЦИОНАЛИЗАЦИЯ
# ==============================================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ
# ==============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ==============================================================================
# КЭШИРОВАНИЕ
# ==============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mybiz-cache',
        'TIMEOUT': 300,
    }
}

# ==============================================================================
# СЕССИИ
# ==============================================================================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# DEBUG TOOLBAR НАСТРОЙКИ
# ==============================================================================

# ==============================================================================
# DJANGO CKEDITOR 5 НАСТРОЙКИ
# ==============================================================================
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote',
            '|', 'undo', 'redo'
        ],
        'language': 'ru',
    },
    'minimal': {
        'toolbar': [
            'bold', 'italic', 'link', 'bulletedList', 'numberedList',
            '|', 'undo', 'redo'
        ],
        'language': 'ru',
    },
    'extends': {
        'toolbar': {
            'items': [
                'heading', 'heading1', 'heading2', 'heading3', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'alignment', '|',
                'bulletedList', 'numberedList', 'todoList', '|',
                'outdent', 'indent', '|',
                'link', 'insertImage', 'insertTable', 'mediaEmbed', '|',
                'blockQuote', 'code', 'codeBlock', '|',
                'subscript', 'superscript', '|',
                'horizontalLine', 'pageBreak', '|',
                'specialCharacters', 'highlight', '|',
                'undo', 'redo', 'removeFormat',
            ],
            'shouldNotGroupWhenFull': True,
        },
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:inline',
                'imageStyle:block', 'imageStyle:side',
                'linkImage', 'imageResize'
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableCellProperties', 'tableProperties'
            ]
        },
        'language': 'ru',
    },
}

CKEDITOR_5_FILE_UPLOAD_PERMISSION = "staff"
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = False
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp', 'svg']

# ==============================================================================
# SORL.THUMBNAIL НАСТРОЙКИ
# ==============================================================================
THUMBNAIL_BACKEND = 'sorl.thumbnail.base.ThumbnailBackend'
THUMBNAIL_KEY_PREFIX = 'mybiz'
THUMBNAIL_QUALITY = 95
THUMBNAIL_PRESERVE_FORMAT = True

# ==============================================================================
# AUDITLOG НАСТРОЙКИ
# ==============================================================================
AUDITLOG_INCLUDE_ALL_MODELS = False
AUDITLOG_DISABLE_ON_RAW_SAVE = False

# ==============================================================================
# ЗАГРУЗКА ФАЙЛОВ
# ==============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# ==============================================================================
# ЛОГИРОВАНИЕ
# ==============================================================================
LOG_DIR = BASE_DIR / 'logs'
try:
    LOG_DIR.mkdir(exist_ok=True)
except (PermissionError, OSError):
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# DRF настройки (троттлинг)
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
