# config/settings/base.py | AI-Control v0.0.1 | 12-10-2026 09:19(GMT-04:00)
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'pgvector',
    'django_crypto_fields',
    'drf_spectacular',
    'django_extensions',
    
    # Local
    'core',
    'omnichannel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Políticas de CORS
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'ai-control'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
# Override via DATABASE_URL no local.py / production.py se necessário
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(default=os.environ['DATABASE_URL'])

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Cuiaba'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_OMNICHANNEL_REDIS_URL = os.environ.get('CELERY_OMNICHANNEL_REDIS_URL')

# Se for um worker dedicado ao omnichannel, sobrescreve o broker
if os.environ.get('WORKER_TYPE') == 'omnichannel' and CELERY_OMNICHANNEL_REDIS_URL:
    CELERY_BROKER_URL = CELERY_OMNICHANNEL_REDIS_URL

CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_TASK_ROUTES = {
    'omnichannel.tasks.*': {'queue': 'omnichannel'},
    'core.tasks.*': {'queue': 'celery'},
}

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'checkpoint-sessions-every-15-min': {
        'task': 'core.tasks.checkpoint.checkpoint_sessions',
        'schedule': crontab(minute='*/15'),
    },
}
# Channels (Daphne/WebSockets)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": os.environ.get('WHATS_GT_CHANNELS_REDIS_URL', 'redis://localhost:6379/1'),
                    "socket_timeout": None,
                    "socket_keepalive": True,
                    "health_check_interval": 180,
                }
            ],
        },
    },
}

# WhatsApp Gateway SaaS
WHATS_GT_API_URL = os.environ.get('WHATS_GT_API_URL', 'http://localhost:8081')
WHATS_GT_API_KEY = os.environ.get('WHATS_GT_API_KEY', '')
WHATS_GT_WEBHOOK_BASE_URL = os.environ.get('WHATS_GT_WEBHOOK_BASE_URL', 'http://localhost:8000')

# Crypto Fields
DJANGO_CRYPTO_FIELDS_KEY_PATH = os.environ.get('CRYPTO_KEY_PATH', os.path.join(BASE_DIR, 'crypto_keys/'))
AUTO_CREATE_KEYS = True
DJANGO_REVISION_IGNORE_WORKING_DIR = False
DJANGO_REVISION_REVISION = '1.0.0'
APP_NAME = 'config'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Configuração condicional de segurança OpenAPI (OWASP API9:2023)
if DEBUG:
    SPECTACULAR_SETTINGS = {
        'TITLE': 'AI-Control API',
        'DESCRIPTION': 'Documentação da API e Endpoints do AI-Control',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
        'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    }
else:
    SPECTACULAR_SETTINGS = {
        'TITLE': 'AI-Control API',
        'DESCRIPTION': 'Documentação da API e Endpoints do AI-Control (Produção)',
        'VERSION': '1.0.0',
        'SERVE_INCLUDE_SCHEMA': False,
        'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAdminUser'],
        'SECURITY': [{'BearerAuth': []}],
        'APPEND_COMPONENTS': {
            'securitySchemes': {
                'BearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                }
            }
        },
    }

# Usuário de serviço do bot (usado na migration de seed e no orquestrador)
BOT_USER_USERNAME = os.environ.get('BOT_USER_USERNAME', 'ai-bot')
