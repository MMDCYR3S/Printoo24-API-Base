<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحلیل معماری کتابخانه مشترک (shared_libs)</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>تحلیل معماری کتابخانه مشترک (`shared_libs`)</h1>
            <p class="subtitle">بررسی ساختار، نحوه نصب و چالش‌های یکپارچه‌سازی در محیط Docker</p>
        </header>
        <main>
            <section id="structure">
                <h2>۱. تحلیل ساختار پوشه‌بندی</h2>
                <p>
                    پوشه <code>shared_libs</code> به عنوان یک کتابخانه مرکزی (Central Library) طراحی شده است که منطق تجاری و مدل‌های داده مشترک بین تمام سرویس‌های پروژه (مانند <code>admin_site</code> و <code>customer_site</code>) را در خود جای می‌دهد. این رویکرد از تکرار کد (Code Duplication) جلوگیری کرده و نگهداری پروژه را ساده‌تر می‌کند.
                </p>
                <h3>ساختار لایه‌ای اپلیکیشن `core`</h3>
                <p>
                    معماری داخلی اپلیکیشن <code>core</code> از الگوهای طراحی استاندارد برای تفکیک مسئولیت‌ها (Separation of Concerns) پیروی می‌کند:
                </p>
                <ul>
                    <li><strong><code>core/models/</code>: لایه داده (Data Layer)</strong><br>
                        این بخش شامل تمام مدل‌های جنگو است که ساختار پایگاه داده را تعریف می‌کنند. مدل‌های کلیدی مانند <code>User</code>، <code>Product</code>، <code>Order</code> و <code>Cart</code> در این لایه قرار دارند.</li>
                    <li><strong><code>core/common/</code>: لایه منطق تجاری (Business Logic Layer)</strong><br>
                        این پوشه، مغز متفکر کتابخانه است و خود به زیرشاخه‌هایی تقسیم می‌شود که منطق دسترسی به داده و قوانین کسب‌وکار را از هم جدا می‌کنند.</li>
                    <li><strong><code>core/migrations/</code>:</strong> این پوشه، تاریخچه تغییرات مدل‌های داده را برای اعمال در پایگاه داده نگهداری می‌کند.</li>
                    <li><strong><code>core/signals.py</code>: لایه رویداد-محور (Event-Driven Layer)</strong><br>
                        این فایل مسئولیت اجرای خودکار فرآیندها در پاسخ به رویدادهای خاص پایگاه داده را بر عهده دارد.</li>
                </ul>
                <h3 id="signals-py">فایل `signals.py`: خودکارسازی فرآیندهای مبتنی بر رویداد</h3>
                <p>
                    یکی از قابلیت‌های قدرتمند جنگو، سیستم <strong>سیگنال‌ها (Signals)</strong> است که به بخش‌های مختلف برنامه اجازه می‌دهد تا بدون ارتباط مستقیم با یکدیگر، به رویدادها واکنش نشان دهند. فایل `signals.py` در این پروژه از این قابلیت برای خودکارسازی فرآیندهای حیاتی پس از ایجاد یک کاربر جدید استفاده می‌کند.
                </p>
                <pre dir="ltr"><code>from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CustomerProfile, Wallet, Cart
@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)
</code></pre>
                <h4>تحلیل عملکرد سیگنال‌ها</h4>
                <ul>
                    <li><strong>`@receiver(post_save, sender=User)`:</strong> این دکوراتور (Decorator) به جنگو اعلام می‌کند که تابع زیرین باید به عنوان یک "شنونده" (Listener) برای سیگنال `post_save` ثبت شود. این سیگنال دقیقاً <strong class="highlight">بعد از</strong> اینکه یک نمونه از مدل `User` در پایگاه داده ذخیره شد، ارسال می‌شود.</li>
                    <li><strong>`if created:`:</strong> این شرط بسیار کلیدی است. پارامتر `created` یک مقدار بولین است که اگر آبجکت برای اولین بار ایجاد شده باشد `True` و در غیر این صورت (یعنی در حالت به‌روزرسانی یا update) `False` خواهد بود. این شرط تضمین می‌کند که کیف پول، سبد خرید و پروفایل <strong class="highlight">فقط و فقط یک بار</strong> در زمان ثبت‌نام کاربر ایجاد شوند.</li>
                </ul>
                <div class="note-info">
                    <h4>مزایای معماری استفاده از سیگنال‌ها</h4>
                    <p>استفاده از سیگنال‌ها در این سناریو، مزایای معماری مهمی را به همراه دارد:</p>
                    <ul>
                        <li><strong>یکپارچگی داده (Data Integrity):</strong> تضمین می‌کند که هر کاربر جدید به صورت اتمی و خودکار، تمام موجودیت‌های وابسته (پروفایل، کیف پول، سبد خرید) را دریافت می‌کند. این کار از ایجاد کاربر "ناقص" در سیستم جلوگیری می‌کند.</li>
                        <li><strong>جداسازی مسئولیت‌ها (Decoupling):</strong> منطق ایجاد کاربر (که ممکن است در `UserService` یا `views` باشد) نیازی به دانستن این موضوع ندارد که باید پروفایل یا کیف پول هم ایجاد کند. این مسئولیت‌ها به طور کامل از هم جدا شده‌اند که باعث تمیزتر شدن کد و نگهداری آسان‌تر آن می‌شود.</li>
                        <li><strong>توسعه‌پذیری (Extensibility):</strong> اگر در آینده تصمیم بگیریم که با ایجاد هر کاربر، یک فرآیند دیگر (مثلاً ارسال ایمیل خوش‌آمدگویی یا ثبت لاگ) نیز انجام شود، کافی است یک تابع شنونده جدید در `signals.py` اضافه کنیم، بدون اینکه نیازی به دستکاری کدهای مربوط به ایجاد کاربر باشد.</li>
                    </ul>
                </div>
            </section>
            <section id="setup-py">
                <h2>۲. نقش کلیدی فایل `setup.py`</h2>
                <p>
                    فایل <code>setup.py</code> قلب تپنده این معماری است. این فایل با استفاده از ابزار <code>setuptools</code> پایتون، پوشه <code>core</code> را به یک <strong class="highlight">پکیج قابل نصب</strong> تبدیل می‌کند.
                </p>
                <pre dir="ltr"><code>from setuptools import setup, find_packages
setup(
    name="printoo24-core",
    version="0.1.0",
    packages=find_packages(),
    description="Shared models, servieces and utilities for Printoo24 project.",
    author="Mohammad Amin Gholami",
    author_email="amingholami06@gmail.com",
)</code></pre>
                <p>مزایای این رویکرد عبارتند از:</p>
                <ul>
                    <li><strong>قابلیت استفاده مجدد (Reusability):</strong> سرویس‌های مختلف می‌توانند این پکیج را مانند هر کتابخانه دیگری (مثل Django یا Requests) نصب و استفاده کنند.</li>
                    <li><strong>مدیریت نسخه (Versioning):</strong> با تعیین نسخه (<code>version="0.1.0"</code>)، می‌توان تغییرات کتابخانه مشترک را مدیریت کرد و اطمینان حاصل نمود که سرویس‌ها از نسخه سازگار استفاده می‌کنند.</li>
                    <li><strong>وارد کردن تمیز کد (Clean Imports):</strong> پس از نصب، می‌توان به سادگی و بدون مسیردهی نسبی پیچیده، ماژول‌ها را import کرد (مثلاً <code>from core.models import Product</code>).</li>
                </ul>
            </section>
            <section id="integration">
                <h2>۳. نحوه دسترسی سرویس‌ها در محیط Docker</h2>
                <p>
                    یکپارچه‌سازی کتابخانه مشترک با سرویس‌های ایزوله در Docker Compose با یک تکنیک هوشمندانه انجام شده است. این فرآیند دو مرحله کلیدی دارد:
                </p>
                <ol style="list-style-type: decimal; padding-right: 40px;">
                    <li>
                        <strong>Mount کردن کد با <code>volumes</code>:</strong>
                        در فایل <code>docker-compose.yml</code>، پوشه <code>shared_libs/core</code> از سیستم میزبان به یک مسیر مشخص در داخل هر کانتینر (مثلاً <code>/usr/src/shared_libs/core/</code>) متصل (mount) می‌شود.
                    </li>
                    <li>
                        <strong>نصب در حالت قابل ویرایش (Editable Mode):</strong>
                        دستور اصلی در بخش <code>command</code> هر سرویس، این پکیج را نصب می‌کند:
                        <pre><code>command: >
  sh -c "pip install -e /usr/src/shared_libs/core/ && ..."</code></pre>
                        فلگ <span class="key-concept">-e</span> یا <span class="key-concept">--editable</span> به <code>pip</code> می‌گوید که به جای کپی کردن فایل‌ها، یک لینک به پوشه اصلی ایجاد کند. این به معنای <strong class="highlight">Live Reloading</strong> برای کتابخانه مشترک است؛ هر تغییری در کد <code>shared_libs</code> روی سیستم شما، فوراً در تمام سرویس‌های در حال اجرا منعکس می‌شود، بدون نیاز به build مجدد ایمیج.
                    </li>
                </ol>
            </section>
            <section id="challenges">
                <h2>۴. چالش‌ها و راهکارهای پیاده‌سازی</h2>
                <div class="note">
                    <h3>چالش: ایزوله‌سازی کانتینر و مسیرهای پایتون (Python Path)</h3>
                    <p>
                        هر کانتینر داکر یک فایل سیستم کاملاً ایزوله دارد. صرفاً کپی یا Mount کردن پوشه <code>shared_libs</code> به داخل کانتینر کافی نیست. مفسر پایتون در سرویس <code>admin_site</code> به صورت پیش‌فرض از وجود مسیر <code>shared_libs.core</code> آگاه نیست و تلاش برای ایمپورت کردن ماژولی مانند <code>import shared_libs.core.models</code> با خطای <code>ModuleNotFoundError</code> مواجه خواهد شد. پایتون تنها مسیرهای استاندارد (مانند <code>site-packages</code>) و پوشه کاری فعلی (<code>WORKDIR</code>) را جستجو می‌کند.
                    </p>
                    <h3>راهکار: نصب پکیج به عنوان راه حل قطعی</h3>
                    <p>
                        راهکار پیاده‌سازی شده در این پروژه، یعنی استفاده از <strong class="highlight"><code>pip install -e</code></strong>، این چالش را به شکلی استاندارد و تمیز حل می‌کند. این دستور، پوشه <code>core</code> را به عنوان یک پکیج معتبر به محیط پایتونِ <strong>درون کانتینر</strong> معرفی می‌کند. در نتیجه، مسیر آن به صورت خودکار به <code>sys.path</code> اضافه شده و به سرویس‌ها اجازه می‌دهد تا با یک `import` سرراست و خوانا (مانند <code>from core.models import User</code>) به ماژول‌های مشترک دسترسی پیدا کنند، گویی که این پکیج از یک منبع رسمی مثل PyPI نصب شده است. این رویکرد هم مشکل ایزوله‌سازی را حل می‌کند و هم خوانایی و قابلیت نگهداری کد را حفظ می‌نماید.
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
