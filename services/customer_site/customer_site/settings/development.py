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
        # ===== هندلر جدید برای افزودن به سبد خرید ===== #
        'cart_add_to_cart_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/add_to_cart_service.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        # ===== هندلر جدید برای سرویس فایل (در پوشه cart) ===== #
        'cart_file_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/file_service.log', 
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای لیست سبد خرید ===== #
        'cart_list_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/list_service.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای سرویس حذف سبد خرید ===== #
        'cart_delete_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/delete_service.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای سرویس فایل‌های موقت (Cart) ===== #
        'cart_temp_file_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/temp_file_service.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای جزئیات آیتم سبد خرید ===== #
        'cart_detail_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/detail_service.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر جدید برای اعتبارسنجی سبد خرید ===== #
        'cart_validator_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/validator.log', # ذخیره در پوشه cart
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر جدید برای سرویس بروزرسانی سبد خرید ===== #
        'cart_update_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/cart/update_service.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
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
        # ===== هندلر برای سرویس آدرس ===== #
        'userprofile_address_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/userprofile/address_service.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای سرویس پروفایل ===== #
        'userprofile_profile_service_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/userprofile/profile_service.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای سفارشات پروفایل کاربر ===== #
        'userprofile_orders_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/userprofile/orders.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ===== هندلر برای کیف پول پروفایل کاربر ===== #
        'userprofile_wallet_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/userprofile/wallet.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
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
        # ===== لاگر جدید برای سرویس افزودن به سبد خرید ===== #
        'cart.services.add_to_cart': {
            'handlers': ['cart_add_to_cart_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر جدید برای سرویس مدیریت فایل سبد خرید ===== #
        'cart.services.cart_file': {
            'handlers': ['cart_file_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس لیست سبد خرید ===== #
        'cart.services.list': {
            'handlers': ['cart_list_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس جزئیات آیتم ===== #
        'cart.services.detail': {
            'handlers': ['cart_detail_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس حذف/پاکسازی سبد خرید ===== #
        'cart.services.delete': {
            'handlers': ['cart_delete_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس فایل موقت ===== #
        'cart.services.temp_file': {
            'handlers': ['cart_temp_file_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر جدید سرویس اعتبارسنجی ===== #
        'cart.services.cart_validator': {
            'handlers': ['cart_validator_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس بروزرسانی ===== #
        'cart.services.update': {
            'handlers': ['cart_update_service_file', 'console'],
            'level': 'DEBUG',
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
        # ===== لاگر سرویس آدرس ===== #
        'userprofile.services.address': {
            'handlers': ['userprofile_address_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس پروفایل ===== #
        'userprofile.services.profile': {
            'handlers': ['userprofile_profile_service_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس سفارشات پروفایل ===== #
        'userprofile.services.orders': {
            'handlers': ['userprofile_orders_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # ===== لاگر سرویس کیف پول پروفایل ===== #
        'userprofile.services.wallet': {
            'handlers': ['userprofile_wallet_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
