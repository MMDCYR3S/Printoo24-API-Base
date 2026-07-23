<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی پیکربندی Celery</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی پیکربندی Celery</h1>
            <p class="subtitle">بررسی ساختار و پیکربندی سیستم صف وظایف ناهمزمان (Task Queue) در پروژه Printoo24</p>
        </header>
        <main>
            <section id="celery-overview">
                <h2>۱. مرور کلی بر Celery</h2>
                <p>
                    Celery یک سیستم صف وظایف ناهمزمان (Distributed Task Queue) قدرتمند برای زبان برنامه‌نویسی پایتون است. در پروژه Printoo24 از Celery برای اجرای وظایف سنگین یا زمان‌بر به صورت ناهمزمان استفاده می‌شود تا عملکرد اصلی سیستم تحت تأثیر قرار نگیرد.
                </p>
                <h3>کاربردهای Celery در پروژه</h3>
                <ul>
                    <li><strong>ارسال ایمیل‌های تأیید و اعلان:</strong> جلوگیری از تأخیر در پاسخ به کاربران هنگام ارسال ایمیل</li>
                    <li><strong>پردازش فایل‌های سنگین:</strong> تبدیل فرمت‌ها، تغییر اندازه تصاویر و غیره</li>
                    <li><strong>پردازش‌های پس‌زمینه:</strong> به‌روزرسانی آمار، پاک‌سازی فایل‌های موقت و غیره</li>
                </ul>
                <div class="note-info">
                    <h4>مزایای استفاده از Celery</h4>
                    <ul>
                        <li><strong>افزایش عملکرد:</strong> وظایف زمان‌بر به صورت ناهمزمان اجرا می‌شوند</li>
                        <li><strong>مقیاس‌پذیری:</strong> امکان اجرای همزمان چندین وظیفه</li>
                        <li><strong>مدیریت خطا:</strong> قابلیت تلاش مجدد در صورت بروز خطا</li>
                    </ul>
                </div>
            </section>
            <section id="celery-architecture">
                <h2>۲. معماری Celery در پروژه</h2>
                <p>
                    معماری Celery در پروژه Printoo24 از سه جزء اصلی تشکیل شده است:
                </p>
                <ul>
                    <li><strong>Celery Client (Producer):</strong> بخشی از اپلیکیشن Django که وظایف را تولید و به صف ارسال می‌کند</li>
                    <li><strong>Message Broker (Redis):</strong> سیستمی برای مدیریت صف وظایف (در این پروژه از Redis استفاده می‌شود)</li>
                    <li><strong>Celery Workers:</strong> فرآیندهایی که وظایف را از صف دریافت و اجرا می‌کنند</li>
                </ul>
                <h3>بررسی جزئیات پیکربندی</h3>
                <p>
                    تنظیمات Celery در فایل <code>development.py</code> به صورت زیر تعریف شده است:
                </p>
                <pre dir="ltr"><code># ====== Celery Settings ====== #
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"</code></pre>
                <p>
                    در این پیکربندی، Redis هم به عنوان Message Broker و هم به عنوان Result Backend استفاده می‌شود.
                </p>
            </section>
            <section id="celery-app-configuration">
                <h2>۳. پیکربندی اصلی Celery App</h2>
                <p>
                    پیکربندی اصلی Celery در فایل <code>celery.py</code> در مسیر <code>customer_site/customer_site/</code> انجام شده است:
                </p>
                <pre dir="ltr"><code>import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_site.settings.development')

app = Celery('customer_site')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """ تسک برای نمایش تمامی درخواست هایی که ارسال میشه """
    print(f"Request: {self.request!r}")</code></pre>
                <h3>تحلیل خط به خط</h3>
                <ul>
                    <li><strong><code>os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_site.settings.development')</code>:</strong> تنظیم محیط Django برای اجرای Celery</li>
                    <li><strong><code>app = Celery('customer_site')</code>:</strong> ایجاد نمونه اصلی Celery با نام پروژه</li>
                    <li><strong><code>app.config_from_object("django.conf:settings", namespace="CELERY")</code>:</strong> بارگذاری تنظیمات Celery از فایل تنظیمات Django</li>
                    <li><strong><code>app.autodiscover_tasks()</code>:</strong> کشف خودکار وظایف تعریف شده در اپلیکیشن‌ها</li>
                    <li><strong><code>@app.task(bind=True, ignore_result=True)</code>:</strong> تعریف یک وظیفه نمونه برای اهداف دیباگ</li>
                </ul>
            </section>
            <section id="installed-apps">
                <h2>۴. اپلیکیشن‌های مرتبط با Celery</h2>
                <p>
                    در فایل تنظیمات پایه پروژه (<code>base.py</code>)، اپلیکیشن‌های مرتبط با Celery به شرح زیر در بخش <code>INSTALLED_APPS</code> تعریف شده‌اند:
                </p>
                <pre dir="ltr"><code># ==== 3rd party apps ==== #
"django_celery_beat",
"django_celery_results",</code></pre>
                <h3>بررسی اپلیکیشن‌ها</h3>
                <ul>
                    <li><strong><code>django_celery_beat</code>:</strong> ارائه سیستم زمان‌بندی وظایف (Periodic Tasks) در محیط Django Admin</li>
                    <li><strong><code>django_celery_results</code>:</strong> ذخیره نتایج وظایف در پایگاه داده به جای حافظه</li>
                </ul>
                <p>
                    worth noting that the main <code>celery</code> app is commented out in the installed apps, which is correct as we configure Celery directly in our project.
                </p>
            </section>
            <section id="task-creation">
                <h2>۵. نحوه تعریف وظایف (Tasks)</h2>
                <p>
                    وظایف Celery را می‌توان در هر جایی از پروژه تعریف کرد، اما بهتر است در بخش‌های مرتبط با منطق تجاری قرار داده شوند. برای تعریف یک وظیفه جدید کافی است از دکوراتور <code>@shared_task</code> یا <code>@app.task</code> استفاده کنید.
                </p>
                <h3>مثال از تعریف یک وظیفه</h3>
                <pre dir="ltr"><code>from celery import shared_task

@shared_task
def send_notification_email(user_id, message):
    # منطق ارسال ایمیل
    pass</code></pre>
                
                <h3>نحوه فراخوانی وظایف</h3>
                <p>
                    برای فراخوانی یک وظیفه در کد، می‌توانید از روش‌های مختلفی استفاده کنید:
                </p>
                
                <pre dir="ltr"><code># اجرای فوری وظیفه
send_notification_email.delay(user_id, message)

# اجرای وظیفه با تنظیمات خاص
send_notification_email.apply_async(
    args=[user_id, message],
    countdown=60  # اجرای وظیفه بعد از 60 ثانیه
)</code></pre>
                <div class="note">
                    <h4>نکات مهم در تعریف وظایف</h4>
                    <ul>
                        <li><strong>عدم استفاده از اشیاء غیرقابل سریالایز:</strong> از ارسال اشیاء Django Model به عنوان پارامتر خودداری کنید</li>
                        <li><strong>استفاده از شناسه‌ها:</strong> بهتر است شناسه‌های اشیاء را ارسال کرده و در وظیفه آن‌ها را بازیابی کنید</li>
                        <li><strong>مدیریت خطا:</strong> استفاده از بلوک try-except در داخل وظایف برای مدیریت خطاها</li>
                    </ul>
                </div>
            </section>
            <section id="celery-execution">
                <h2>۶. نحوه اجرای Celery</h2>
                <p>
                    برای اجرای Celery Worker در محیط توسعه، دستور زیر را در ترمینال اجرا کنید:
                </p>
                <pre dir="ltr"><code>celery -A customer_site worker -l info</code></pre>
                <p>
                    برای اجرای زمان‌بند وظایف (در صورت استفاده از وظایف دوره‌ای):
                </p>
                <pre dir="ltr"><code>celery -A customer_site beat -l info</code></pre>
                <h3>پیکربندی Docker</h3>
                <p>
                    در محیط تولید، اجرای Celery Worker و Beat بهتر است از طریق Docker انجام شود. یک نمونه پیکربندی در فایل docker-compose.yml باید شامل سرویس‌های زیر باشد:
                </p>
                <pre dir="ltr"><code>services:
  celery_worker:
    # پیکربندی سرویس Worker
    command: celery -A customer_site worker -l info
    
  celery_beat:
    # پیکربندی سرویس زمان‌بند
    command: celery -A customer_site beat -l info</code></pre>
            </section>
            <section id="monitoring">
                <h2>۷. مانیتورینگ وظایف</h2>
                <p>
                    برای مانیتورینگ وظایف Celery در محیط توسعه می‌توانید از دستور زیر استفاده کنید:
                </p>
                <pre dir="ltr"><code>celery -A customer_site events</code></pre>
                <p>
                    همچنین می‌توانید از ابزارهایی مانند Flower برای مانیتورینگ گرافیکی استفاده کنید:
                </p>
                <pre dir="ltr"><code>celery -A customer_site flower</code></pre>
                <div class="note-info">
                    <h4>اطلاعات ذخیره شده در Result Backend</h4>
                    <ul>
                        <li><strong>وضعیت وظایف:</strong> موفق، ناموفق، در حال اجرا و غیره</li>
                        <li><strong>نتایج وظایف:</strong> خروجی وظایف که می‌توانند ذخیره شوند</li>
                        <li><strong>زمان اجرا:</strong> آمار زمان اجرای وظایف برای بهینه‌سازی</li>
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