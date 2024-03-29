import os
from .base import *
from datetime import timedelta

DEBUG = False
ACCOUNT_EMAIL_VERIFICATION = "none"

# For storage
DEFAULT_FILE_STORAGE = "github_storages.backend.BackendStorages"
GITHUB_HANDLE = os.environ.get("GITHUB_USERNAME")
ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
GITHUB_REPO_NAME = os.environ.get("GITHUB_REPO_NAME")
MEDIA_BUCKET_NAME = "media"
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ["https://doosti.onrender.com","https://doostiapp.onrender.com"]
SESSION_COOKIE_SECURE = True

ALLOWED_HOSTS = [
    "http://127.0.0.0.1:8000",
    "https://doosti.onrender.com",
    "doosti.onrender.com"
]

# Django cors headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8888",
    "https://doostiapp.onrender.com",
]

# Channels Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_HOSTNAME")],
        },
    },
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}

# Jwt setting
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# To maintain loging in production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # "handlers": {
    #     "console": {
    #         "class": "logging.StreamHandler",
    #     },
    #     "file": {
    #         "level": "DEBUG",
    #         "class": "logging.FileHandler",
    #         "filename": "log.django",
    #     },
    # },
    # "loggers": {
    #     "django": {
    #         "handlers": ["console", "file"],
    #         "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
    #     },
    # },
}
