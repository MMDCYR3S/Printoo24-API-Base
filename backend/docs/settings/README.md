# مستندات تنظیمات پروژه Printoo24 Backend

## 📋 پیش‌نیاز
- مطالعه [مستندات معماری کلی](../00_architecture_overview.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار تنظیمات](#ساختار-تنظیمات)
3. [تنظیمات پایه (base.py)](#تنظیمات-پایعه-basepy)
4. [تنظیمات توسعه (development.py)](#تنظیمات-توسعه-developmentpy)
5. [تنظیمات تولید (production.py)](#تنظیمات-تولید-productionpy)
6. [متغیرهای محیطی](#متغیرهای-محیطی)
7. [نکات مهم](#نکات-مهم)

---

## مقدمه

پروژه Printoo24 از ساختار تنظیمات چند محیطی Django استفاده می‌کند. این ساختار امکان استفاده از تنظیمات متفاوت برای محیط‌های توسعه، تست و تولید را فراهم می‌کند بدون نیاز به تغییر کد.

### 🎯 اهداف این ساختار:
- ✅ جداسازی تنظیمات بین محیط‌ها
- ✅ امنیت بیشتر (رمزهای عبور و کلیدها در محیط production متفاوت)
- ✅ قابلیت توسعه آسان
- ✅ کاهش خطاهای انسانی

---

## ساختار تنظیمات

### نمای کلی فایل‌های تنظیمات:

```
backend/
└── backend/
    └── settings/
        ├── __init__.py          # فایل خالی برای تبدیل به پکیج
        ├── base.py              # تنظیمات مشترک تمام محیط‌ها
        ├── development.py       # تنظیمات محیط توسعه
        └── production.py        # تنظیمات محیط تولید
```

### نحوه کار:

```
┌─────────────────────────────────────────┐
│         manage.py                       │
│  (تعیین محیط پیش‌فرض)                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  DJANGO_SETTINGS_MODULE                 │
│  = "backend.settings.development"       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  development.py                         │
│  (import everything from base.py)       │
│  (override specific settings)           │
└─────────────────────────────────────────┘
```

---

## تنظیمات پایه (base.py)

### 📍 موقعیت: `backend/backend/settings/base.py`

### هدف:
این فایل شامل تمام تنظیمات مشترک بین تمام محیط‌ها است. فایل‌های development و production از این فایل import می‌کنند و فقط تنظیمات خاص خودشان را override می‌کنند.

### بخش‌های اصلی:

#### 1. **مسیرهای پروژه (Paths)**
```python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
```
- مسیر اصلی پروژه
- تمام مسیرهای دیگر نسبت به این مسیر تعریف می‌شوند

#### 2. **متغیرهای محیطی (Environment Variables)**
```python
env = environ.Env(
    DEBUG=(bool, True)
)
env_file = os.path.join(BASE_DIR, 'env/.env.dev')
environ.Env.read_env(env_file)
```
- استفاده از `django-environ` برای خواندن متغیرهای محیطی
- فایل `.env.dev` در پوشه `env/` قرار دارد
- **نکته امنیتی**: فایل‌های `.env` هرگز در Git commit نمی‌شوند

#### 3. **تنظیمات امنیتی**
```python
SECRET_KEY = env('SECRET_KEY')
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = ["*"]
```
- `SECRET_KEY`: کلید رمزنگاری Django (باید در production تغییر کند)
- `DEBUG`: حالت دیباگ (در production باید False باشد)
- `ALLOWED_HOSTS`: دامنه‌های مجاز (در production باید محدود شود)

#### 4. **اپلیکیشن‌های نصب شده (INSTALLED_APPS)**
```python
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + APPLICATIONS
```

**DJANGO_APPS** (اپلیکیشن‌های داخلی Django):
- `django.contrib.admin` - پنل مدیریت
- `django.contrib.auth` - سیستم احراز هویت
- `django.contrib.contenttypes` - نوع محتوا
- `django.contrib.sessions` - مدیریت session
- `django.contrib.messages` - سیستم پیام‌ها
- `django.contrib.staticfiles` - فایل‌های استاتیک
- `django.contrib.sites` - سیستم سایت‌ها

**THIRD_PARTY_APPS** (کتابخانه‌های شخص ثالث):
- `rest_framework` - Django REST Framework
- `rest_framework_simplejwt` - احراز هویت JWT
- `corsheaders` - مدیریت CORS
- `django_filters` - فیلتر کردن
- `redis` - اتصال به Redis
- `django_redis` - کش Django با Redis
- `django_celery_beat` - زمان‌بندی Celery
- `django_celery_results` - نتایج Celery
- `drf_spectacular` - مستندات API
- `drf_yasg` - Swagger UI

**APPLICATIONS** (اپلیکیشن‌های پروژه):
- `core` - هسته مشترک
- `apps.accounts` - احراز هویت
- `apps.shop` - فروشگاه
- `apps.order` - سفارشات
- `apps.home` - صفحه اصلی
- `apps.cart` - سبد خرید
- `apps.userprofile` - پروفایل کاربر
- `apps.notification` - اعلان‌ها
- `apps.dashboard` - داشبورد مدیریت
- `apps.blog` - وبلاگ

#### 5. **میان‌افزارها (Middleware)**
```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.append('apps.accounts.middleware.AutoLoginSuperuserMiddleware')
```
- ترتیب middlewareها مهم است
- در حالت دیباگ، middleware اضافی برای ورود خودکار ادمین اضافه می‌شود

#### 6. **تنظیمات Django REST Framework**
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'accounts_login': '50/min',
        'accounts_verify': '30/min',
        'accounts_register': '30/hour',
    },
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "EXCEPTION_HANDLER": "core.product.exception_handler.product_exception_handler",
}
```

**توضیحات:**
- **احراز هویت**: پیش‌فرض JWT است
- **مجوزها**: پیش‌فرض نیاز به احراز هویت دارد
- **Throttle (محدودیت نرخ)**:
  - کاربران ناشناس: 100 درخواست در روز
  - کاربران عادی: 1000 درخواست در روز
  - ورود به حساب: 50 در دقیقه
  - تأیید حساب: 30 در دقیقه
  - ثبت‌نام: 30 در ساعت
- **فیلتر**: استفاده از django-filter
- **Schema**: تولید خودکار مستندات با drf-spectacular
- **Exception Handler**: هندلر سفارشی برای خطاها

#### 7. **تنظیمات JWT**
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=300),      # 5 ساعت
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),          # 1 روز
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
}
```
- توکن دسترسی: 5 ساعت اعتبار
- توکن تمدید: 1 روز اعتبار
- الگوریتم: HS256

#### 8. **تنظیمات فایل‌های استاتیک و مدیا**
```python
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```
- فایل‌های استاتیک: CSS، JS، تصاویر استاتیک
- فایل‌های مدیا: فایل‌های آپلودی کاربران

#### 9. **مدل کاربر سفارشی**
```python
AUTH_USER_MODEL = 'core.User'
```
- به جای مدل پیش‌فرض Django، از مدل `core.User` استفاده می‌شود

#### 10. **تنظیمات مستندات API**
```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Printoo24 API',
    'DESCRIPTION': 'API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'docExpansion': 'none',
    },
    'COMPONENT_SPLIT_REQUEST': True,
}
```
- عنوان: Printoo24 API
- نسخه: 1.0.0
- قابلیت‌های Swagger UI

---

## تنظیمات توسعه (development.py)

### 📍 موقعیت: `backend/backend/settings/development.py`

### هدف:
تنظیمات خاص محیط توسعه (Local Development)

### تنظیمات اصلی:

#### 1. **import تنظیمات پایه**
```python
from .base import *
```
- تمام تنظیمات base.py اینجا اعمال می‌شوند

#### 2. **پایگاه داده (Database)**
```python
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
```
- **PostgreSQL** به عنوان دیتابیس
- تمام اطلاعات از متغیرهای محیطی خوانده می‌شود

#### 3. **کش (Cache)**
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```
- **Redis** برای کش
- دیتابیس شماره 1 Redis

#### 4. **Celery (وظایف ناهمزمان)**
```python
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
```
- **Redis** به عنوان Broker (صف پیام)
- دیتابیس شماره 0 Redis
- فرمت JSON برای تسک‌ها

#### 5. **ایمیل (Email)**
```python
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env("EMAIL_HOST", default='smtp.gmail.com')
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="amingholami06@gmail.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="oojt ugkq exew ofbs")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
```
- استفاده از SMTP Gmail به صورت پیش‌فرض
- تمام تنظیمات قابل تغییر با متغیرهای محیطی

#### 6. **CORS (Cross-Origin Resource Sharing)**
```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://localhost:5173',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-guest-token',
]
```
- در توسعه، تمام origins مجاز هستند
- در production باید محدود شود

#### 7. **CSRF Trusted Origins**
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://localhost:5173',
]
```
- دامنه‌های قابل اعتماد برای CSRF

#### 8. **لاگ‌گذاری (Logging)**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # ... (بخش بزرگ لاگینگ - 527 خط!)
}
```

**ویژگی‌های لاگینگ:**
- **فرمت‌ها**: verbose و simple
- **هندلرها**: فایل و کنسول
- **RotatingFileHandler**: فایل‌های لاگ با اندازه محدود (5-20 MB)
- **بک‌آپ**: نگهداری 5-15 فایل لاگ قدیمی
- **لاگرهای اختصاصی**: برای هر سرویس یک لاگر جدا

**دسته‌بندی لاگرها:**
1. **Accounts**: auth، password_reset، token، verification، security
2. **Cart**: add_to_cart، cart_file، list، detail، delete، temp_file، validator، update
3. **Shop**: product_list، product_detail، price_calculator، order_creation، feedback
4. **UserProfile**: address، profile، orders، wallet، notification
5. **Dashboard**: product_dashboard، tasks، cart_dashboard، customer، wallet

**مثال استفاده:**
```python
import logging
logger = logging.getLogger('shop.services.product_list')
logger.info("Product list retrieved successfully")
logger.error("Failed to fetch products", exc_info=True)
```

---

## تنظیمات تولید (production.py)

### 📍 موقعیت: `backend/backend/settings/production.py`

### وضعیت:
این فایل در حال حاضر خالی است و باید طبق نیازهای production تکمیل شود.

### تنظیمات مورد نیاز برای production:

```python
from .base import *

# Security
DEBUG = False
ALLOWED_HOSTS = ['printoo24.com', 'www.printoo24.com', 'api.printoo24.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database (Production PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': 5432,
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Cache (Production Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_TIMEOUT': 5,
            'SOCKET_CONNECT_TIMEOUT': 5,
        }
    }
}

# Celery (Production)
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Email (Production SMTP)
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', 587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# CORS (Production - Restrictive)
CORS_ALLOWED_ORIGINS = [
    'https://printoo24.com',
    'https://www.printoo24.com',
]
CORS_ALLOW_CREDENTIALS = True

# CSRF (Production)
CSRF_TRUSTED_ORIGINS = [
    'https://printoo24.com',
    'https://www.printoo24.com',
]

# Logging (Production - Less verbose)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Static files (Production - WhiteNoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (Production - S3 or similar)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
```

---

## متغیرهای محیطی

### فایل `.env.dev` (توسعه)
**موقعیت**: `env/.env.dev`

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
POSTGRES_DB=printoo24_db
POSTGRES_USER=printoo24_user
POSTGRES_PASSWORD=printoo24_pass
POSTGRES_HOST=localhost

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# API Documentation
SWAGGER_TOKEN=your-swagger-token
```

### فایل `.env.production` (تولید)
**موقعیت**: `env/.env.production`

```env
# Django
SECRET_KEY=very-secure-secret-key-production
DEBUG=False
ALLOWED_HOSTS=printoo24.com,www.printoo24.com,api.printoo24.com

# Database
POSTGRES_DB=printoo24_prod_db
POSTGRES_USER=printoo24_prod_user
POSTGRES_PASSWORD=very-secure-password
POSTGRES_HOST=prod-db-host

# Redis
REDIS_URL=redis://prod-redis:6379/0

# Celery
CELERY_BROKER_URL=redis://prod-redis:6379/0
CELERY_RESULT_BACKEND=redis://prod-redis:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=info@printoo24.com
EMAIL_HOST_PASSWORD=very-secure-email-password
DEFAULT_FROM_EMAIL=info@printoo24.com

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=printoo24-media
AWS_S3_REGION_NAME=us-east-1
```

### نحوه خواندن متغیرها:
```python
# در فایل‌های Python
value = env('VARIABLE_NAME')
value_with_default = env('VARIABLE_NAME', default='default_value')
int_value = env.int('INT_VARIABLE', default=42)
bool_value = env.bool('BOOL_VARIABLE', default=True)
```

---

## نکات مهم

### 1. **امنیت**
- ❌ هرگز فایل‌های `.env` را در Git commit نکنید
- ✅ از کلیدهای SECRET_KEY متفاوت در هر محیط استفاده کنید
- ✅ در production، `DEBUG = False` باشد
- ✅ `ALLOWED_HOSTS` را در production محدود کنید
- ✅ از HTTPS در production استفاده کنید

### 2. **بهینه‌سازی**
- ✅ در production از WhiteNoise یا CDN برای فایل‌های استاتیک استفاده کنید
- ✅ برای فایل‌های مدیا از S3 یا similar استفاده کنید
- ✅ Connection pooling برای دیتابیس فعال کنید
- ✅ کش Redis را به درستی پیکربندی کنید

### 3. **لاگ‌گذاری**
- ✅ در development: لاگ‌های کامل (DEBUG)
- ✅ در production: فقط WARNING و ERROR
- ✅ از JSON formatter در production استفاده کنید
- ✅ لاگ‌ها را به سیستم‌های متمرکز (مثل ELK) ارسال کنید

### 4. **مقیاس‌پذیری**
- ✅ از Connection Pooling برای دیتابیس استفاده کنید
- ✅ Redis را برای کش و صف پیام استفاده کنید
- ✅ Celery Workers را به صورت جداگانه اجرا کنید
- ✅ از Load Balancer در production استفاده کنید

---

## 🔧 عیب‌یابی مشکلات رایج

### مشکل 1: Import Error برای تنظیمات
**علت**:DJANGO_SETTINGS_MODULE به درستی تنظیم نشده
**راه‌حل**:
```bash
export DJANGO_SETTINGS_MODULE=backend.settings.development
```

### مشکل 2: خطا در خواندن متغیرهای محیطی
**علت**: فایل `.env` وجود ندارد یا فرمت اشتباه است
**راه‌حل**:
```bash
# بررسی وجود فایل
ls -la env/.env.dev

# بررسی محتوا
cat env/.env.dev
```

### مشکل 3: خطا در اتصال به دیتابیس
**علت**: اطلاعات دیتابیس اشتباه است
**راه‌حل**:
```bash
# تست اتصال
psql -h localhost -U printoo24_user -d printoo24_db
```

### مشکل 4: خطا در CORS
**علت**: Origin مجاز نیست
**راه‌حل**: اضافه کردن origin به `CORS_ALLOWED_ORIGINS`

---

## 📚 مستندات مرتبط

- **[مستندات معماری کلی](../00_architecture_overview.md)** - پیش‌نیاز این مستند
- **[مستندات API](./api/README.md)** - بعد از این مستند
- **[مستندات اپلیکیشن‌ها](./apps/README.md)** - بعد از مستندات API

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24