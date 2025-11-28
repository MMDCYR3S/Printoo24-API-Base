<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی بازآرایی زیرساخت Monorepo و Docker</title>
    <style>
        /* Modern Dark Theme for Tech Docs */
        :root {
            --bg-color: #0f172a; /* Slate 900 */
            --fg-color: #e2e8f0; /* Slate 200 */
            --card-bg: #1e293b; /* Slate 800 */
            --border-color: #334155; /* Slate 700 */
            --accent-color: #38bdf8; /* Sky 400 */
            --highlight-bg: #818cf8; /* Indigo 400 */
            --code-bg: #020617; /* Slate 950 */
            --green: #4ade80;
            --yellow: #facc15;
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
        }
        header {
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
        }
        h1 {
            font-size: 2.2rem;
            color: var(--accent-color);
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
        }
        section {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        h2 {
            font-size: 1.6rem;
            color: var(--fg-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.75rem;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        h3 {
            font-size: 1.25rem;
            color: var(--purple);
            margin-top: 1.5rem;
        }
        pre {
            background-color: var(--code-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            direction: ltr;
            text-align: left;
        }
        code {
            font-family: inherit;
            color: var(--accent-color);
        }
        .highlight-text {
            color: var(--yellow);
            font-weight: bold;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            position: relative;
            padding-right: 1.5rem;
            margin-bottom: 0.75rem;
        }
        li::before {
            content: "▹";
            position: absolute;
            right: 0;
            color: var(--accent-color);
        }
        .architecture-diagram {
            font-family: monospace;
            white-space: pre;
            color: var(--green);
            line-height: 1.2;
            direction: ltr;
            text-align: left;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            background-color: rgba(56, 189, 248, 0.1);
            color: var(--accent-color);
            margin-left: 0.5rem;
        }
        .alert {
            background-color: rgba(245, 158, 11, 0.1);
            border-right: 4px solid var(--yellow);
            padding: 1rem;
            border-radius: 4px;
            margin: 1.5rem 0;
        }
        .success {
            background-color: rgba(74, 222, 128, 0.1);
            border-right: 4px solid var(--green);
            padding: 1rem;
            border-radius: 4px;
            margin: 1.5rem 0;
        }
        footer {
            text-align: center;
            color: #64748b;
            margin-top: 4rem;
            padding-top: 1rem;
            border-top: 1px dashed var(--border-color);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی بازآرایی معماری Micro-Modular</h1>
            <p class="subtitle">استانداردسازی ساختار Monorepo، استراتژی Docker Context و مدیریت وابستگی‌های اشتراکی</p>
        </header>
        <main>
            <section id="structure">
                <h2>۱. بازآرایی ساختار پروژه (Monorepo Restructuring)</h2>
                <p>
                    به منظور دستیابی به معماری تمیز (Clean Architecture) و جلوگیری از پیچیدگی‌های غیرضروری، ساختار پوشه‌بندی پروژه از حالت تودرتو (Nested) به حالت تخت (Flat) و استاندارد پایتون تغییر یافت. این تغییر برای تبدیل <code>shared_libs</code> به یک پکیج قابل نصب حیاتی بود.
                </p>
                <h3>ساختار درختی جدید</h3>
                <pre class="architecture-diagram">
Repo Root/
├── docker-compose.yml
├── shared_libs/                <span style="color: #94a3b8;"># <--- Root of Shared Package</span>
│   ├── setup.py                <span style="color: #94a3b8;"># <--- Correct placement for setuptools</span>
│   └── core/                   <span style="color: #94a3b8;"># <--- Actual Python Package</span>
│       ├── __init__.py         <span style="color: #94a3b8;"># <--- Essential for package discovery</span>
│       ├── models/
│       ├── domain/
│       └── apps.py
└── services/
    ├── customer_site/
    └── admin_site/
                </pre>
                <div class="alert">
                    <strong>تغییر مهم:</strong> فایل <code>setup.py</code> اکنون مستقیماً در ریشه <code>shared_libs</code> قرار دارد و پکیج <code>core</code> را شناسایی می‌کند. این ساختار امکان نصب پکیج را به صورت استاندارد (Standard Distribution) فراهم می‌کند.
                </div>
            </section>
            <section id="docker-strategy">
                <h2>۲. تغییر استراتژی Docker Build Context</h2>
                <p>
                    یکی از چالش‌های اصلی در معماری میکروسرویس/ماژولار، دسترسی سرویس‌ها به کدهای مشترک (Shared Libraries) در زمان بیلد داکر بود. پیش از این، کانتکست بیلد محدود به پوشه هر سرویس بود که دسترسی به <code>shared_libs</code> را غیرممکن می‌کرد.
                </p>
                <h3>راهکار: Root Level Context</h3>
                <p>
                    ما <code>Build Context</code> را برای تمام سرویس‌ها به ریشه پروژه (<code>.</code>) تغییر دادیم. این کار به Dockerfile اجازه می‌دهد تا به تمام فایل‌های پروژه دسترسی داشته باشد.
                </p>
                <div class="code-block-title">تغییر در docker-compose.yml</div>
                <pre><code>services:
  customer_site:
    build:
      context: .  <span style="color: #64748b;"># <--- کانتکست بیلد اکنون ریشه پروژه است</span>
      dockerfile: services/customer_site/dockerfiles/dev/Dockerfile
    # ...</code></pre>
            </section>
            <section id="dockerfile">
                <h2>۳. بازنویسی Dockerfile (رویکرد Multi-Layer)</h2>
                <p>
                    فایل <code>Dockerfile</code> جدید به گونه‌ای طراحی شده که هم برای محیط توسعه و هم پروداکشن بهینه باشد. عملیات نصب پکیج مشترک از زمان اجرا (Runtime) به زمان ساخت (Build Time) منتقل شد.
                </p>
                <h3>مراحل کلیدی در Dockerfile</h3>
                <ul>
                    <li><strong>کانتکست ایزوله:</strong> کد سرویس در <code>/app/src</code> و کد مشترک در <code>/app/shared_libs</code> قرار می‌گیرد.</li>
                    <li><strong>نصب وابستگی‌ها:</strong> پکیج <code>core</code> کپی شده و نصب می‌شود.</li>
                    <li><strong>قابلیت حمل:</strong> چون کد مشترک داخل ایمیج <code>COPY</code> می‌شود، ایمیج نهایی مستقل از فایل‌های هاست است (Production Ready).</li>
                </ul>
                <pre><code>FROM python:3.11-slim
WORKDIR /app

# 1. Copy & Install Shared Libs (Core Domain)
COPY ./shared_libs /app/shared_libs
RUN pip install --upgrade pip && \
    pip install -e /app/shared_libs

# 2. Install Service Dependencies
COPY ./services/customer_site/requirements/dev/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# 3. Copy Service Code
COPY ./services/customer_site /app/src
WORKDIR /app/src

CMD ["python", "manage.py", "runserver", "0.0.0.0:9010"]</code></pre>
            </section>
            <section id="dev-environment">
                <h2>۴. پیکربندی محیط توسعه (Hot-Reload & PYTHONPATH)</h2>
                <p>
                    برای تضمین تجربه توسعه روان (DX)، دو تکنیک مهم پیاده‌سازی شد تا تغییرات کد بلافاصله اعمال شوند و پایتون مسیرهای جدید را بشناسد.
                </p>
                <h3>الف) تکنیک PYTHONPATH Injection</h3>
                <p>
                    به جای تکیه بر نصب مجدد پکیج در هر بار اجرای کانتینر، مسیر لایبرری مشترک مستقیماً به <code>PYTHONPATH</code> تزریق شد. این سریع‌ترین و مطمئن‌ترین روش برای محیط توسعه است.
                </p>
                <h3>ب) مدیریت Volumeها</h3>
                <p>
                    برای اعمال آنی تغییرات (Hot Reloading)، دو مسیر حیاتی به کانتینر Mount شدند.
                </p>
                <pre><code>  customer_site:
    environment:
      - PYTHONPATH=/app/shared_libs:$PYTHONPATH  <span style="color: #64748b;"># <--- تضمین شناسایی پکیج Core</span>
    volumes:
      - ./services/customer_site:/app/src        <span style="color: #64748b;"># <--- سینک کد سرویس</span>
      - ./shared_libs:/app/shared_libs           <span style="color: #64748b;"># <--- سینک کد مشترک (Core)</span></code></pre>
                <div class="success">
                    <strong>نتیجه نهایی:</strong> توسعه‌دهنده می‌تواند کدهای <code>core</code> یا <code>customer_site</code> را در سیستم خود تغییر دهد و سرور جنگو به صورت خودکار ریستارت شده و تغییرات را اعمال می‌کند، بدون نیاز به بیلد مجدد.
                </div>
            </section>
        </main>
        <footer>
            <p>تهیه شده توسط تیم فنی ShivaTek | نسخه بازآرایی شده</p>
        </footer>
    </div>
</body>
</html>