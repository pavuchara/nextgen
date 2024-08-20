from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

DEBUG = str(os.getenv('DEBUG')) == 'True'

# TODO Fix this
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    os.getenv('HOST_URL'),
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
    'http://nextgen-blog.pavuk-django.ru',
    'https://nextgen-blog.pavuk-django.ru',
]

# For debug.
INTERNAL_IPS = [
    'nextgen-blog.pavuk-django.ru',
]

# Application definition

INSTALLED_APPS = [
    # Base apps.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Self apps.
    'apps.blog.apps.BlogConfig',
    'apps.user_app.apps.UserAppConfig',
    'apps.core.apps.CoreConfig',
    # Packages.
    'mptt',
    'django_mptt_admin',
    'debug_toolbar',
    'django_bootstrap5',
    'taggit',
    'django_recaptcha',
    'ckeditor_uploader',
    'ckeditor',
    'social_django',
]

MIDDLEWARE = [
    # Base middleware.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # From packages.
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Self apps.
    'apps.user_app.middleware.ActiveUserMiddleware',
]

ROOT_URLCONF = 'blog_nextgen.urls'

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
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_nextgen.wsgi.application'


if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'django'),
            'USER': os.getenv('POSTGRES_USER', 'django'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', ''),
            'PORT': os.getenv('DB_PORT', 5432)
        }
    }


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

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Статика.
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / STATIC_URL / 'js_back',
    BASE_DIR / STATIC_URL / 'js_bootstrap',
]

# Медиа.
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = 'uploads/'

CKEDITOR_CONFIGS = {
    'awesome_ckeditor': {
        'toolbar': 'full',
        'height': 300,
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis
REDIS_HOST = 'redis'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'

# Переопределенная модель пользователя.
AUTH_USER_MODEL = 'user_app.NextgenUser'

# Переадресация на главную после логина.
LOGIN_REDIRECT_URL = 'blog:home'

# Генерацию слагов для тегов с поддержкой транслитерации.
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING = True

# reCAPTCHA secret keys
RECAPTCHA_PUBLIC_KEY = str(os.getenv('RECAPTCHA_PUBLIC_KEY'))
RECAPTCHA_PRIVATE_KEY = str(os.getenv('RECAPTCHA_PRIVATE_KEY'))

# Обработка ошибки 403 связанной с csrf.
CSRF_FAILURE_VIEW = 'apps.core.views.custom_403csrf'

# Ключи авторизации google.
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = str(os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'))
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = str(os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'))
