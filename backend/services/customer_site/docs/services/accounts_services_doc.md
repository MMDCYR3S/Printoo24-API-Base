<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی سرویس‌های Accounts</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی سرویس‌های Accounts</h1>
            <p class="subtitle">بررسی جامع سرویس‌ها و ریپازیتوری‌های مربوط به اپلیکیشن مدیریت حساب کاربری در پروژه Printoo24</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    سرویس‌های اپلیکیشن <code>accounts</code> مسئول اجرای منطق تجاری مربوط به عملیات حساب کاربری در پروژه Printoo24 هستند. این سرویس‌ها از الگوی سه لایه (Presentation - Service - Repository) پیروی می‌کنند و مسئولیت‌های خود را به خوبی تقسیم‌بندی شده‌اند.
                </p>
                <div class="note-info">
                    <h4>ویژگی‌های کلیدی سرویس‌ها</h4>
                    <ul>
                        <li><strong>تقسیم‌بندی منطقی:</strong> هر سرویس مسئولیت خاصی را بر عهده دارد</li>
                        <li><strong>وابستگی کم:</strong> سرویس‌ها از طریق interfaceها با یکدیگر ارتباط دارند</li>
                        <li><strong>تست‌پذیری:</strong> ساختار مناسب برای نوشتن unit test</li>
                        <li><strong>قابلیت توسعه:</strong> امکان افزودن قابلیت‌های جدید بدون تغییر در ساختار کلی</li>
                    </ul>
                </div>
            </section>
            <section id="architecture">
                <h2>۲. معماری سرویس‌ها</h2>
                <p>
                    سرویس‌های اپلیکیشن <code>accounts</code> از الگوی سه لایه پیروی می‌کنند:
                </p>
                <ul>
                    <li><strong>لایه Presentation:</strong> شامل API Views و Serializers</li>
                    <li><strong>لایه Service:</strong> شامل منطق تجاری (فایل‌های موجود در پوشه services)</li>
                    <li><strong>لایه Repository:</strong> شامل دسترسی به داده‌ها (فایل‌های موجود در core/common/users)</li>
                </ul>
                <h3>نمودار معماری</h3>
                <pre dir="ltr"><code>API Views/Serializers
        ↓
  Services Layer
   (accounts/services)
        ↓
 Repository Layer
(core/common/users)</code></pre>
                <p>
                    این ساختار اطمینان می‌دهد که منطق تجاری از دسترسی به داده‌ها جدا شده و قابلیت توسعه و نگهداری بالایی دارد.
                </p>
            </section>
            <section id="services">
                <h2>۳. بررسی سرویس‌ها</h2>
                <h3><code>AuthService</code></h3>
                <p>
                    سرویس احراز هویت مسئول مدیریت فرآیندهای ثبت‌نام و ورود کاربران است.
                </p>
                <pre dir="ltr"><code>class AuthService:
    def register_user(self, validated_data: Dict[str, Any]) -> User:
        """ثبت‌نام کاربر جدید"""
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """ورود کاربر به سیستم"""</code></pre>
                <h4>منطق ثبت‌نام</h4>
                <ol>
                    <li>ایجاد کاربر توسط سرویس UserService</li>
                    <li>بررسی وجود نقش "مشتری" و اختصاص آن به کاربر</li>
                    <li>ارسال کد تأیید به ایمیل کاربر</li>
                </ol>
                <h4>منطق ورود</h4>
                <ol>
                    <li>اعتبارسنجی نام کاربری و رمز عبور</li>
                    <li>بررسی فعال بودن حساب کاربری</li>
                    <li>ایجاد توکن‌های JWT برای کاربر</li>
                </ol>
                <h3><code>PasswordResetService</code></h3>
                <p>
                    سرویس بازنشانی رمز عبور مسئول مدیریت فرآیند فراموشی رمز عبور است.
                </p>
                <pre dir="ltr"><code>class PasswordResetService:
    def send_reset_link(self, email: str) -> None:
        """ارسال لینک بازنشانی رمز عبور"""
    def confirm_password_reset(
        self, 
        uidb64: str, 
        token: str, 
        new_password: str
    ) -> User:
        """تأیید و اعمال رمز عبور جدید"""</code></pre>
                <h4>ویژگی‌های کلیدی</h4>
                <ul>
                    <li><strong>جلوگیری از اسپم:</strong> استفاده از کش برای محدود کردن درخواست‌های مکرر</li>
                    <li><strong>امنیت:</strong> استفاده از توکن‌های یک‌بار مصرف و محدودیت زمانی</li>
                    <li><strong>مدیریت خطا:</strong> پیام‌های مناسب برای جلوگیری از User Enumeration</li>
                </ul>
                <h3><code>TokenService</code></h3>
                <p>
                    سرویس مدیریت توکن‌های JWT برای احراز هویت کاربران.
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
                <h4>قابلیت‌ها</h4>
                <ul>
                    <li>ایجاد توکن‌های Access و Refresh</li>
                    <li>تازه‌سازی توکن‌های منقضی شده</li>
                    <li>افزودن توکن‌ها به لیست سیاه برای خروج ایمن</li>
                </ul>
                <h3><code>VerificationService</code></h3>
                <p>
                    سرویس تأیید هویت کاربران از طریق ایمیل.
                </p>
                <pre dir="ltr"><code>class VerificationService:
    def send_verification_code(self, email: str) -> None:
        """ارسال کد تأیید به ایمیل کاربر"""
    def verify_code(self, email: str, code: str) -> bool:
        """تأیید کد ارسال شده توسط کاربر"""</code></pre>
                <h4>ویژگی‌ها</h4>
                <ul>
                    <li>ایجاد کد تصادفی ۶ رقمی</li>
                    <li>ذخیره کد در کش با محدودیت زمانی ۵ دقیقه</li>
                    <li>ارسال ایمیل به صورت ناهمزمان</li>
                    <li>فعال‌سازی حساب کاربری پس از تأیید کد</li>
                </ul>
            </section>
            <section id="repositories">
                <h2>۴. ریپازیتوری‌ها</h2>
                <p>
                    ریپازیتوری‌ها مسئول دسترسی به داده‌ها و انجام عملیات CRUD بر روی مدل‌ها هستند.
                </p>
                <h3><code>IRepository</code> (Interface)</h3>
                <p>
                    ریپازیتوری انتزاعی که به عنوان interface برای سایر ریپازیتوری‌ها عمل می‌کند.
                </p>
                <pre dir="ltr"><code>class IRepository(Generic[T]):
    def get_by_id(self, pk: Any) -> Optional[T]:
        """دریافت یک آبجکت با شناسه"""
    def get_by_slug(self, slug: Any) -> Optional[T]:
        """دریافت یک آبجکت با اسلاگ"""
    def get_all(self) -> List[T]:
        """دریافت همه آبجکت های موجود"""
    def filter(self, **kwargs) -> List[T]:
        """دریافت آبجکت های با شرایط مختلف"""
    def exists(self, **kwargs) -> bool:
        """صحت از وجود یک آبجکت"""
    def create(self, data: Dict[str, Any]) -> T:
        """ایجاد یک آبجکت"""
    def update(self, instance: T, data: Dict[str, Any]) -> T:
        """ویرایش یک آبجکت"""
    def delete(self, instance: T) -> None:
        """حذف یک آبجکت"""</code></pre>
                <h3><code>UserRepository</code></h3>
                <p>
                    ریپازیتوری مخصوص مدیریت کاربران که از IRepository ارث‌بری می‌کند.
                </p>
                <pre dir="ltr"><code>class UserRepository(IRepository[User]):
    def get_by_id(self, id: int) -> User | None:
        """دریافت یک کاربر با شناسه"""
    def get_by_username(self, username: str) -> User | None:
        """دریافت کاربر با نام کاربری"""
    def get_by_email(self, email: str) -> User | None:
        """دریافت کاربر با ایمیل"""
    def save(self, user: User) -> User:
        """ذخیره کاربر"""</code></pre>
            </section>
            <section id="user-service">
                <h2>۵. UserService</h2>
                <p>
                    سرویس مدیریت کاربران که به عنوان یک لایه بین ریپازیتوری و سایر سرویس‌ها عمل می‌کند.
                </p>
                <pre dir="ltr"><code>class UserService:
    def create_user(self, data: Dict[str, Any]) -> User:
        """ایجاد کاربر جدید"""
    def get_by_id(self, id: int) -> User | None:
        """دریافت کاربر با شناسه"""
    def get_by_email(self, email: str) -> User | None:
        """دریافت کاربر با ایمیل"""
    def set_user_as_verified(self, user: User) -> User:
        """تایید کاربر"""
    def set_password(self, user: User, new_password: str):
        """تغییر رمز عبور کاربر"""</code></pre>
                <p>
                    این سرویس از UserRepository برای دسترسی به داده‌ها استفاده می‌کند و منطق تجاری مربوط به کاربران را پیاده‌سازی می‌کند.
                </p>
            </section>
            <section id="dependencies">
                <h2>۶. وابستگی‌ها و ارتباطات</h2>
                <p>
                    سرویس‌ها از طریق dependency injection با یکدیگر ارتباط دارند:
                </p>
                <h3>نمودار وابستگی‌ها</h3>
                <pre dir="ltr"><code>AuthService ────► UserService ────► UserRepository
                    ▲
PasswordResetService ┘

VerificationService ────► UserService

TokenService (مستقل)</code></pre>                
                <h3>استفاده در عمل</h3>
                <pre dir="ltr"><code># در views یا سایر بخش‌های برنامه
user_service = UserService(UserRepository())
auth_service = AuthService(
    user_service=user_service,
    verify_service=VerificationService(user_service)
)
password_reset_service = PasswordResetService(
    user_service=user_service,
    cache_service=CacheService()
)</code></pre>
                <p>
                    این ساختار اطمینان می‌دهد که هر سرویس فقط به واسطه interfaceها با سایر سرویس‌ها ارتباط دارد و وابستگی کمی دارد.
                </p>
            </section>
            <section id="logging">
                <h2>۷. لاگ‌نویسی</h2>
                <p>
                    تمام سرویس‌ها از سیستم لاگ‌نویسی یکپارچه پروژه استفاده می‌کنند:
                </p>
                <pre dir="ltr"><code># هر سرویس لاگ‌های خود را دارد
logger = logging.getLogger('accounts.services.auth')
security_logger = logging.getLogger('accounts.services.security')</code></pre>
                <h3>سطح‌های لاگ‌نویسی</h3>
                <ul>
                    <li><strong>DEBUG:</strong> اطلاعات جزئی برای توسعه‌دهندگان</li>
                    <li><strong>INFO:</strong> اطلاعات کلی درباره عملیات‌ها</li>
                    <li><strong>WARNING:</strong> هشدارها و عملیات مشکوک</li>
                    <li><strong>ERROR:</strong> خطاها و استثناها</li>
                </ul>     
                <p>
                    همچنین لاگ‌های امنیتی در فایل‌های جداگانه‌ای ثبت می‌شوند.
                </p>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>