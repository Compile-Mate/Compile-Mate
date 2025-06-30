"""
Django settings for compilemate project.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow all hosts (not recommended for production, restrict to your domain/IP for security)
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'crispy_tailwind',
    'django_htmx',
    'tailwind',
    'django_browser_reload',
    'debug_toolbar',
    'django_extensions',
    'django_filters',
    # 'django_ratelimit',  # Temporarily disabled due to cache backend issues
    'cacheops',
    'django_celery_results',
    'django_celery_beat',
    
    # Local apps
    'core',
    'problems',
    'contests',
    'rewards',
    'judge',
    'users',
    'theme',
    'channels',
    'resume_scanner',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'compilemate.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'compilemate.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Site ID for allauth
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Tailwind CSS
TAILWIND_APP_NAME = 'theme'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

# Try to use Redis if available, otherwise fallback to database cache
try:
    import redis
    redis_client = redis.Redis.from_url(config('REDIS_URL', default='redis://127.0.0.1:6379/1'))
    redis_client.ping()  # Test connection
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        }
    }
    CACHEOPS_REDIS = config('REDIS_URL', default='redis://127.0.0.1:6379/2')
    CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
except (ImportError, redis.ConnectionError):
    # Fallback to database cache if Redis is not available
    CACHEOPS_REDIS = None
    CELERY_BROKER_URL = 'memory://'
    print("Warning: Redis not available, using database cache and memory broker")

# Celery settings
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Cacheops settings - only enable if Redis is available
if CACHEOPS_REDIS:
    CACHEOPS = {
        'problems.Problem': {'ops': 'all', 'timeout': 60*15},
        'contests.Contest': {'ops': 'all', 'timeout': 60*15},
        'users.User': {'ops': 'all', 'timeout': 60*15},
    }
else:
    # Disable cacheops if Redis is not available
    CACHEOPS = {}

# Judge0 API settings
JUDGE0_API_URL = config('JUDGE0_API_URL', default='https://judge0-ce.p.rapidapi.com')
JUDGE0_API_KEY = config('JUDGE0_API_KEY', default='')

# MateCoins settings
INITIAL_COINS = 100
COINS_PER_ACCEPTED_SOLUTION = 10
COINS_PER_HARD_PROBLEM = 25
COINS_PER_CONTEST_PARTICIPATION = 50
COINS_PER_WEEKLY_STREAK = 100

# Debug toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],  # Log to both file and console
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Google OAuth Credentials (add these to your .env file)
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret 

# Email backend
if DEBUG:
    # For development: write emails to files
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
else:
    # For production: use SMTP or a transactional email service
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@compilemate.com')

# Recommended production settings for scalability and efficiency
# -------------------------------------------------------------
# 1. Use Redis for cache and Celery broker (already supported in this config)
# 2. Use a production-ready database (e.g., PostgreSQL)
# 3. Set DEBUG = False and configure ALLOWED_HOSTS
# 4. Use a real email backend (see above)
# 5. Set up static/media file hosting (e.g., AWS S3, GCP Storage)
# 6. Use a WSGI/ASGI server (e.g., Gunicorn, Daphne, Uvicorn) behind a reverse proxy (e.g., Nginx)
# 7. Enable HTTPS in production
# 8. Monitor logs and errors (e.g., Sentry, ELK stack)
# 9. Set up proper security settings (SECURE_*, CSRF_COOKIE_SECURE, etc.)
# 10. Use environment variables for all secrets and credentials

# Real-Time Chat Support System Configuration
# ===========================================

# ASGI Application for WebSocket support
ASGI_APPLICATION = 'compilemate.asgi.application'

# Channel Layers for WebSocket communication
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [config('REDIS_URL', default='redis://127.0.0.1:6379/3')],
        },
    },
}

# Fallback to in-memory channel layer if Redis is not available
try:
    import redis
    redis_client = redis.Redis.from_url(config('REDIS_URL', default='redis://127.0.0.1:6379/3'))
    redis_client.ping()  # Test connection
except (ImportError, redis.ConnectionError):
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    print("Warning: Redis not available for WebSockets, using in-memory channel layer")

# Chat Support System Settings
# ============================

# Chat configuration
CHAT_SETTINGS = {
    'MAX_MESSAGE_LENGTH': 1000,
    'MAX_FILE_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_FILE_TYPES': ['image/jpeg', 'image/png', 'image/gif', 'text/plain', 'application/pdf'],
    'AUTO_ASSIGN_ENABLED': True,
    'MAX_ADMIN_CHATS': 5,
    'CHAT_TIMEOUT': 30 * 60,  # 30 minutes
    'POLLING_INTERVAL': 3000,  # 3 seconds
}

# Admin availability settings
ADMIN_AVAILABILITY = {
    'DEFAULT_WORKING_HOURS': {
        'monday': {'start': '09:00', 'end': '17:00'},
        'tuesday': {'start': '09:00', 'end': '17:00'},
        'wednesday': {'start': '09:00', 'end': '17:00'},
        'thursday': {'start': '09:00', 'end': '17:00'},
        'friday': {'start': '09:00', 'end': '17:00'},
        'saturday': {'start': '10:00', 'end': '15:00'},
        'sunday': {'start': '10:00', 'end': '15:00'},
    },
    'DEFAULT_TIMEZONE': 'UTC',
    'DEFAULT_SPECIALIZATIONS': ['general', 'technical', 'billing'],
    'DEFAULT_LANGUAGES': ['English'],
}

# Chat notification settings
CHAT_NOTIFICATIONS = {
    'ENABLE_EMAIL_NOTIFICATIONS': True,
    'ENABLE_PUSH_NOTIFICATIONS': False,
    'NEW_CHAT_EMAIL_TEMPLATE': 'emails/new_chat_notification.html',
    'CHAT_RESOLVED_EMAIL_TEMPLATE': 'emails/chat_resolved_notification.html',
}

# Chat rating and feedback settings
CHAT_RATING = {
    'ENABLE_RATINGS': True,
    'REQUIRE_RATING': False,
    'RATING_REMINDER_HOURS': 24,
    'MIN_RATING_FOR_BONUS': 4,
    'RATING_BONUS_COINS': 5,
}

# Chat widget settings
CHAT_WIDGET = {
    'ENABLE_FLOATING_WIDGET': True,
    'WIDGET_POSITION': 'bottom-right',
    'WIDGET_COLOR': '#3B82F6',
    'WELCOME_MESSAGE': 'Hi! Need help? Our support team is here to assist you.',
    'QUICK_ACTIONS': [
        {'label': 'General Question', 'category': 'general', 'description': 'Ask about the platform'},
        {'label': 'Technical Issue', 'category': 'technical', 'description': 'Report bugs or problems'},
        {'label': 'Billing & Payments', 'category': 'billing', 'description': 'Questions about MateCoins'},
    ],
}

# Chat security settings
CHAT_SECURITY = {
    'RATE_LIMIT_MESSAGES': 10,  # messages per minute
    'RATE_LIMIT_CHATS': 3,  # new chats per hour
    'BLOCK_SPAM_KEYWORDS': ['spam', 'advertisement', 'promotion'],
    'REQUIRE_AUTHENTICATION': True,
    'ALLOW_ANONYMOUS_CHATS': False,
}

# Chat analytics settings
CHAT_ANALYTICS = {
    'TRACK_RESPONSE_TIMES': True,
    'TRACK_SATISFACTION_SCORES': True,
    'TRACK_CHAT_DURATIONS': True,
    'TRACK_CATEGORY_DISTRIBUTION': True,
    'ENABLE_ADMIN_PERFORMANCE_METRICS': True,
}

# File upload settings for chat attachments
CHAT_FILE_UPLOAD = {
    'MAX_FILE_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_EXTENSIONS': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt'],
    'UPLOAD_PATH': 'chat_attachments/',
    'ENABLE_IMAGE_PREVIEW': True,
    'ENABLE_FILE_DOWNLOAD': True,
}

# Chat template settings
CHAT_TEMPLATES = {
    'ENABLE_TEMPLATES': True,
    'DEFAULT_TEMPLATES': [
        {
            'name': 'Welcome Message',
            'category': 'general',
            'content': 'Hello! Welcome to CompileMate. How can I help you today?',
        },
        {
            'name': 'Technical Issue Response',
            'category': 'technical',
            'content': 'I understand you\'re experiencing a technical issue. Let me help you resolve this.',
        },
        {
            'name': 'Billing Question Response',
            'category': 'billing',
            'content': 'Thank you for your question about billing and MateCoins. Let me clarify how our reward system works.',
        },
    ],
}

# Chat export and backup settings
CHAT_BACKUP = {
    'ENABLE_AUTO_BACKUP': True,
    'BACKUP_INTERVAL_DAYS': 7,
    'RETAIN_CHAT_LOGS_DAYS': 365,
    'ENABLE_CHAT_EXPORT': True,
    'EXPORT_FORMATS': ['json', 'csv'],
}

# Performance optimization settings
CHAT_PERFORMANCE = {
    'MESSAGE_CACHE_TIMEOUT': 300,  # 5 minutes
    'CHAT_LIST_CACHE_TIMEOUT': 60,  # 1 minute
    'ENABLE_MESSAGE_PAGINATION': True,
    'MESSAGES_PER_PAGE': 50,
    'ENABLE_LAZY_LOADING': True,
}

# Integration settings
CHAT_INTEGRATIONS = {
    'ENABLE_SLACK_INTEGRATION': False,
    'ENABLE_DISCORD_INTEGRATION': False,
    'ENABLE_EMAIL_INTEGRATION': True,
    'ENABLE_WEBHOOK_INTEGRATION': False,
}

# Development and testing settings
if DEBUG:
    CHAT_SETTINGS.update({
        'ENABLE_DEBUG_LOGGING': True,
        'SHOW_ADMIN_DEBUG_INFO': True,
        'ENABLE_TEST_MODE': True,
    })
    
    # Add test admin user for development
    CHAT_DEVELOPMENT = {
        'CREATE_TEST_ADMIN': True,
        'TEST_ADMIN_USERNAME': 'admin',
        'TEST_ADMIN_EMAIL': 'admin@compilemate.com',
        'TEST_ADMIN_PASSWORD': 'admin123',
    } 