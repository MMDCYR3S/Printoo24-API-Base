<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی Docker Compose و Dockerfile</title>
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
            max-width: 900px;
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
            margin-top: 2rem;
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
            content: '✓';
            position: absolute;
            right: 0;
            color: var(--green);
            font-weight: bold;
        }
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
            <h1>مستند فنی معماری Docker</h1>
            <p class="subtitle">تحلیل فایل‌های <code>docker-compose.yml</code> و <code>Dockerfile</code> برای محیط توسعه</p>
        </header>
        <main>
            <section id="introduction">
                <h2>۱. مقدمه و هدف</h2>
                <p>
                    این مستند به تشریح کامل فایل <code>docker-compose.yml</code> و <code>Dockerfile</code> مشترک پروژه می‌پردازد. هدف اصلی این ساختار، تعریف، راه‌اندازی و مدیریت یکپارچه و ایزوله تمام سرویس‌های مورد نیاز برای محیط توسعه محلی (Local Development) است. با این روش، یک محیط قابل تکرار (Reproducible) و سازگار (Consistent) برای تمام اعضای تیم فراهم می‌شود.
                </p>
                <div class="note">
                    <strong>نحوه راه‌اندازی:</strong> برای اجرای تمام سرویس‌ها، کافیست دستور زیر را در ریشه پروژه اجرا کنید:
                    <pre><code>docker-compose up --build</code></pre>
                    فلگ <code>--build</code> ایمیج‌ها را بر اساس آخرین تغییرات کد، دوباره می‌سازد.
                </div>
            </section>
            <section id="services">
                <h2>۲. تحلیل سرویس‌های Docker Compose</h2>
                <p>فایل <code>docker-compose.yml</code> وظیفه ارکستراسیون (هماهنگی) کانتینرهای مختلف پروژه را بر عهده دارد. در ادامه، هر سرویس به تفکیک بررسی می‌شود.</p>
                <h3>سرویس `db` (پایگاه داده PostgreSQL)</h3>
                <p>این سرویس، پایگاه داده اصلی پروژه را راه‌اندازی می‌کند.</p>
                <ul>
                    <li><strong>ایمیج:</strong> استفاده از <code>postgres:17-alpine</code>، یک نسخه سبک و به‌روز.</li>
                    <li><strong>پایداری داده‌ها (Data Persistence):</strong> با استفاده از <code>volumes</code>، دیتای پایگاه داده روی سیستم میزبان ذخیره می‌شود. این کار از پاک شدن اطلاعات با هر بار ری‌استارت کانتینر جلوگیری می‌کند. این یک <strong class="highlight">مفهوم کلیدی</strong> در کار با دیتابیس‌ها در داکر است.</li>
                    <li><strong>دسترسی از بیرون:</strong> پورت <code>5432</code> کانتینر به پورت <code>5432</code> میزبان متصل شده تا بتوان با ابزارهایی مثل DBeaver به آن وصل شد.</li>
                    <li><strong>مدیریت متغیرها:</strong> اطلاعات حساس مانند نام کاربری و رمز عبور از طریق <code>env_file</code> خوانده می‌شوند تا در کد هاردکد نشوند.</li>
                </ul>
                <h3>سرویس `redis` (کش و صف پیام)</h3>
                <p>این سرویس یک دیتابیس in-memory از نوع Redis را اجرا می‌کند که دو نقش حیاتی دارد:</p>
                <ul>
                    <li><strong>کش (Caching):</strong> برای ذخیره موقت داده‌های پرتکرار و افزایش سرعت پاسخ‌دهی API.</li>
                    <li><strong>صف پیام (Message Broker):</strong> به عنوان واسط بین اپلیکیشن‌های ما و پردازشگرهای پس‌زمینه (Celery) عمل می‌کند. تسک‌های سنگین به این صف ارسال می‌شوند.</li>
                </ul>
                <h3>سرویس‌های `admin_site` و `customer_site` (اپلیکیشن‌های اصلی)</h3>
                <p>این دو سرویس، هسته اصلی APIهای پروژه هستند که ساختاری مشابه دارند. مهم‌ترین ویژگی‌های آن‌ها در Docker Compose عبارتند از:</p>
                <ul>
                    <li>
                        <strong>توسعه سریع با Volumes:</strong> دو مسیر کلیدی به داخل کانتینر mount می‌شوند:
                        <ol>
                            <li>کد خود سرویس (مثلاً <code>./services/admin_site/</code>)</li>
                            <li>کد کتابخانه مشترک (<code>./shared_libs/core/</code>)</li>
                        </ol>
                        این کار قابلیت <span class="key-concept">Live Reloading</span> را فعال می‌کند؛ یعنی هر تغییری در کد بلافاصله و بدون نیاز به build مجدد در کانتینر اعمال می‌شود.
                    </li>
                    <li>
                        <strong>نصب کتابخانه مشترک به صورت Editable:</strong>
                        <p>دستور <code>pip install -e /usr/src/shared_libs/core/</code> که در <code>command</code> هر سرویس آمده، کتابخانه مشترک را به صورت "قابل ویرایش" نصب می‌کند. این یعنی تغییرات در `shared_libs` فوراً در هر دو سرویس `admin_site` و `customer_site` منعکس می‌شود.</p>
                    </li>
                     <li>
                        <strong>ترتیب اجرا:</strong> با استفاده از <code>depends_on</code>، تضمین می‌شود که این سرویس‌ها تنها پس از آمادگی کامل <code>db</code> و <code>redis</code> شروع به کار کنند.
                    </li>
                </ul>
                <pre dir="ltr"><code># بخشی از سرویس admin_site در docker-compose.yml
command: >
  sh -c "pip install -e /usr/src/shared_libs/core/ &&
         python manage.py runserver 0.0.0.0:8010"
volumes:
  - ./services/admin_site/:/usr/src/app/
  - ./shared_libs/core/:/usr/src/shared_libs/core/
depends_on:
  - db
  - redis</code></pre>
                <h3>سرویس‌های `celery_worker` (پردازشگرهای پس‌زمینه)</h3>
                <p>این سرویس‌ها وظیفه اجرای تسک‌های سنگین (مانند ارسال ایمیل) را در پس‌زمینه بر عهده دارند تا API اصلی سریع و پاسخگو بماند.</p>
                <ul>
                    <li>این سرویس‌ها از همان <code>Dockerfile</code> و <code>build context</code> اپلیکیشن اصلی استفاده می‌کنند تا از هرگونه عدم تطابق وابستگی‌ها جلوگیری شود.</li>
                    <li>تنها تفاوت آن‌ها در <code>command</code> است که به جای `runserver`، دستور اجرای Celery worker اجرا می‌شود.</li>
                </ul>
            </section>
            <section id="dockerfile">
                <h2>۳. تحلیل Dockerfile مشترک</h2>
                <p>تمام سرویس‌های پایتونی (APIها و Workerها) از یک `Dockerfile` پایه مشترک برای ساخت ایمیج خود استفاده می‌کنند. این فایل با رعایت بهترین شیوه‌ها طراحی شده است.</p>
                <pre dir="ltr"><code>FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /usr/src/app
# ۱. کپی و نصب نیازمندی‌ها
COPY ./requirements/dev/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# ۲. کپی کردن باقی کد برنامه
COPY . .
</code></pre>
                <div class="note">
                    <strong class="highlight">نکته کلیدی: بهینه‌سازی لایه‌های کش داکر</strong>
                    <p>
                        ترتیب دستورات در این `Dockerfile` بسیار مهم است. ابتدا <strong>فقط فایل `requirements.txt`</strong> کپی و نصب می‌شود و سپس باقی کدها کپی می‌شوند. از آنجایی که وابستگی‌ها به ندرت تغییر می‌کنند ولی کد برنامه مدام در حال تغییر است، داکر لایه سنگین `pip install` را کش می‌کند. در نتیجه، هنگام build مجدد، فقط لایه آخر (کپی کد) اجرا شده و فرآیند build <strong>بسیار سریع‌تر</strong> خواهد بود.
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
