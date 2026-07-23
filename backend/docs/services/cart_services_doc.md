<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی سیستم سبد خرید</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --fg-color: #e2e8f0;
            --card-bg: #1e293b;
            --border-color: #334155;
            --accent-color: #f59e0b; /* Amber 500 */
            --highlight-bg: #fbbf24;
            --code-bg: #020617;
            --green: #4ade80;
            --blue: #38bdf8;
            --red: #f87171;
            --purple: #c084fc;
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
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 0;
            font-size: 16px;
        }
        .container {
            max-width: 1000px;
            margin: 2rem auto;
            padding: 1rem 2rem;
        }
        header {
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
        }
        h1 {
            font-size: 2.4rem;
            color: var(--accent-color);
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
        }
        section {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        h2 {
            font-size: 1.8rem;
            color: var(--fg-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.75rem;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        h3 {
            font-size: 1.3rem;
            color: var(--purple);
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }
        p {
            margin-bottom: 1rem;
            color: #cbd5e1;
        }
        pre {
            background-color: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.2rem;
            overflow-x: auto;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            direction: ltr;
            text-align: left;
            margin: 1rem 0;
        }
        .note {
            background-color: rgba(56, 189, 248, 0.1);
            border-right: 4px solid var(--blue);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            border-radius: 6px;
        }
        .warning {
            background-color: rgba(248, 113, 113, 0.1);
            border-right: 4px solid var(--red);
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            border-radius: 6px;
        }
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 0.5rem;
            vertical-align: middle;
        }
        .badge-app { background: rgba(245, 158, 11, 0.15); color: var(--accent-color); }
        .badge-core { background: rgba(192, 132, 252, 0.15); color: var(--purple); }
        .badge-util { background: rgba(56, 189, 248, 0.15); color: var(--blue); }
        .flow-step {
            display: flex;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }
        .step-num {
            background: var(--accent-color);
            color: #000;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-left: 1rem;
            flex-shrink: 0;
        }
        .step-content strong { color: var(--fg-color); display: block; margin-bottom: 0.3rem;}
        code {
            font-family: inherit;
            color: var(--highlight-bg);
            background: rgba(255,255,255,0.05);
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
        }
        footer {
            text-align: center;
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px dashed var(--border-color);
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی سیستم سبد خرید (Cart System)</h1>
            <p class="subtitle">معماری پردازش سفارشات چاپی، مدیریت فایل‌های حجیم و محاسبه قیمت</p>
        </header>
        <section id="introduction">
            <h2>۱. معرفی و چالش‌ها</h2>
            <p>
                برخلاف فروشگاه‌های معمولی (که فقط محصول و تعداد دارند)، سبد خرید در <strong>پرینتو24</strong> یک موجودیت پیچیده است. هر آیتم در سبد خرید می‌تواند شامل فایل‌های طراحی حجیم (با استانداردهای چاپ)، ابعاد سفارشی (طول و عرض دلخواه) و ویژگی‌های متغیر باشد.
            </p>
            <div class="warning">
                <strong>چالش اصلی:</strong> فایل‌های آپلودی کاربر نباید تا زمان نهایی شدن "افزودن به سبد"، در حافظه اصلی سرور ذخیره شوند. همچنین، اگر کاربر فایل را آپلود کرد ولی خرید را تکمیل نکرد، فایل‌های بیهوده نباید فضای سرور را اشغال کنند.
            </div>
        </section>
        <section id="workflow">
            <h2>۲. جریان داده (Data Flow)</h2>
            <p>فرآیند افزودن یک محصول به سبد خرید طی مراحل زیر انجام می‌شود:</p>
            <div class="flow-step">
                <div class="step-num">۱</div>
                <div class="step-content">
                    <strong>آپلود موقت (Temp Upload)</strong>
                    فرانت‌اند فایل را به اندپوینت موقت می‌فرستد. سرویس <code>TemporaryFileService</code> فایل را از نظر فنی (DPI, CMYK, Dimensions) بررسی کرده و در پوشه <code>/temp</code> ذخیره می‌کند. نام فایل برگردانده می‌شود.
                </div>
            </div>
            <div class="flow-step">
                <div class="step-num">۲</div>
                <div class="step-content">
                    <strong>درخواست افزودن (Add Request)</strong>
                    فرانت‌اند نام فایل‌های موقت + ویژگی‌های محصول (سایز، تیراژ، متریال) را به اندپوینت <code>AddToCartView</code> می‌فرستد.
                </div>
            </div>
            <div class="flow-step">
                <div class="step-num">۳</div>
                <div class="step-content">
                    <strong>اعتبارسنجی و آماده‌سازی (Orchestration)</strong>
                    سرویس <code>AddToCartService</code> داده‌ها را اعتبارسنجی می‌کند و فایل‌ها را از پوشه <code>/temp</code> به پوشه دائمی کاربر (مثلاً <code>/cart_uploads/user_12/</code>) منتقل می‌کند.
                </div>
            </div>
            <div class="flow-step">
                <div class="step-num">۴</div>
                <div class="step-content">
                    <strong>ثبت نهایی در دامین (Domain Commit)</strong>
                    سرویس <code>CartDomainService</code> قیمت دقیق را محاسبه کرده و آیتم را همراه با لینک فایل‌ها در دیتابیس به صورت <strong>تراکنش اتمیک</strong> ذخیره می‌کند.
                </div>
            </div>
        </section>
        <section id="services-app">
            <h2>۳. سرویس‌های لایه اپلیکیشن <span class="badge badge-app">Application Layer</span></h2>
            <p>این سرویس‌ها در <code>customer_site</code> قرار دارند و وظیفه هماهنگی درخواست‌های وب را دارند.</p>
            <h3><code>AddToCartService</code> (The Facade)</h3>
            <p>این کلاس مغز متفکر پشت API افزودن به سبد خرید است. خودش کار سنگین نمی‌کند، بلکه مدیریت می‌کند:</p>
            <ul>
                <li>فراخوانی <code>CartDataValidator</code> برای اطمینان از اینکه سایز انتخاب شده متعلق به محصول است.</li>
                <li>فراخوانی <code>FileFinalizeService</code> برای جابجایی فایل‌ها.</li>
                <li>فراخوانی <code>CartDomainService</code> برای ثبت در دیتابیس.</li>
            </ul>
            <h3><code>FileFinalizeService</code> (The Mover)</h3>
            <p>وظیفه خطیر انتقال فایل از حافظه موقت به دائم را دارد. اگر در حین انتقال خطایی رخ دهد، عملیات را Rollback می‌کند.</p>
            <pre><code>def prepare_files_for_domain(self, temp_files, user_id):
    # چک کردن وجود فایل در temp
    # انتقال (Move) به cart_uploads/{user_id}
    # بازگرداندن مسیر نسبی برای دیتابیس</code></pre>
            <h3><code>TemporaryFileService</code> (The Gatekeeper)</h3>
            <p>این سرویس قبل از هر چیزی اجرا می‌شود. اجازه نمی‌دهد فایل بی‌کیفیت وارد سیستم شود.</p>
            <ul>
                <li>بررسی <strong>Dimensions:</strong> آیا ابعاد فایل با سایز انتخابی محصول (یا ابعاد دلخواه) می‌خورد؟</li>
                <li>بررسی <strong>CMYK:</strong> آیا فایل برای چاپ افست آماده است؟</li>
                <li>بررسی <strong>DPI:</strong> آیا کیفیت فایل حداقل ۳۰۰ است؟</li>
            </ul>
        </section>
        <section id="services-core">
            <h2>۴. سرویس‌های لایه هسته <span class="badge badge-core">Core Domain</span></h2>
            <p>این سرویس‌ها در <code>shared_libs</code> قرار دارند و قوانین بیزنس خالص را اجرا می‌کنند.</p>
            <h3><code>CartDomainService</code></h3>
            <p>تنها جایی که اجازه دارد در جداول <code>Cart</code> و <code>CartItem</code> بنویسد. متد کلیدی آن <code>add_complex_item</code> است که به صورت Atomic اجرا می‌شود.</p>
            <h3><code>ProductPriceCalculator</code></h3>
            <p>موتور قیمت‌گذاری سیستم. قیمت را بر اساس فرمول زیر محاسبه می‌کند:</p>
            <div class="note">
                Price = (قیمت تیراژ + قیمت متریال + قیمت سایز + قیمت آپشن‌ها) × (۱ + درصد تغییرات)
            </div>
        </section>
        <section id="api-integration">
            <h2>۵. راهنمای توسعه‌دهندگان فرانت‌‌اند</h2>
            <h3>مرحله ۱: آپلود فایل</h3>
            <p>به ازای هر نیازمندی فایل (مثلاً "طرح رو")، یک درخواست به این اندپوینت بزنید:</p>
            <pre><code>POST /api/v1/cart/upload-temp/
Body: { 
    "product_id": 1, 
    "file": [BINARY], 
    "size_id": 5 (یا custom_width/height) 
}
Response: { "temp_filename": "uuid-xxx.tif" }</code></pre>
            <h3>مرحله ۲: افزودن به سبد</h3>
            <p>نام فایل دریافتی را به همراه سایر مشخصات ارسال کنید:</p>
            <pre><code>POST /api/v1/cart/add/
Body: {
    "product_slug": "business-card-matte",
    "quantity": 1000,
    "selections": {
        "quantity_id": 10,
        "material_id": 2,
        "size_id": 5,
        "options_ids": [1, 4]
    },
    "temp_files": {
        "1": "uuid-xxx.tif" // کلید = ID نیازمندی آپلود
    }
}</code></pre>
        </section>
        <section id="devops">
            <h2>۶. نکات زیرساخت (DevOps)</h2>
            <div class="warning">
                <strong>Volume Mapping:</strong> پوشه‌های <code>media/uploads/temp</code> و <code>media/cart_uploads</code> باید حتماً روی دیسک پایدار (Persistent Volume) باشند.
            </div>
            <ul>
                <li><strong>Cleanup Task:</strong> یک CronJob باید تنظیم شود تا فایل‌های موجود در پوشه <code>temp</code> که قدیمی‌تر از ۲۴ ساعت هستند را به صورت خودکار حذف کند.</li>
                <li><strong>Validation Dependencies:</strong> برای بررسی CMYK و DPI، کتابخانه‌های سیستمی مانند <code>Pillow</code> و متعلقات آن باید در Dockerfile نصب شده باشند.</li>
            </ul>
        </section>
    </div>
    <footer>
        <p>تیم فنی ShivaTek | مستندسازی نسخه ۲.۰ ماژول سبد خرید</p>
    </footer>
</body>
</html>