import os
from envparse import env
from djangoeditorwidgets.config import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
BOT_API_KEY = env.str("BOT_API_KEY")
ALLOWED_HOSTS = ["crawler.m-gh.com"]
SERVER_IP = env.str("SERVER_IP")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rangefilter",
    "rest_framework",
    "agency",
    "social",
    "notification",
    "clear_cache",
    "prettyjson",
    "djangoeditorwidgets",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "crawler.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "crawler.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASS"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Asia/Tehran"

# CELERY
BROKER_URL = "redis://crawler_redis:6379"
CELERY_RESULT_BACKEND = "redis://crawler_redis:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")


REST_FRAMEWORK = {
    # When you enable API versioning, the request.version attribute will contain a string
    # that corresponds to the version requested in the incoming client request.
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REDIS_EXPORTER_LOCK_KEY = "redis_exporter_lock"

if not DEBUG:
    log_path = "/var/log/app/"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "general_log_file": {
                "level": "INFO",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": os.path.join(log_path, "logs.log"),
                "formatter": "standard",
            },
            "celery_log_file": {
                "level": "INFO",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": os.path.join(log_path, "celery.log"),
                "formatter": "standard",
            },
        },
        "loggers": {
            # all modules
            "": {
                "handlers": ["general_log_file"],
                "level": "INFO",
            },
            "celery": {
                "handlers": ["celery_log_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
