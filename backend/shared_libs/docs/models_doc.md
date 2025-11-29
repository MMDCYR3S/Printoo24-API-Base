<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی لایه مدل‌ها (Data Layer)</title>
    <style>
        /* Modern Dark Theme for Tech Docs */
        :root {
            --bg-color: #1a1b26; /* Dark background */
            --fg-color: #c0caf5; /* Light foreground text */
            --card-bg: #24283b; /* Slightly lighter background for cards/code */
            --border-color: #414868;
            --accent-color: #7aa2f7; /* Blue for headers and links */
            --highlight-bg: #bb9af7; /* Purple for highlights */
            --highlight-fg: #1a1b26;
            --green: #9ece6a;
            --yellow: #e0af68;
            --red: #f7768e;
            --orange: #ff9e64;
        }
        @font-face {
            font-family: 'Vazirmatn';
            src: url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
            font-weight: 100 900;
            font-display: swap;
        }
        body {
            background-color: var(--bg-color);
            color: var(--fg-color);
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 0;
            font-size: 16px;
        }
        .container {
            max-width: 950px;
            margin: 2rem auto;
            padding: 1rem 2rem;
            background-color: var(--bg-color);
        }
        h1, h2, h3 {
            color: var(--accent-color);
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }
        h1 {
            font-size: 2.5rem;
            text-align: center;
            border-bottom: none;
            margin-bottom: 0;
        }
        .subtitle {
            text-align: center;
            color: #a9b1d6;
            margin-top: 0.5rem;
            font-size: 1.1rem;
        }
        h2 {
            font-size: 2rem;
            margin-top: 3rem;
        }
        h3 {
            font-size: 1.5rem;
            color: var(--green);
            border-bottom-style: dashed;
            margin-top: 2.5rem;
        }
        a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.2s ease-in-out;
        }
        a:hover {
            color: var(--highlight-bg);
        }
        strong, .highlight {
            color: var(--yellow);
            font-weight: 600;
        }
        .key-concept {
            background-color: rgba(187, 154, 247, 0.1);
            color: var(--highlight-bg);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.95em;
        }
        pre {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
        }
        code {
            font-family: inherit;
        }
        ul {
            list-style-type: none;
            padding-right: 20px;
        }
        li {
            position: relative;
            padding-right: 25px;
            margin-bottom: 0.75rem;
        }
        li::before {
            content: '»';
            position: absolute;
            right: 0;
            color: var(--accent-color);
            font-weight: bold;
        }
        .toc {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 1rem 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
        }
        .toc h3 {
            margin-top: 0;
            border: none;
        }
        .toc ul { padding: 0;}
        .toc li { margin-bottom: 0.5rem;}
        .toc li::before { content: '•'; color: var(--green);}
        footer {
            text-align: center;
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
            color: #a9b1d6;
        }
        .note {
            background-color: rgba(122, 162, 247, 0.1);
            border-right: 4px solid var(--accent-color);
            padding: 1rem 1.5rem;
            margin: 2rem 0;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی لایه مدل‌ها (Data Layer)</h1>
            <p class="subtitle">تحلیل دیاگرام ارتباط موجودیت‌ها (ERD) و ساختار داده‌های پروژه</p>
        </header>
        <nav class="toc">
            <h3>فهرست مطالب</h3>
            <ul>
                <li><a href="#intro">مقدمه: نقش پوشه Models</a></li>
                <li><a href="#user-models">ماژول کاربر (`user.py`)</a></li>
                <li><a href="#product-models">ماژول محصول (`product.py`) - هسته اصلی سیستم</a></li>
                <li><a href="#cart-models">ماژول سبد خرید (`cart.py`)</a></li>
                <li><a href="#order-models">ماژول سفارش (`order.py`)</a></li>
                <li><a href="#notification-models">ماژول اعلان‌ها (`notification.py`)</a></li>
                <li><a href="#init-file">فایل `__init__.py`: تسهیل در دسترسی</a></li>
                <li><a href="#conclusion">جمع‌بندی: وضعیت فعلی و آینده</a></li>
            </ul>
        </nav>
        <main>
            <section id="intro">
                <h2>مقدمه: نقش پوشه Models</h2>
                <p>
                    پوشه <code>models</code> در اپلیکیشن <code>core</code>، قلب تپنده و پایه اصلی داده‌های کل پروژه است. این بخش، ساختار جداول پایگاه داده، روابط بین آن‌ها و منطق اولیه داده‌ها را تعریف می‌کند. طراحی دقیق و اصولی این لایه، سنگ بنای یک سیستم قابل توسعه و نگهداری است. در ادامه، هر یک از فایل‌های این پوشه به تفصیل شرح داده می‌شوند.
                </p>
            </section>
            <section id="user-models">
                <h2>ماژول کاربر (`user.py`)</h2>
                <p>این ماژول مسئولیت مدیریت تمام جنبه‌های مربوط به کاربران، احراز هویت، سطوح دسترسی و اطلاعات پروفایل آن‌ها را بر عهده دارد.</p>
                <h3>مدل `User`</h3>
                <ul>
                    <li><strong>معماری:</strong> این مدل با ارث‌بری از <span class="key-concept">AbstractBaseUser</span> و <span class="key-concept">PermissionsMixin</span>، مدل کاربر پیش‌فرض جنگو را با انعطاف‌پذیری کامل جایگزین کرده است. این کار به ما اجازه می‌دهد تا <strong class="highlight">نام کاربری (`username`)</strong> را به عنوان فیلد اصلی ورود (<code>USERNAME_FIELD</code>) تعریف کنیم و کنترل کاملی روی فیلدهای کاربر داشته باشیم.</li>
                    <li><strong>مدیر مدل:</strong> از یک <code>UserManager</code> سفارشی برای مدیریت ایجاد کاربران عادی و ابرکاربران (Superusers) استفاده می‌شود که منطق ایجاد کاربر را متمرکز می‌کند.</li>
                </ul>
                <h3>مدل‌های `Role` و `UserRole`</h3>
                <ul>
                    <li><strong>هدف:</strong> این دو مدل یک سیستم مدیریت نقش (Role-Based Access Control) را پیاده‌سازی می‌کنند.</li>
                    <li><strong>روابط:</strong> مدل `Role` از طریق یک رابطه <span class="key-concept">ManyToManyField</span> به مدل `Permission` پیش‌فرض جنگو متصل است. مدل `UserRole` به عنوان یک جدول واسط عمل کرده و یک کاربر (`User`) را به یک نقش (`Role`) خاص متصل می‌کند. این ساختار اجازه می‌دهد تا به هر کاربر چندین نقش تخصیص داده شود.</li>
                </ul>
                <h3>مدل‌های `Wallet` و `WalletTransaction`</h3>
                <ul>
                    <li><strong>هدف:</strong> پیاده‌سازی سیستم کیف پول برای هر کاربر.</li>
                    <li><strong>روابط:</strong> مدل `Wallet` با یک رابطه <span class="key-concept">OneToOneField</span> به `User` متصل است، یعنی هر کاربر دقیقاً یک کیف پول دارد.</li>
                    <li><strong>تراکنش‌ها:</strong> مدل `WalletTransaction` تمام تغییرات موجودی کیف پول را ثبت می‌کند. هر تراکنش دارای نوع (افزایش، کاهش، پرداخت و...)، مبلغ و موجودی پس از عملیات است که قابلیت حسابرسی کامل را فراهم می‌کند.</li>
                </ul>
                <h3>مدل `CustomerProfile`</h3>
                <ul>
                    <li><strong>هدف:</strong> جداسازی اطلاعات احراز هویت (در مدل `User`) از اطلاعات پروفایل شخصی مشتری. این یک <strong class="highlight">Best Practice</strong> در طراحی مدل است.</li>
                    <li><strong>روابط:</strong> این مدل نیز با یک رابطه <span class="key-concept">OneToOneField</span> به `User` متصل است و اطلاعاتی مانند نام، آدرس و شماره تماس را نگهداری می‌کند.</li>
                </ul>
            </section>
            <section id="product-models">
                <h2>ماژول محصول (`product.py`) - هسته اصلی سیستم</h2>
                <p>این ماژول پیچیده‌ترین و در عین حال حیاتی‌ترین بخش سیستم است که تمام جنبه‌های مربوط به محصولات، دسته‌بندی‌ها، قیمت‌گذاری و ویژگی‌های آن‌ها را مدیریت می‌کند.</p>
                <h3>مدل `ProductCategory`</h3>
                <ul>
                    <li><strong>معماری:</strong> با استفاده از کتابخانه `django-mptt` و ارث‌بری از <span class="key-concept">MPTTModel</span>، یک ساختار درختی برای دسته‌بندی محصولات پیاده‌سازی شده است. فیلد <span class="key-concept">TreeForeignKey</span> به `self` اجازه ایجاد دسته‌بندی‌های تو در تو با عمق نامحدود را می‌دهد.</li>
                </ul>
                <h3>مدل `Product`</h3>
                <ul>
                    <li><strong>موجودیت مرکزی:</strong> این مدل، نقطه ثقل ماژول است و اطلاعات پایه محصول مانند نام، دسته، قیمت پایه و توضیحات را در خود دارد.</li>
                    <li><strong>قیمت‌گذاری پویا:</strong> فیلدهایی مانند <code>price_per_square_unit</code> (برای محصولات با ابعاد سفارشی) و <code>price_modifier_percent</code> (برای اعمال تخفیف یا افزایش قیمت کلی) امکان قیمت‌گذاری بسیار انعطاف‌پذیر را فراهم می‌کنند.</li>
                    <li><strong>تولید خودکار کد و اسلاگ:</strong> متد `save` به صورت خودکار یک اسلاگ (slug) خوانا برای URL و یک کد محصول یکتا بر اساس دسته‌بندی و سال تولید می‌کند.</li>
                </ul>
                <h3>مدل‌های ویژگی محصول (Product Attributes)</h3>
                <p>سیستم به جای افزودن فیلدهای زیاد به مدل `Product`، از مدل‌های جداگانه برای ویژگی‌ها و جداول واسط برای اتصال آن‌ها به محصول استفاده می‌کند. این طراحی، نرمال‌سازی پایگاه داده را بهبود بخشیده و انعطاف‌پذیری بالایی ایجاد می‌کند.</p>
                <ul>
                    <li><strong>`Size`, `Material`, `Quantity`, `Option`</strong>: این‌ها مدل‌های مستقلی هستند که ویژگی‌های قابل استفاده مجدد را تعریف می‌کنند (مثلاً سایز A4، جنس گلاسه، تیراژ ۱۰۰۰ عدد، ویژگی "نوع چاپ").</li>
                    <li><strong>`ProductSize`, `ProductMaterial`, `ProductQuantity`, `ProductOption`</strong>: این‌ها <strong class="highlight">جداول واسط (Junction Tables)</strong> هستند. هر کدام از این مدل‌ها یک محصول را به یکی از ویژگی‌های بالا متصل می‌کنند. نکته کلیدی در بسیاری از آنها، فیلد <span class="key-concept">price_impact</span> است که مشخص می‌کند انتخاب آن ویژگی چقدر به قیمت پایه محصول اضافه یا از آن کم می‌کند.</li>
                </ul>
                <h3>مدل‌های `ProductImage` و `ProductAttachment`</h3>
                <ul>
                    <li>این مدل‌ها برای مدیریت تصاویر و فایل‌های پیوست مربوط به هر محصول طراحی شده‌اند و از طریق `ForeignKey` به مدل `Product` متصل می‌شوند.</li>
                </ul>
            </section>
            <section id="cart-models">
                <h2>ماژول سبد خرید (`cart.py`)</h2>
                <p>این ماژول وضعیت موقت سبد خرید کاربر را قبل از نهایی شدن سفارش مدیریت می‌کند.</p>
                <ul>
                    <li><strong>`Cart`</strong>: مدل اصلی که از طریق `ForeignKey` به `User` متصل است و به عنوان یک نگهدارنده (Container) برای آیتم‌ها عمل می‌کند.</li>
                    <li><strong>`CartItem`</strong>: هر آیتم اضافه شده به سبد خرید را نمایندگی می‌کند. این مدل به `Product` و `Cart` متصل است. فیلد <span class="key-concept">JSONField</span> با نام `items` یک قابلیت بسیار قدرتمند است که تمام ویژگی‌های انتخاب شده توسط کاربر برای آن محصول خاص (مانند سایز، جنس، آپشن‌های خاص و ...) را به صورت ساختاریافته ذخیره می‌کند.</li>
                </ul>
            </section>
            <section id="order-models">
                <h2>ماژول سفارش (`order.py`)</h2>
                <p>این ماژول مسئولیت ثبت نهایی خرید کاربر، آیتم‌های سفارش داده شده و فایل‌های مربوط به آن را بر عهده دارد. داده‌های این بخش پس از ثبت، معمولاً تغییرناپذیر هستند.</p>
                <ul>
                    <li><strong>`OrderStatus`</strong>: یک مدل جداگانه برای تعریف وضعیت‌های مختلف سفارش (مانند "در حال پردازش"، "ارسال شده"). این طراحی به ادمین اجازه می‌دهد وضعیت‌های جدید را بدون تغییر در کد اضافه کند.</li>
                    <li><strong>`Order`</strong>: سرآیند (Header) سفارش که اطلاعات کلی مانند کاربر، وضعیت و قیمت کل را نگهداری می‌کند.</li>
                    <li><strong>`OrderItem`</strong>: مشابه `CartItem`، هر آیتم داخل سفارش را با جزئیات کامل (محصول، تعداد، قیمت نهایی و ویژگی‌های انتخاب شده در فیلد `items`) ذخیره می‌کند.</li>
                    <li><strong>`DesignFile` و `OrderItemDesignFile`</strong>: این ساختار به کاربر اجازه می‌دهد برای هر آیتم سفارش، یک یا چند فایل طراحی آپلود کند. `OrderItemDesignFile` جدول واسطی است که این ارتباط چند به چند را مدیریت می‌کند.</li>
                </ul>
            </section>
            <section id="notification-models">
                <h2>ماژول اعلان‌ها (`notification.py`)</h2>
                <p>این ماژول یک سیستم اطلاع‌رسانی بسیار انعطاف‌پذیر را پیاده‌سازی می‌کند.</p>
                <h3>مدل `CustomerNotification`</h3>
                <ul>
                    <li><strong>معماری پیشرفته:</strong> این مدل از <strong class="highlight">GenericForeignKey</strong> جنگو استفاده می‌کند. این الگو به یک مدل اجازه می‌دهد تا به هر مدل دیگری در پایگاه داده متصل شود، بدون اینکه نیاز به تعریف `ForeignKey` مجزا برای هر کدام باشد.</li>
                    <li><strong>اجزاء کلیدی:</strong>
                        <ul>
                            <li><span class="key-concept">content_type</span>: نوع مدل هدف را ذخیره می‌کند (مثلاً مدل `Order`).</li>
                            <li><span class="key-concept">object_id</span>: شناسه (PK) رکورد هدف را ذخیره می‌کند (مثلاً ID سفارش `123`).</li>
                            <li><span class="key-concept">generic_key</span>: فیلد مجازی که این دو را برای دسترسی به شیء واقعی ترکیب می‌کند.</li>
                        </ul>
                    </li>
                    <li><strong>کاربرد:</strong> با این طراحی، می‌توان یک نوتیفیکیشن را به یک سفارش، یک محصول جدید، یک تراکنش کیف پول یا هر موجودیت دیگری در سیستم مرتبط کرد.</li>
                </ul>
            </section>
            <section id="init-file">
                <h2>فایل `__init__.py`: تسهیل در دسترسی</h2>
                <p>
                    فایل <code>__init__.py</code> در پوشه <code>models</code> نقش یک "جمع‌کننده" را ایفا می‌کند. با وارد کردن (import) تمام مدل‌ها از فایل‌های مختلف در این فایل، به توسعه‌دهندگان اجازه می‌دهد تا به جای مسیرهای طولانی مانند <code>from core.models.product import Product</code>، از یک مسیر ساده و خوانا مانند <code>from core.models import Product</code> استفاده کنند. این کار خوانایی کد را در سایر بخش‌های پروژه به شدت افزایش می‌دهد.
                </p>
            </section>
            <section id="conclusion">
                <h2>جمع‌بندی: وضعیت فعلی و آینده</h2>
                <div class="note">
                    <strong>توجه:</strong> ساختار مدل‌های تشریح شده در این مستند، نسخه اولیه و هسته اصلی محصول در فاز <strong>محصول کمینه قابل ارائه (MVP)</strong> است. این طراحی یک پایه محکم و مقیاس‌پذیر را فراهم می‌کند که به مرور زمان و بر اساس نیازهای جدید کسب‌وکار، قابلیت گسترش و تکمیل را خواهد داشت.
                </div>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>
