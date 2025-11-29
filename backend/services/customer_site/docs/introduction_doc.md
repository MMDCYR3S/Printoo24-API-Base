<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی ساختار پروژه Customer Site</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی ساختار پروژه Customer Site</h1>
            <p class="subtitle">بررسی جامع ساختار، اجزا و نحوه کارکرد پروژه Customer Site در پروژه Printoo24</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    پروژه <code>customer_site</code> یکی از دو پروژه اصلی در مجموعه Printoo24 است که مسئول ارائه خدمات به مشتریان نهایی می‌باشد. این پروژه شامل تمامی امکانات مورد نیاز کاربران برای خرید محصولات، مدیریت حساب کاربری و سایر فعالیت‌های مرتبط با فروشگاه است.
                </p>
                <div class="note-info">
                    <h4>ویژگی‌های کلیدی پروژه</h4>
                    <ul>
                        <li><strong>معماری چند لایه:</strong> تقسیم‌بندی مناسب بین API، اپلیکیشن‌ها و تنظیمات</li>
                        <li><strong>قابلیت گسترش:</strong> ساختار مناسب برای افزودن اپلیکیشن‌های جدید</li>
                        <li><strong>توسعه موازی:</strong> امکان توسعه همزمان چندین اپلیکیشن</li>
                        <li><strong>یکپارچگی:</strong> استفاده از اپلیکیشن مشترک برای مدل‌های داده</li>
                    </ul>
                </div>
            </section>
            <section id="structure">
                <h2>۲. ساختار پوشه‌بندی</h2>
                <p>
                    پروژه <code>customer_site</code> دارای ساختار سلسله‌مراتبی و منظمی است که هر بخش مسئولیت خاصی را بر عهده دارد:
                </p>
                <pre dir="ltr"><code>.
├── api
│   ├── v1
│   │   ├── authentication
│   │   ├── shop
│   │   └── urls.py
│   └── urls.py
├── apps
│   ├── accounts
│   ├── cart
│   ├── notification
│   ├── order
│   ├── shop
│   └── userprofile
├── customer_site
│   ├── settings
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── dockerfiles
├── docs
└── manage.py</code></pre>
                <h3>بررسی هر پوشه و فایل</h3>
                <h4><code>api</code></h4>
                <p>
                    این پوشه شامل تمامی APIهای پروژه است که به صورت نسخه‌بندی شده سازماندهی شده‌اند. هر نسخه API شامل اپلیکیشن‌های مختلف با serializers و views مربوطه است.
                </p>
                <ul>
                    <li><strong><code>v1/authentication</code>:</strong> APIهای مربوط به احراز هویت کاربران</li>
                    <li><strong><code>v1/shop</code>:</strong> APIهای مربوط به فروشگاه و محصولات</li>
                </ul>
                <h4><code>apps</code></h4>
                <p>
                    پوشه اصلی حاوی اپلیکیشن‌های Django است. هر اپلیکیشن مسئول یک بخش خاص از عملکرد پروژه است:
                </p>
                <ul>
                    <li><strong><code>accounts</code>:</strong> مدیریت حساب کاربری، ثبت‌نام، ورود و احراز هویت</li>
                    <li><strong><code>cart</code>:</strong> مدیریت سبد خرید کاربران</li>
                    <li><strong><code>notification</code>:</strong> سیستم اعلان‌ها و پیام‌ها</li>
                    <li><strong><code>order</code>:</strong> مدیریت سفارشات کاربران</li>
                    <li><strong><code>shop</code>:</strong> منطق تجاری مربوط به فروشگاه و محصولات</li>
                    <li><strong><code>userprofile</code>:</strong> مدیریت پروفایل و اطلاعات کاربران</li>
                </ul>
                <h4><code>customer_site</code></h4>
                <p>
                    پوشه اصلی پروژه Django که شامل تنظیمات، فایل‌های پیکربندی و تنظیمات مربوط به deployment است:
                </p>
                <ul>
                    <li><strong><code>settings</code>:</strong> تنظیمات مختلف محیط‌های توسعه و تولید</li>
                    <li><strong><code>celery.py</code>:</strong> پیکربندی Celery برای وظایف ناهمزمان</li>
                    <li><strong><code>urls.py</code>:</strong> مسیریابی اصلی پروژه</li>
                </ul>
                <h4><code>dockerfiles</code></h4>
                <p>
                    شامل Dockerfileهای مورد نیاز برای اجرای پروژه در محیط‌های مختلف.
                </p>
                <h4><code>docs</code></h4>
                <p>
                    شامل مستندات فنی پروژه که به توسعه‌دهندگان کمک می‌کند تا با ساختار و عملکرد پروژه آشنا شوند.
                </p>
                <h4><code>manage.py</code></h4>
                <p>
                    ابزار خط فرمان Django برای مدیریت پروژه.
                </p>
            </section>
            <section id="apps-details">
                <h2>۳. بررسی اپلیکیشن‌ها</h2>
                <h3><code>accounts</code></h3>
                <p>
                    اپلیکیشن مسئول مدیریت تمام فرآیندهای مرتبط با حساب کاربری:
                </p>
                <ul>
                    <li>ثبت‌نام و ورود کاربران</li>
                    <li>تأیید هویت از طریق ایمیل</li>
                    <li>بازنشانی رمز عبور</li>
                    <li>مدیریت توکن‌های JWT</li>
                    <li>وظایف ناهمزمان برای ارسال ایمیل</li>
                </ul>
                <h3><code>shop</code></h3>
                <p>
                    اپلیکیشن مسئول عملیات فروشگاه:
                </p>
                <ul>
                    <li>نمایش لیست و جزئیات محصولات</li>
                    <li>فیلتر کردن محصولات</li>
                    <li>محاسبه قیمت نهایی بر اساس ویژگی‌های انتخابی</li>
                    <li>مدیریت ویژگی‌های محصولات (سایز، جنس، آپشن)</li>
                </ul>
                <h3>سایر اپلیکیشن‌ها</h3>
                <ul>
                    <li><strong><code>cart</code>:</strong> مدیریت سبد خرید کاربران</li>
                    <li><strong><code>notification</code>:</strong> سیستم اعلان‌ها و پیام‌ها</li>
                    <li><strong><code>order</code>:</strong> مدیریت سفارشات کاربران</li>
                    <li><strong><code>userprofile</code>:</strong> مدیریت پروفایل و اطلاعات کاربران</li>
                </ul>
            </section>
            <section id="api-structure">
                <h2>۴. ساختار API</h2>
                <p>
                    APIها به صورت نسخه‌بندی شده و سازماندهی شده‌اند:
                </p>
                <pre dir="ltr"><code>api/
├── v1/
│   ├── authentication/
│   │   ├── serializers/
│   │   ├── views/
│   │   └── urls.py
│   ├── shop/
│   │   ├── serializers/
│   │   ├── views/
│   │   └── urls.py
│   └── urls.py
└── urls.py</code></pre>
                <h3>ویژگی‌های ساختار API</h3>
                <ul>
                    <li><strong>نسخه‌بندی:</strong> امکان توسعه نسخه‌های مختلف API بدون تأثیر بر نسخه‌های قبلی</li>
                    <li><strong>تقسیم‌بندی بر اساس عملکرد:</strong> هر بخش API مسئولیت خاصی را بر عهده دارد</li>
                    <li><strong>سازماندهی مناسب:</strong> جدا کردن serializers و views در پوشه‌های مجزا</li>
                </ul>
            </section>
            <section id="settings">
                <h2>۵. تنظیمات پروژه</h2>
                <p>
                    تنظیمات پروژه در پوشه <code>customer_site/settings</code> قرار دارند و به صورت محیطی (توسعه، تولید) سازماندهی شده‌اند:
                </p>
                <ul>
                    <li><strong><code>base.py</code>:</strong> تنظیمات پایه مشترک بین تمام محیط‌ها</li>
                    <li><strong><code>development.py</code>:</strong> تنظیمات خاص محیط توسعه</li>
                    <li><strong><code>production.py</code>:</strong> تنظیمات خاص محیط تولید</li>
                </ul>
                <p>
                    این ساختار امکان استفاده از تنظیمات متفاوت برای هر محیط را فراهم می‌کند.
                </p>
            </section>
            <section id="integration">
                <h2>۶. یکپارچه‌سازی با اپلیکیشن مشترک</h2>
                <p>
                    پروژه <code>customer_site</code> از اپلیکیشن مشترک <code>core</code> برای دسترسی به مدل‌های داده استفاده می‌کند:
                </p>
                <pre dir="ltr"><code># در فایل تنظیمات
INSTALLED_APPS = [
    # ... سایر اپلیکیشن‌ها ...
    "core",  # اپلیکیشن مشترک
    "apps.accounts",
    "apps.shop",
    # ... سایر اپلیکیشن‌های محلی ...
]</code></pre>
                <p>
                    این رویکرد اطمینان می‌دهد که مدل‌های داده در تمام پروژه‌های مرتبط یکسان باشند.
                </p>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>