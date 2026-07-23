<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی اپلیکیشن Accounts</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی اپلیکیشن Accounts</h1>
            <p class="subtitle">بررسی ساختار، اجزا و نحوه کارکرد اپلیکیشن مدیریت حساب کاربری در پروژه Printoo24</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    اپلیکیشن <code>accounts</code> مسئول مدیریت تمام فرآیندهای مرتبط با حساب کاربری در پروژه Printoo24 است. این اپلیکیشن شامل عملیاتی مانند ثبت‌نام، ورود، تأیید هویت، بازنشانی رمز عبور و مدیریت توکن‌های احراز هویت می‌شود.
                </p>
                <div class="note-info">
                    <h4>ویژگی‌های کلیدی اپلیکیشن</h4>
                    <ul>
                        <li><strong>مدیریت کاربران:</strong> ثبت‌نام، ورود و خروج کاربران</li>
                        <li><strong>تأیید هویت:</strong> ارسال و اعتبارسنجی کد تأیید به ایمیل کاربران</li>
                        <li><strong>امنیت:</strong> مدیریت توکن‌های JWT و بازنشانی رمز عبور</li>
                        <li><strong>پردازش ناهمزمان:</strong> ارسال ایمیل‌ها به صورت ناهمزمان با استفاده از Celery</li>
                    </ul>
                </div>
            </section>
            <section id="structure">
                <h2>۲. ساختار پوشه‌بندی</h2>
                <p>
                    اپلیکیشن <code>accounts</code> دارای ساختار سلسله‌مراتبی و منظمی است که هر بخش مسئولیت خاصی را بر عهده دارد:
                </p>
                <pre dir="ltr"><code>.
├── migrations
│   └── __init__.py
├── services
│   ├── __init__.py
│   ├── auth_service.py
│   ├── password_reset_service.py
│   ├── token_service.py
│   └── verify_service.py
├── tasks
│   ├── __init__.py
│   └── emails.py
├── templates
│   └── email
│       ├── send_reset_password_email.html
│       └── verify_email.html
├── __init__.py
├── admin.py
└── apps.py</code></pre>
                <h3>بررسی هر پوشه و فایل</h3>
                <h4><code>migrations</code></h4>
                <p>
                    این پوشه شامل فایل‌های مربوط به تغییرات ساختار پایگاه داده برای اپلیکیشن است. در حال حاضر تنها فایل <code>__init__.py</code> وجود دارد که نشان‌دهنده عدم اعمال هیچ تغییری در ساختار پایگاه داده توسط این اپلیکیشن است.
                </p>
                <h4><code>services</code></h4>
                <p>
                    پوشه اصلی حاوی منطق تجاری اپلیکیشن است. هر فایل در این پوشه مسئول یک بخش خاص از عملیات حساب کاربری است:
                </p>
                <ul>
                    <li><strong><code>auth_service.py</code>:</strong> مدیریت فرآیندهای احراز هویت شامل ثبت‌نام و ورود کاربران</li>
                    <li><strong><code>password_reset_service.py</code>:</strong> مدیریت فرآیند بازنشانی رمز عبور</li>
                    <li><strong><code>token_service.py</code>:</strong> مدیریت توکن‌های JWT برای احراز هویت</li>
                    <li><strong><code>verify_service.py</code>:</strong> مدیریت فرآیند تأیید هویت کاربران از طریق ایمیل</li>
                </ul>
                <h4><code>tasks</code></h4>
                <p>
                    این پوشه شامل وظایف ناهمزمان (Celery Tasks) مربوط به ارسال ایمیل‌ها است:
                </p>
                <ul>
                    <li><strong><code>emails.py</code>:</strong> تعریف وظایف ناهمزمان برای ارسال ایمیل‌های تأیید و بازنشانی رمز عبور</li>
                </ul>
                <h4><code>templates/email</code></h4>
                <p>
                    پوشه حاوی قالب‌های HTML مورد استفاده در ارسال ایمیل‌ها:
                </p>
                <ul>
                    <li><strong><code>send_reset_password_email.html</code>:</strong> قالب ایمیل بازنشانی رمز عبور</li>
                    <li><strong><code>verify_email.html</code>:</strong> قالب ایمیل تأیید حساب کاربری</li>
                </ul>
                <h4>فایل‌های ریشه اپلیکیشن</h4>
                <ul>
                    <li><strong><code>admin.py</code>:</strong> ثبت مدل‌های مرتبط با حساب کاربری در پنل ادمین جنگو</li>
                    <li><strong><code>apps.py</code>:</strong> پیکربندی اپلیکیشن</li>
                    <li><strong><code>__init__.py</code>:</strong> تبدیل پوشه به پکیج پایتون</li>
                </ul>
            </section>
            <section id="services-details">
                <h2>۳. بررسی جزئیات سرویس‌ها</h2>
                <h3><code>auth_service.py</code></h3>
                <p>
                    کلاس <code>AuthService</code> مسئول مدیریت فرآیندهای احراز هویت است:
                </p>
                <pre dir="ltr"><code>class AuthService:
    def register_user(self, validated_data: Dict[str, Any]) -> User:
        """ثبت‌نام کاربر جدید"""
        
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """ورود کاربر به سیستم"""</code></pre>
                <h3><code>password_reset_service.py</code></h3>
                <p>
                    کلاس <code>PasswordResetService</code> مسئول مدیریت فرآیند بازنشانی رمز عبور:
                </p>
                <pre dir="ltr"><code>class PasswordResetService:
    def send_reset_link(self, email: str) -> None:
        """ارسال لینک بازنشانی رمز عبور"""
        
    def confirm_password_reset(self, uidb64: str, token: str, new_password: str) -> User:
        """تأیید و اعمال رمز عبور جدید"""</code></pre>
                <h3><code>token_service.py</code></h3>
                <p>
                    کلاس <code>TokenService</code> مسئول مدیریت توکن‌های JWT:
                </p>
                <pre dir="ltr"><code>class TokenService:
    @staticmethod
    def create_token_for_user(user: User) -> Dict[str, str]:
        """ایجاد توکن برای کاربر"""
        
    @classmethod
    def refresh_token_for_user(cls, refresh_token: str) -> Dict[str, str]:
        """تازه‌سازی توکن کاربر"""
        
    @staticmethod
    def send_to_blacklist(refresh_token: str) -> None:
        """افزودن توکن به لیست سیاه"""</code></pre>
                <h3><code>verify_service.py</code></h3>
                <p>
                    کلاس <code>VerificationService</code> مسئول فرآیند تأیید هویت کاربران:
                </p>
                <pre dir="ltr"><code>class VerificationService:
    def send_verification_code(self, email: str) -> None:
        """ارسال کد تأیید به ایمیل کاربر"""
        
    def verify_code(self, email: str, code: str) -> bool:
        """تأیید کد ارسال شده توسط کاربر"""</code></pre>
            </section>
            <section id="tasks-details">
                <h2>۴. وظایف ناهمزمان (Celery Tasks)</h2>
                <h3><code>emails.py</code></h3>
                <p>
                    این فایل شامل وظایف ناهمزمان برای ارسال ایمیل‌ها است:
                </p>
                <pre dir="ltr"><code>@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_verification_email_task(user_email: str, verification_code: str):
    """وظیفه ارسال ایمیل تأیید حساب کاربری"""

@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 5})
def send_password_reset_email_task(user_email:str, reset_link: str):
    """وظیفه ارسال ایمیل بازنشانی رمز عبور"""</code></pre>
                <p>
                    این وظایف با استفاده از دکوراتور <code>@shared_task</code> تعریف شده‌اند و دارای قابلیت تلاش مجدد خودکار در صورت بروز خطا هستند.
                </p>
            </section>
            <section id="templates-details">
                <h2>۵. قالب‌های ایمیل</h2>
                <h3><code>verify_email.html</code></h3>
                <p>
                    قالب ایمیل ارسال کد تأیید حساب کاربری که شامل اطلاعات زیر است:
                </p>
                <ul>
                    <li>پیام خوش‌آمدگویی</li>
                    <li>کد تأیید ۶ رقمی</li>
                    <li>اطلاعات مربوط به انقضای کد</li>
                </ul>
                <h3><code>send_reset_password_email.html</code></h3>
                <p>
                    قالب ایمیل ارسال لینک بازنشانی رمز عبور که شامل:
                </p>
                <ul>
                    <li>لینک بازنشانی رمز عبور</li>
                    <li>اطلاعات مربوط به انقضای لینک</li>
                    <li>هشدار در صورت درخواست ناعمدانه</li>
                </ul>
            </section>
            <section id="integration">
                <h2>۶. یکپارچه‌سازی با سایر بخش‌ها</h2>
                <h3>یکپارچه‌سازی با سیستم کاربران مشترک</h3>
                <p>
                    اپلیکیشن <code>accounts</code> از مدل‌های کاربر تعریف شده در اپلیکیشن مشترک <code>core</code> استفاده می‌کند:
                </p>
                <pre dir="ltr"><code>from core.models import User, Role, UserRole, CustomerProfile</code></pre>
                <h3>یکپارچه‌سازی با سیستم کش</h3>
                <p>
                    برای مدیریت کدهای تأیید و محدود کردن درخواست‌های مکرر از سیستم کش استفاده می‌شود:
                </p>
                <pre dir="ltr"><code>from core.common.cache.cache_service import CacheService</code></pre>
                <h3>یکپارچه‌سازی با سیستم ایمیل</h3>
                <p>
                    برای ارسال ایمیل‌ها از سرویس ایمیل تعریف شده در اپلیکیشن مشترک استفاده می‌شود:
                </p>
                <pre dir="ltr"><code>from core.common.email.email_service import EmailService</code></pre>
            </section>
        </main>
        <footer>
            <p>جهت اطلاعات بیشتر راجب سرویس‌ها، به <a href="../services/accounts_services_doc.md">مستندات سرویس‌های اپلیکیشن accounts</a> مراجعه کنید</p>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>