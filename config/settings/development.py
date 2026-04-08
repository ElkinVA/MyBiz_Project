# config/settings/development.py
"""Настройки для разработки."""
import os
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

for template in TEMPLATES:
    if template['BACKEND'] == 'django.template.backends.django.DjangoTemplates':
        template['OPTIONS']['debug'] = True
        template['APP_DIRS'] = False
        template['OPTIONS']['loaders'] = [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]

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
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # 🔇 Подавляем отладочные сообщения шаблонов
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
