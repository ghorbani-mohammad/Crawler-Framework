import os
from envparse import env
from djangoeditorwidgets.config import *

from djangoeditorwidgets.config import init_web_editor_config
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
BOT_API_KEY = env.str("BOT_API_KEY")
ALLOWED_HOSTS = ["localhost", "crawler.m-gh.com"]
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
CELERY_ACCEPT_CONTENT = [
    "application/json",
]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tehran"


STATIC_URL = "/static/"
if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static")


REST_FRAMEWORK = {
    # When you enable API versioning, the request.version attribute will contain a string
    # that corresponds to the version requested in the incoming client request.
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Email Configs
EMAIL_HOST = "smtp-mail.outlook.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default=None)
EMAIL_USE_TLS = True

# Email Logging Configs
ADMIN_EMAIL_LOG = env("ADMIN_EMAIL_LOG", default=None)
ADMINS = (("Log Admin", ADMIN_EMAIL_LOG),)
SERVER_EMAIL = EMAIL_HOST_USER

# Logging (Just Email Handler)
if EMAIL_HOST_USER and ADMIN_EMAIL_LOG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "formatter": "simple",
            },
        },
        "loggers": {
            # all modules
            "": {
                "handlers": ["mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "celery": {
                "handlers": ["mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }


BASE_DIR_ = Path(__file__).resolve().parent.parent
WEB_EDITOR_DOWNLOAD, WEB_EDITOR_CONFIG = init_web_editor_config(
    # set the directory where files are downloaded
    BASE_DIR_ / "static",
    # set static url prefix
    STATIC_URL,
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
