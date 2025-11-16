<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی Tasks اپلیکیشن Accounts</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی Tasks اپلیکیشن Accounts</h1>
            <p class="subtitle">بررسی جامع وظایف ناهمزمان (Celery Tasks) مربوط به ارسال ایمیل در اپلیکیشن حساب کاربری</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    اپلیکیشن <code>accounts</code> از وظایف ناهمزمان (Celery Tasks) برای ارسال ایمیل‌های تأیید حساب کاربری و بازنشانی رمز عبور استفاده می‌کند. این رویکرد باعث می‌شود که عملیات ارسال ایمیل به صورت ناهمزمان انجام شده و عملکرد اصلی سیستم تحت تأثیر قرار نگیرد.
                </p>
                <div class="note-info">
                    <h4>مزایای استفاده از وظایف ناهمزمان</h4>
                    <ul>
                        <li><strong>افزایش عملکرد:</strong> کاربران فوراً پاسخ دریافت می‌کنند و نیازی به منتظر ماندن برای ارسال ایمیل نیست</li>
                        <li><strong>مدیریت خطا:</strong> قابلیت تلاش مجدد خودکار در صورت بروز خطا</li>
                        <li><strong>مقیاس‌پذیری:</strong> امکان اجرای همزمان چندین وظیفه</li>
                    </ul>
                </div>
            </section>
            <section id="location">
                <h2>۲. مسیر فایل</h2>
                <p>
                    فایل حاوی وظایف ناهمزمان اپلیکیشن accounts در مسیر زیر قرار دارد:
                </p>
                <pre dir="ltr"><code>services/customer_site/apps/accounts/tasks/emails.py</code></pre>
                <p>
                    این فایل شامل دو وظیفه اصلی برای ارسال ایمیل‌های تأیید حساب کاربری و بازنشانی رمز عبور است.
                </p>
            </section>
            <section id="celery-integration">
                <h2>۳. یکپارچه‌سازی با Celery</h2>
                <p>
                    پروژه Printoo24 از Celery به عنوان سیستم صف وظایف ناهمزمان استفاده می‌کند. تنظیمات Celery در فایل <code>customer_site/customer_site/celery.py</code> انجام شده است:
                </p>
                <pre dir="ltr"><code>import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_site.settings.development')

app = Celery('customer_site')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()</code></pre>
                <h3>نحوه کشف خودکار وظایف</h3>
                <p>
                    با فراخوانی <code>app.autodiscover_tasks()</code>، Celery به طور خودکار وظایف تعریف شده در فایل‌های <code>tasks.py</code> تمام اپلیکیشن‌ها را کشف می‌کند.
                </p>
                <h3>پیکربندی از طریق تنظیمات Django</h3>
                <p>
                    تنظیمات مربوط به Celery در فایل تنظیمات توسعه (<code>development.py</code>) به صورت زیر تعریف شده است:
                </p>
                <pre dir="ltr"><code>CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"</code></pre>
            </section>
            <section id="tasks-details">
                <h2>۴. بررسی وظایف تعریف شده</h2>
                <h3><code>send_verification_email_task</code></h3>
                <p>
                    این وظیفه مسئول ارسال ایمیل تأیید حساب کاربری به کاربران جدید است.
                </p>
                <pre dir="ltr"><code>@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_verification_email_task(user_email: str, verification_code: str):
    """یک تسک برای ارسال ایمیل فعال سازی برای کاربر"""</code></pre>
                <h4>پارامترها</h4>
                <ul>
                    <li><strong><code>user_email</code>:</strong> آدرس ایمیل کاربری که قرار است ایمیل تأیید برایش ارسال شود</li>
                    <li><strong><code>verification_code</code>:</strong> کد تأیید ۶ رقمی که باید در ایمیل ارسال شود</li>
                </ul>
                <h4>ویژگی‌های کلیدی</h4>
                <ul>
                    <li><strong>تلاش مجدد خودکار:</strong> در صورت بروز خطا، وظیفه حداکثر ۳ بار با فاصله ۵ ثانیه‌ای تلاش مجدد می‌کند</li>
                    <li><strong>لاگ‌نویسی:</strong> عملیات ارسال ایمیل به همراه لاگ‌های مناسب ثبت می‌شود</li>
                </ul>
                <h3><code>send_password_reset_email_task</code></h3>
                <p>
                    این وظیفه مسئول ارسال ایمیل بازنشانی رمز عبور به کاربران است.
                </p>
                <pre dir="ltr"><code>@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_password_reset_email_task(user_email:str, reset_link: str):
    """ارسال ایمیل بازنشانی رمز عبور به کاربر"""</code></pre>
                <h4>پارامترها</h4>
                <ul>
                    <li><strong><code>user_email</code>:</strong> آدرس ایمیل کاربری که قرار است ایمیل بازنشانی رمز عبور برایش ارسال شود</li>
                    <li><strong><code>reset_link</code>:</strong> لینک یک‌بار مصرف برای بازنشانی رمز عبور</li>
                </ul>
                <h4>ویژگی‌های کلیدی</h4>
                <ul>
                    <li><strong>تلاش مجدد خودکار:</strong> در صورت بروز خطا، وظیفه حداکثر ۳ بار با فاصله ۵ ثانیه‌ای تلاش مجدد می‌کند</li>
                    <li><strong>امنیت:</strong> استفاده از لینک یک‌بار مصرف و محدودیت زمانی</li>
                </ul>
            </section>
            <section id="usage">
                <h2>۵. نحوه استفاده از وظایف</h2>
                <p>
                    وظایف تعریف شده از طریق فراخوانی متد <code>delay()</code> یا <code>apply_async()</code> اجرا می‌شوند:
                </p>
                <h3>در سرویس تأیید حساب کاربری</h3>
                <pre dir="ltr"><code># در فایل services/accounts/services/verify_service.py
logger.debug(f"Triggering verification email task for: {email}")
send_verification_email_task.delay(email, code)</code></pre>
                <h3>در سرویس بازنشانی رمز عبور</h3>
                <pre dir="ltr"><code># در فایل services/accounts/services/password_reset_service.py
logger.debug(f"Triggering email task for password reset - Email: {email}")
send_password_reset_email_task.delay(user_email=email, reset_link=reset_link)</code></pre>
                <p>
                    با این روش، وظایف به صورت ناهمزمان در صف قرار گرفته و توسط workerهای Celery اجرا می‌شوند.
                </p>
            </section>
            <section id="email-service">
                <h2>۶. سرویس ایمیل مشترک</h2>
                <p>
                    وظایف تعریف شده از سرویس ایمیل مشترک (<code>EmailService</code>) برای ارسال ایمیل‌ها استفاده می‌کنند:
                </p>  
                <pre dir="ltr"><code>from core.common.email.email_service import EmailService

email_service = EmailService()
email_service._send_email(
    subject="عنوان ایمیل",
    template_name="مسیر/قالب.html",
    context={"داده‌های مورد نیاز قالب"},
    from_email=settings.EMAIL_HOST_USER,
    to_email=user_email
)</code></pre>
                <p>
                    این سرویس از تنظیمات ایمیل تعریف شده در فایل تنظیمات استفاده می‌کند و امکان ارسال ایمیل با قالب‌های HTML را فراهم می‌کند.
                </p>
            </section>
            <section id="execution">
                <h2>۷. نحوه اجرای وظایف</h2>
                <p>
                    برای اجرای وظایف Celery، باید workerهای Celery را اجرا کنید:
                </p>
                <pre dir="ltr"><code># اجرای worker
celery -A customer_site worker -l info</code></pre>
                <p>
                    در محیط تولید، اجرای workerها بهتر است از طریق Docker یا سرویس‌های مدیریت فرآیند مانند systemd انجام شود.
                </p>
                <div class="note">
                    <h4>نکته مهم</h4>
                    <p>
                        برای اجرای صحیح وظایف، اطمینان حاصل کنید که Redis (به عنوان broker و backend) در حال اجرا است و تنظیمات مربوط به اتصال به آن در فایل تنظیمات پروژه به درستی انجام شده است.
                    </p>
                </div>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>