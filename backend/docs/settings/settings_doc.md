<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی تنظیمات پروژه (Settings)</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی تنظیمات پروژه (Settings)</h1>
            <p class="subtitle">بررسی ساختار، پیکربندی‌ها و تنظیمات محیط‌های مختلف در پروژه Printoo24</p>
        </header>
        <main>
            <section id="structure">
                <h2>۱. ساختار کلی تنظیمات</h2>
                <p>
                    تنظیمات پروژه به صورت سلسله مراتبی و بر اساس محیط‌های مختلف طراحی شده است. این رویکرد به توسعه‌دهندگان اجازه می‌دهد تا تنظیمات مشترک را در یک فایل مرکزی تعریف کنند و تنظیمات خاص هر محیط را در فایل‌های جداگانه پیاده‌سازی کنند.
                </p>
                <h3>ساختار فایل‌های تنظیمات</h3>
                <ul>
                    <li><strong><code>base.py</code>: تنظیمات پایه و مشترک</strong><br>
                        تمام تنظیمات اصلی و مشترک بین محیط‌های مختلف در این فایل قرار دارند. این فایل شامل تنظیمات مرتبط با پایگاه داده، اپلیکیشن‌ها، میدلویرها و دیگر پیکربندی‌های عمومی است.</li>
                    <li><strong><code>development.py</code>: تنظیمات محیط توسعه</strong><br>
                        تنظیمات مخصوص محیط توسعه که شامل اتصال به سرویس‌های توسعه، لاگ‌نویسی گسترده و تنظیماتی برای تسهیل فرآیند توسعه است.</li>
                    <li><strong><code>production.py</code>: تنظیمات محیط تولید</strong><br>
                        تنظیمات بهینه‌سازی شده برای محیط تولید که بر امنیت، کارایی و مقیاس‌پذیری تمرکز دارد.</li>
                </ul>
                <h3>الگوی ارث‌بری تنظیمات</h3>
                <p>
                    تنظیمات پروژه از الگوی ارث‌بری پیروی می‌کند. فایل‌های تنظیمات محیطی (development.py و production.py) ابتدا تمام تنظیمات پایه را از طریق دستور <code>from .base import *</code> وارد می‌کنند و سپس تنظیمات خاص خود را اضافه یا بازنویسی می‌کنند.
                </p>
                <pre dir="ltr"><code># مثال از نحوه ارث‌بری در فایل development.py
from .base import *
# تنظیمات خاص محیط توسعه
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": 5432,
    }
}</code></pre>
            </section>
            <section id="environment-variables">
                <h2>۲. متغیرهای محیطی</h2>
                <p>
                    پروژه از کتابخانه <code>django-environ</code> برای مدیریت متغیرهای محیطی استفاده می‌کند. این رویکرد امنیت و انعطاف‌پذیری را در مدیریت تنظیمات حساس افزایش می‌دهد.
                </p>     
                <h3>پیکربندی متغیرهای محیطی</h3>
                <p>
                    در فایل <code>base.py</code>، متغیرهای محیطی به صورت زیر پیکربندی شده‌اند:
                </p>
                <pre dir="ltr"><code>import os
from environ import environ
# ==== Environment Variables ==== #
env = environ.Env(
    DEBUG=(bool, True)
)
env_file = os.path.join(BASE_DIR, 'env\\.env.dev')
environ.Env.read_env(env_file)</code></pre>
                <div class="note-info">
                    <h4>مزایای استفاده از متغیرهای محیطی</h4>
                    <ul>
                        <li><strong>امنیت:</strong> اطلاعات حساس مانند کلمه عبور پایگاه داده و کلیدهای امن در فایل‌های کد ذخیره نمی‌شوند</li>
                        <li><strong>انعطاف‌پذیری:</strong> تغییر محیط بدون نیاز به تغییر در کد اصلی</li>
                        <li><strong>مدیریت چند محیط:</strong> هر محیط (توسعه، تست، تولید) می‌تواند فایل متغیرهای محیطی خاص خود را داشته باشد</li>
                    </ul>
                </div>
            </section>
            <section id="database-config">
                <h2>۳. پیکربندی پایگاه داده</h2>
                <p>
                    پروژه از پایگاه داده PostgreSQL برای ذخیره‌سازی داده‌ها استفاده می‌کند. تنظیمات پایگاه داده در فایل <code>development.py</code> به صورت زیر تعریف شده است:
                </p>
                <pre dir="ltr"><code># ====== Databases (Postgresql) ====== #
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": 5432,
    }
}</code></pre>
                <p>
                    تمام اطلاعات اتصال از طریق متغیرهای محیطی دریافت می‌شوند که این رویکرد امنیت بالایی را فراهم می‌کند.
                </p>
            </section>
            <section id="cache-config">
                <h2>۴. پیکربندی کش</h2>
                <p>
                    برای بهبود عملکرد و کاهش بار پایگاه داده، از Redis به عنوان سیستم کش استفاده می‌شود. تنظیمات کش در فایل <code>development.py</code> به صورت زیر تعریف شده است:
                </p>
                <pre dir="ltr"><code># ====== Cache (Redis Settings) ====== #
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}</code></pre>
                <p>
                    استفاده از Django-Redis به عنوان backend کش، امکان استفاده از Redis را با API یکسان Django فراهم می‌کند.
                </p>
            </section>
            <section id="celery-config">
                <h2>۵. پیکربندی Celery</h2>
                <p>
                    برای اجرای وظایف ناهمزمان (Asynchronous Tasks) از Celery استفاده می‌شود که با Redis به عنوان broker ارتباط دارد.
                </p>
                <pre dir="ltr"><code># ====== Celery Settings ====== #
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"</code></pre>
                <p>
                    این تنظیمات Celery را برای استفاده از Redis به عنوان broker و backend نتایج پیکربندی می‌کند و فرمت JSON را برای سریالایز کردن داده‌ها مشخص می‌کند.
                </p>
            </section>
            <section id="email-config">
                <h2>۶. پیکربندی ایمیل</h2>
                <p>
                    سیستم ایمیل برای ارسال اعلان‌ها و تأییدیه‌ها به کاربران استفاده می‌شود. تنظیمات ایمیل به صورت انعطاف‌پذیر از طریق متغیرهای محیطی قابل پیکربندی است:
                </p>
                <pre dir="ltr"><code># ====== Email Settings ====== #
EMAIL_BACKEND = env("EMAIL_BACKEND", default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env("EMAIL_HOST", default='smtp.gmail.com')
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="amingholami06@gmail.com")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="oojt ugkq exew ofbs")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)</code></pre>
                <p>
                    این تنظیمات به طور پیش‌فرض برای استفاده از Gmail پیکربندی شده‌اند اما قابلیت تغییر برای استفاده از هر سرویس ایمیل دیگری را دارند.
                </p>
            </section> 
            <section id="logging-config">
                <h2>۷. پیکربندی لاگ‌نویسی</h2>
                <p>
                    سیستم لاگ‌نویسی پیشرفته برای ثبت وقایع و خطاهای سیستم طراحی شده است. این سیستم به صورت متمرکز و با تفکیک بخش‌های مختلف پروژه پیکربندی شده است.
                </p>
                <h3>تنظیمات عمومی لاگ‌نویسی</h3>
                <pre dir="ltr"><code>LOGGING = {
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
    # ...</code></pre>
                <h3>تعریف handlerها برای بخش‌های مختلف</h3>
                <p>
                    برای هر بخش از سیستم handlerهای مجزایی تعریف شده‌اند که امکان لاگ‌نویسی مجزا را فراهم می‌کنند:
                </p>
                <ul>
                    <li><strong>Accounts Handlers:</strong> برای خدمات مربوط به حساب کاربری</li>
                    <li><strong>Shop Handlers:</strong> برای خدمات فروشگاه</li>
                    <li><strong>Console Handler:</strong> برای نمایش لاگ‌ها در کنسول</li>
                </ul>
                <pre dir="ltr"><code>'handlers': {
    # ====== Accounts Handlers ====== #
    'accounts_auth_file': {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': 'logs/accounts/auth_service.log',
        'maxBytes': 1024 * 1024 * 15,  # 15 MB
        'backupCount': 10,
        'formatter': 'verbose',
    },
    # سایر handlerها...

    # ====== Console Handler ====== #
    'console': {
        'level': 'INFO',
        'class': 'logging.StreamHandler',
        'formatter': 'simple',
    },
},</code></pre>                
                <h3>تعریف loggerها</h3>
                <p>
                    loggerهای مختلف برای بخش‌های مختلف سیستم تعریف شده‌اند که هر کدام به handlerهای مربوطه متصل شده‌اند:
                </p> 
                <pre dir="ltr"><code>'loggers': {
    # ====== Accounts Loggers ====== #
    'accounts.services.auth': {
        'handlers': ['accounts_auth_file', 'console'],
        'level': 'DEBUG',
        'propagate': False,
    },
    # سایر loggerها...
}</code></pre>
                <div class="note">
                    <h4>نکات مهم در لاگ‌نویسی</h4>
                    <ul>
                        <li><strong>استفاده از RotatingFileHandler:</strong> جلوگیری از بزرگ شدن بیش از حد فایل‌های لاگ</li>
                        <li><strong>تخصیص مجزا برای هر سرویس:</strong> امکان ردیابی خطاهای خاص هر بخش</li>
                        <li><strong>سطح لاگ‌نویسی مناسب:</strong> استفاده از سطوح DEBUG و INFO برای توسعه و WARNING برای امنیت</li>
                    </ul>
                </div>
            </section>
            <section id="security-config">
                <h2>۸. پیکربندی امنیتی</h2>
                <p>
                    تنظیمات امنیتی در فایل‌های تنظیمات به دقت پیکربندی شده‌اند تا امنیت بالایی برای سیستم فراهم کنند.
                </p>
                <h3>پیکربندی JWT</h3>
                <p>
                    از JWT (JSON Web Token) برای احراز هویت کاربران استفاده می‌شود:
                </p>
                <pre dir="ltr"><code># ======= Simple JWT ======= #
SIMPLEJWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
}</code></pre>
                <h3>اعتبارسنجی کلمه عبور</h3>
                <p>
                    سیستم اعتبارسنجی کلمه عبور برای افزایش امنیت حساب‌های کاربری:
                </p>  
                <pre dir="ltr"><code>AUTH_PASSWORD_VALIDATORS = [
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
]</code></pre>
                <div class="note-info">
                    <h4>نقاط قوت پیکربندی امنیتی</h4>
                    <ul>
                        <li><strong>JWT با عمر محدود:</strong> توکن‌های دسترسی با عمر کوتاه برای افزایش امنیت</li>
                        <li><strong>اعتبارسنجی چندمرحله‌ای کلمه عبور:</strong> جلوگیری از استفاده از کلمه عبورهای ضعیف</li>
                        <li><strong>بلک‌لیست کردن توکن‌ها:</strong> امکان لغو توکن‌های فعال در صورت نیاز</li>
                    </ul>
                </div>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>