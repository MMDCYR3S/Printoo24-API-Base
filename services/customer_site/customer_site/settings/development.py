from .base import *

# ====== Databases (Postgresql) ====== #
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": 5432,
    }
}

# ====== Cache (Redis Settings) ====== #
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# ====== Celery Settings ====== #
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# ====== Email Settings ====== #
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env("EMAIL_HOST", default='smtp.gmail.com')
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="amingholami06@gmail.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="oojt ugkq exew ofbs")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)


# ====== Logging Settings ====== #
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
        # ====== Accounts Handlers ====== #
        'accounts_auth_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/accounts/auth_service.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'accounts_password_reset_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/accounts/password_reset_service.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'accounts_token_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/accounts/token_service.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'accounts_verification_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/accounts/verification_service.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'accounts_security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/accounts/security.log',
            'maxBytes': 1024 * 1024 * 20,  # 20 MB
            'backupCount': 15,
            'formatter': 'verbose',
        },
        
        # ====== Shop Handlers ====== #
        'shop_product_list_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/shop/product_list_service.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'shop_product_detail_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/shop/product_detail_service.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'shop_price_calculator_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/shop/price_calculator.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر جدید برای ایجاد سفارش ===== #
        'shop_order_creation_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/order/order_creation_service.log',
            'maxBytes': 1024 * 1024 * 20,  # 20 MB (increased size due to importance)
            'backupCount': 10,
            'formatter': 'verbose',
        },
        
        # ====== Console Handler ====== #
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        # ====== Accounts Loggers ====== #
        'accounts.services.auth': {
            'handlers': ['accounts_auth_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts.services.password_reset': {
            'handlers': ['accounts_password_reset_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts.services.token': {
            'handlers': ['accounts_token_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'accounts.services.verification': {
            'handlers': ['accounts_verification_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # ====== Security Logger ====== #
        'accounts.services.security': {
            'handlers': ['accounts_security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        # ====== Shop Loggers ====== #
        'shop.services.product_list': {
            'handlers': ['shop_product_list_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shop.services.product_detail': {
            'handlers': ['shop_product_detail_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'shop.services.price_calculator': {
            'handlers': ['shop_price_calculator_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر جدید برای سرویس ایجاد سفارش ===== #
        'shop.services.order_creation': {
            'handlers': ['shop_order_creation_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
