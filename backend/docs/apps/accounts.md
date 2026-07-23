# مستندات اپلیکیشن Accounts

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌ها](#مدل‌ها)
4. [سرویس‌ها](#سرویس‌ها)
5. [وظایف Celery](#وظایف-celery)
6. [API Views](#api-views)
7. [Serializers](#serializers)
8. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن accounts مسئول تمام فرآیندهای مربوط به احراز هویت و حساب کاربری است. این اپلیکیشن از امنیت بالا برخوردار است و تمام عملیات مربوط به ورود، ثبت‌نام، تأیید ایمیل و بازنشانی رمز عبور را مدیریت می‌کند.

---

## ساختار فایل‌ها

```
accounts/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── managers.py              # منیجرهای سفارشی
├── exceptions.py            # Exceptionهای سفارشی
├── signals.py               # سیگنال‌های Django
├── middleware.py            # AutoLoginSuperuserMiddleware
├── migrations/              # مهاجرت‌های دیتابیس
├── services/                # لایه سرویس‌ها
│   ├── __init__.py
│   ├── auth_service.py      # سرویس احراز هویت
│   ├── password_reset_service.py  # سرویس بازنشانی رمز
│   ├── verify_service.py    # سرویس تأیید ایمیل
│   └── wallet_service.py    # سرویس کیف پول
├── tasks/                   # وظایف Celery
│   ├── __init__.py
│   └── emails.py            # وظایف ارسال ایمیل
├── templates/               # قالب‌های ایمیل
│   └── accounts/
│       ├── email_verification.html
│       └── password_reset.html
└── tests/                   # تست‌ها
```

---

## مدل‌ها

### 📍 موقعیت: `backend/apps/accounts/models.py`

### توضیحات:
این فایل شامل مدل‌های مربوط به احراز هویت و حساب کاربری است. البته مدل اصلی User در `core/users/models.py` تعریف شده است.

**نکته مهم**: اپلیکیشن accounts از مدل `core.User` استفاده می‌کند نه مدل پیش‌فرض Django.

---

## managers.py

### 📍 موقعیت: `backend/apps/accounts/managers.py`

### توضیحات:
منیجرهای سفارشی برای مدل‌های accounts.

**منیجرهای اصلی:**
- `UserManager`: مدیریت کاربران (در core.users.managers.users)
- `AddressManager`: مدیریت آدرس‌ها (در core.users.managers.address)

---

## exceptions.py

### 📍 موقعیت: `backend/apps/accounts/exceptions.py`

### توضیحات:
Exceptionهای سفارشی برای اپلیکیشن accounts.

**Exceptionهای اصلی:**
```python
class AuthenticationError(Exception):
    """خطا در احراز هویت"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """نام کاربری یا رمز عبور اشتباه"""
    pass

class AccountNotVerifiedError(AuthenticationError):
    """حساب کاربری تأیید نشده"""
    pass

class TokenExpiredError(AuthenticationError):
    """توکن منقضی شده"""
    pass

class PasswordResetError(Exception):
    """خطا در بازنشانی رمز عبور"""
    pass

class EmailVerificationError(Exception):
    """خطا در تأیید ایمیل"""
    pass
```

---

## signals.py

### 📍 موقعیت: `backend/apps/accounts/signals.py`

### توضیحات:
سیگنال‌های Django برای اجرای کد در رویدادهای خاص.

**سیگنال‌های اصلی:**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.users.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ایجاد خودکار پروفایل برای کاربران جدید"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """ایجاد خودکار کیف پول برای کاربران جدید"""
    if created:
        Wallet.objects.create(user=instance)
```

---

## middleware.py

### 📍 موقعیت: `backend/apps/accounts/middleware.py`

### توضیحات:
میان‌افزار سفارشی برای ورود خودکار ادمین در حالت دیباگ.

**AutoLoginSuperuserMiddleware:**
```python
class AutoLoginSuperuserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # در حالت دیباگ، اگر ادمین وارد نشده باشد، خودکار وارد می‌شود
        if settings.DEBUG and not request.user.is_authenticated:
            try:
                admin = User.objects.filter(is_superuser=True).first()
                if admin:
                    from django.contrib.auth import login
                    login(request, admin)
            except Exception:
                pass
        
        return self.get_response(request)
```

**نکته**: این middleware فقط در حالت DEBUG فعال است.

---

## services/

### 📍 موقعیت: `backend/apps/accounts/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن accounts که شامل منطق تجاری مربوط به احراز هویت است.

---

### auth_service.py

#### 📍 موقعیت: `backend/apps/accounts/services/auth_service.py`

#### هدف:
مدیریت فرآیندهای ورود، ثبت‌نام و خروج از حساب کاربری.

#### کلاس اصلی: `AuthService`

**متدهای اصلی:**

```python
class AuthService:
    def login(self, username: str, password: str) -> dict:
        """
        ورود به حساب کاربری
        
        Args:
            username: نام کاربری
            password: رمز عبور
        
        Returns:
            dict: {
                'access': 'access_token',
                'refresh': 'refresh_token',
                'user': User instance
            }
        
        Raises:
            InvalidCredentialsError: اگر نام کاربری یا رمز عبور اشتباه باشد
            AccountNotVerifiedError: اگر حساب تأیید نشده باشد
        """
        pass
    
    def register(self, user_data: dict) -> User:
        """
        ثبت‌نام کاربر جدید
        
        Args:
            user_data: {
                'username': str,
                'email': str,
                'password': str,
                'first_name': str,
                'last_name': str
            }
        
        Returns:
            User: کاربر جدید ایجاد شده
        
        Raises:
            ValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def logout(self, token: str) -> bool:
        """
        خروج از حساب و بلاک‌لیست توکن
        
        Args:
            token: توکن دسترسی
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def refresh_token(self, refresh_token: str) -> dict:
        """
        تمدید توکن دسترسی
        
        Args:
            refresh_token: توکن تمدید
        
        Returns:
            dict: {
                'access': 'new_access_token'
            }
        
        Raises:
            TokenExpiredError: اگر توکن منقضی شده باشد
        """
        pass
```

**مثال استفاده:**
```python
from apps.accounts.services.auth_service import AuthService

auth_service = AuthService()

# ورود
result = auth_service.login(username="user", password="pass")
access_token = result['access']
user = result['user']

# ثبت‌نام
new_user = auth_service.register({
    'username': 'newuser',
    'email': 'user@example.com',
    'password': 'secure123',
    'first_name': 'علی',
    'last_name': 'محمدی'
})

# خروج
auth_service.logout(access_token)

# تمدید توکن
new_tokens = auth_service.refresh_token(refresh_token)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('accounts.services.auth')
```

---

### password_reset_service.py

#### 📍 موقعیت: `backend/apps/accounts/services/password_reset_service.py`

#### هدف:
مدیریت فرآیند بازنشانی رمز عبور.

#### کلاس اصلی: `PasswordResetService`

**متدهای اصلی:**

```python
class PasswordResetService:
    def request_reset(self, email: str) -> bool:
        """
        درخواست بازنشانی رمز عبور
        
        Args:
            email: ایمیل کاربر
        
        Returns:
            bool: آیا ایمیل ارسال شد
        
        Raises:
            UserNotFoundError: اگر کاربری با این ایمیل وجود نداشته باشد
        """
        pass
    
    def confirm_reset(self, token: str, new_password: str) -> bool:
        """
        تأیید و بازنشانی رمز عبور
        
        Args:
            token: توکن بازنشانی
            new_password: رمز عبور جدید
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            InvalidTokenError: اگر توکن نامعتبر باشد
            TokenExpiredError: اگر توکن منقضی شده باشد
        """
        pass
```

**فرآیند بازنشانی رمز:**
```
1. User → POST /api/v1/accounts/password-reset/
   {email: "user@example.com"}

2. PasswordResetService.request_reset(email)
   - پیدا کردن کاربر با ایمیل
   - تولید توکن بازنشانی
   - ارسال ایمیل با لینک بازنشانی (Celery Task)

3. User کلیک روی لینک در ایمیل
   → /reset-password/{token}

4. User → POST /api/v1/accounts/password-reset/confirm/
   {token: "...", new_password: "..."}

5. PasswordResetService.confirm_reset(token, new_password)
   - بررسی اعتبار توکن
   - بروزرسانی رمز عبور
   - بلاک‌لیست توکن
```

**مثال استفاده:**
```python
from apps.accounts.services.password_reset_service import PasswordResetService

reset_service = PasswordResetService()

# درخواست بازنشانی
reset_service.request_reset(email="user@example.com")

# تأیید بازنشانی
reset_service.confirm_reset(
    token="abc123...",
    new_password="new_secure_password"
)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('accounts.services.password_reset')
```

---

### verify_service.py

#### 📍 موقعیت: `backend/apps/accounts/services/verify_service.py`

#### هدف:
مدیریت تأیید ایمیل کاربران.

#### کلاس اصلی: `VerifyService`

**متدهای اصلی:**

```python
class VerifyService:
    def send_verification_email(self, user: User) -> bool:
        """
        ارسال ایمیل تأیید
        
        Args:
            user: کاربر
        
        Returns:
            bool: آیا ایمیل ارسال شد
        """
        pass
    
    def verify_email(self, token: str) -> bool:
        """
        تأیید ایمیل با توکن
        
        Args:
            token: توکن تأیید
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            InvalidTokenError: اگر توکن نامعتبر باشد
            TokenExpiredError: اگر توکن منقضی شده باشد
        """
        pass
```

**فرآیند تأیید ایمیل:**
```
1. User → POST /api/v1/accounts/register/
   {username, email, password, ...}

2. AuthService.register()
   - ایجاد کاربر (is_active=True, email_verified=False)
   - فراخوانی VerifyService.send_verification_email()

3. VerifyService.send_verification_email(user)
   - تولید توکن تأیید
   - ارسال ایمیل با لینک تأیید (Celery Task)

4. User کلیک روی لینک در ایمیل
   → /verify-email/{token}

5. User → POST /api/v1/accounts/verify-email/
   {token: "..."}

6. VerifyService.verify_email(token)
   - بررسی اعتبار توکن
   - بروزرسانی email_verified=True
```

**مثال استفاده:**
```python
from apps.accounts.services.verify_service import VerifyService

verify_service = VerifyService()

# ارسال ایمیل تأیید
verify_service.send_verification_email(user)

# تأیید ایمیل
verify_service.verify_email(token="abc123...")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('accounts.services.verification')
```

---

### wallet_service.py

#### 📍 موقعیت: `backend/apps/accounts/services/wallet_service.py`

#### هدف:
مدیریت کیف پول الکترونیکی کاربران.

#### کلاس اصلی: `WalletService`

**متدهای اصلی:**

```python
class WalletService:
    def get_balance(self, user: User) -> Decimal:
        """
        دریافت موجودی کیف پول
        
        Args:
            user: کاربر
        
        Returns:
            Decimal: موجودی
        """
        pass
    
    def add_transaction(self, user: User, amount: Decimal, 
                       type: str, description: str) -> Transaction:
        """
        افزودن تراکنش جدید
        
        Args:
            user: کاربر
            amount: مبلغ
            type: نوع تراکنش (deposit, withdraw, purchase, refund)
            description: توضیحات
        
        Returns:
            Transaction: تراکنش ایجاد شده
        """
        pass
    
    def get_transactions(self, user: User, 
                        page: int = 1, 
                        page_size: int = 20) -> PaginatedResponse:
        """
        دریافت لیست تراکنش‌ها
        
        Args:
            user: کاربر
            page: شماره صفحه
            page_size: تعداد آیتم در هر صفحه
        
        Returns:
            PaginatedResponse: لیست تراکنش‌ها
        """
        pass
```

**مثال استفاده:**
```python
from apps.accounts.services.wallet_service import WalletService
from decimal import Decimal

wallet_service = WalletService()

# دریافت موجودی
balance = wallet_service.get_balance(user)
print(f"موجودی: {balance} تومان")

# افزودن تراکنش
transaction = wallet_service.add_transaction(
    user=user,
    amount=Decimal('100000'),
    type='deposit',
    description='واریز از طریق درگاه پرداخت'
)

# دریافت لیست تراکنش‌ها
transactions = wallet_service.get_transactions(user, page=1, page_size=20)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('accounts.services.wallet')
```

---

## tasks/

### 📍 موقعیت: `backend/apps/accounts/tasks/`

### توضیحات:
وظایف ناهمزمان (Celery Tasks) برای عملیات زمان‌بر.

---

### emails.py

#### 📍 موقعیت: `backend/apps/accounts/tasks/emails.py`

#### هدف:
وظایف Celery برای ارسال ایمیل‌های مختلف.

**وظایف اصلی:**

```python
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def send_verification_email_task(user_id: int) -> bool:
    """
    وظیفه ناهمزمان ارسال ایمیل تأیید حساب
    
    Args:
        user_id: ID کاربر
    
    Returns:
        bool: موفقیت‌آمیز بودن ارسال
    """
    pass

@shared_task
def send_password_reset_email_task(user_id: int) -> bool:
    """
    وظیفه ناهمزمان ارسال ایمیل بازنشانی رمز عبور
    
    Args:
        user_id: ID کاربر
    
    Returns:
        bool: موفقیت‌آمیز بودن ارسال
    """
    pass
```

**مثال استفاده:**
```python
# فراخوانی وظیفه
from apps.accounts.tasks.emails import send_verification_email_task

# ارسال به صورت ناهمزمان
send_verification_email_task.delay(user_id=123)

# یا ارسال همزمان (برای تست)
result = send_verification_email_task(user_id=123)
```

**قالب‌های ایمیل:**
```
templates/accounts/
├── email_verification.html    # قالب ایمیل تأیید
└── password_reset.html        # قالب ایمیل بازنشانی
```

**مثال قالب email_verification.html:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>تأیید ایمیل - Printoo24</title>
</head>
<body>
    <h1>به Printoo24 خوش آمدید!</h1>
    <p>برای تأیید ایمیل خود، روی لینک زیر کلیک کنید:</p>
    <a href="{{ verification_url }}">تأیید ایمیل</a>
    <p>اگر درخواست این ایمیل را نکرده‌اید، آن را نادیده بگیرید.</p>
</body>
</html>
```

---

## API Views

### 📍 موقعیت: `backend/api/v1/accounts/views/`

### توضیحات:
Viewهای API برای احراز هویت.

---

### login_register_view.py

#### 📍 موقعیت: `backend/api/v1/accounts/views/login_register_view.py`

#### هدف:
Viewهای مربوط به ورود و ثبت‌نام.

**Viewهای اصلی:**

```python
class LoginView(APIView):
    """
    View ورود به حساب کاربری
    
    POST /api/v1/accounts/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            auth_service = AuthService()
            result = auth_service.login(username, password)
            
            return Response({
                'success': True,
                'access': result['access'],
                'refresh': result['refresh'],
                'user': UserSerializer(result['user']).data
            }, status=status.HTTP_200_OK)
        
        except InvalidCredentialsError:
            return Response({
                'success': False,
                'message': 'نام کاربری یا رمز عبور اشتباه است'
            }, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    """
    View ثبت‌نام کاربر جدید
    
    POST /api/v1/accounts/register/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            auth_service = AuthService()
            user = auth_service.register(serializer.validated_data)
            
            # ارسال ایمیل تأیید
            send_verification_email_task.delay(user.id)
            
            return Response({
                'success': True,
                'message': 'ثبت‌نام با موفقیت انجام شد. ایمیل تأیید ارسال شد.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
```

---

### email_verify_view.py

#### 📍 موقعیت: `backend/api/v1/accounts/views/email_verify_view.py`

#### هدف:
Viewهای مربوط به تأیید ایمیل.

**Viewهای اصلی:**

```python
class VerifyEmailView(APIView):
    """
    View تأیید ایمیل
    
    POST /api/v1/accounts/verify-email/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        try:
            verify_service = VerifyService()
            success = verify_service.verify_email(token)
            
            if success:
                return Response({
                    'success': True,
                    'message': 'ایمیل شما با موفقیت تأیید شد.'
                }, status=status.HTTP_200_OK)
        
        except InvalidTokenError:
            return Response({
                'success': False,
                'message': 'توکن نامعتبر است.'
            }, status=status.HTTP_400_BAD_REQUEST)
```

---

### password_reset_view.py

#### 📍 موقعیت: `backend/api/v1/accounts/views/password_reset_view.py`

#### هدف:
Viewهای مربوط به بازنشانی رمز عبور.

**Viewهای اصلی:**

```python
class PasswordResetRequestView(APIView):
    """
    View درخواست بازنشانی رمز عبور
    
    POST /api/v1/accounts/password-reset/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            reset_service = PasswordResetService()
            reset_service.request_reset(email)
            
            return Response({
                'success': True,
                'message': 'اگر ایمیل وجود داشته باشد، لینک بازنشانی ارسال شده است.'
            }, status=status.HTTP_200_OK)
        
        except UserNotFoundError:
            # برای امنیت، خطا را برمی‌گردانیم حتی اگر کاربر وجود نداشته باشد
            return Response({
                'success': True,
                'message': 'اگر ایمیل وجود داشته باشد، لینک بازنشانی ارسال شده است.'
            }, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    """
    View تأیید بازنشانی رمز عبور
    
    POST /api/v1/accounts/password-reset/confirm/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        try:
            reset_service = PasswordResetService()
            reset_service.confirm_reset(token, new_password)
            
            return Response({
                'success': True,
                'message': 'رمز عبور با موفقیت تغییر کرد.'
            }, status=status.HTTP_200_OK)
        
        except InvalidTokenError:
            return Response({
                'success': False,
                'message': 'توکن نامعتبر است.'
            }, status=status.HTTP_400_BAD_REQUEST)
```

---

### tokens_view.py

#### 📍 موقعیت: `backend/api/v1/accounts/views/tokens_view.py`

#### هدف:
Viewهای مربوط به مدیریت توکن‌های JWT.

**Viewهای اصلی:**

```python
class TokenRefreshView(APIView):
    """
    View تمدید توکن
    
    POST /api/v1/accounts/token/refresh/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        try:
            auth_service = AuthService()
            result = auth_service.refresh_token(refresh_token)
            
            return Response({
                'access': result['access']
            }, status=status.HTTP_200_OK)
        
        except TokenExpiredError:
            return Response({
                'success': False,
                'message': 'توکن منقضی شده است.'
            }, status=status.HTTP_401_UNAUTHORIZED)

class TokenVerifyView(APIView):
    """
    View بررسی اعتبار توکن
    
    POST /api/v1/accounts/token/verify/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        # بررسی اعتبار توکن
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken
        
        try:
            UntypedToken(token)
            return Response({'valid': True}, status=status.HTTP_200_OK)
        except InvalidToken:
            return Response({'valid': False}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    """
    View خروج از حساب
    
    POST /api/v1/accounts/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        token = request.auth
        
        try:
            auth_service = AuthService()
            auth_service.logout(str(token))
            
            return Response({
                'success': True,
                'message': 'با موفقیت خارج شدید.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': 'خطا در خروج از حساب.'
            }, status=status.HTTP_400_BAD_REQUEST)
```

---

## Serializers

### 📍 موقعیت: `backend/api/v1/accounts/serializers/`

### توضیحات:
Serializers برای اعتبارسنجی و تبدیل داده‌های احراز هویت.

---

### login_register_serializer.py

#### 📍 موقعیت: `backend/api/v1/accounts/serializers/login_register_serializer.py`

#### هدف:
Serializers برای ورود و ثبت‌نام.

**Serializerهای اصلی:**

```python
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError('نام کاربری و رمز عبور الزامی است.')
        
        return data

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    phone = serializers.CharField(max_length=15, required=False)
    
    def validate(self, data):
        # بررسی تطابق رمز عبور
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('رمز عبور و تأیید آن مطابقت ندارند.')
        
        # بررسی یکتا بودن username
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('این نام کاربری قبلاً استفاده شده است.')
        
        # بررسی یکتا بودن email
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('این ایمیل قبلاً ثبت شده است.')
        
        return data
    
    def create(self, validated_data):
        # حذف password_confirm از داده‌ها
        validated_data.pop('password_confirm')
        
        # ایجاد کاربر
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', '')
        )
        
        return user
```

---

### email_verify_serializer.py

#### 📍 موقعیت: `backend/api/v1/accounts/serializers/email_verify_serializer.py`

#### هدف:
Serializer برای تأیید ایمیل.

```python
class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    
    def validate_token(self, value):
        # بررسی اعتبار توکن
        try:
            token = Token.objects.get(token=value, type='email_verify')
            if token.is_expired():
                raise serializers.ValidationError('توکن منقضی شده است.')
            return value
        except Token.DoesNotExist:
            raise serializers.ValidationError('توکن نامعتبر است.')
```

---

### password_reset_serializer.py

#### 📍 موقعیت: `backend/api/v1/accounts/serializers/password_reset_serializer.py`

#### هدف:
Serializers برای بازنشانی رمز عبور.

```python
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError('رمز عبور و تأیید آن مطابقت ندارند.')
        return data
```

---

## نکات مهم

### 1. **امنیت**
- ✅ تمام رمزهای عبور با bcrypt هش می‌شوند
- ✅ توکن‌های JWT با SECRET_KEY امضا می‌شوند
- ✅ توکن‌های بلاک‌لیست در دیتابیس ذخیره می‌شوند
- ✅ محدودیت نرخ درخواست برای جلوگیری از حملات Brute Force

### 2. **عملکرد**
- ✅ ایمیل‌ها به صورت ناهمزمان ارسال می‌شوند (Celery)
- ✅ توکن‌های تأیید و بازنشانی با انقضا محدود هستند
- ✅ در حالت دیباگ، ادمین به صورت خودکار وارد سیستم می‌شود

### 3. **لاگ‌گذاری**
```python
logger = logging.getLogger('accounts.services.auth')
logger = logging.getLogger('accounts.services.password_reset')
logger = logging.getLogger('accounts.services.token')
logger = logging.getLogger('accounts.services.verification')
logger = logging.getLogger('accounts.services.security')
```

### 4. **محدودیت‌ها (Throttling)**
- ورود به حساب: 50 درخواست در دقیقه
- ثبت‌نام: 30 درخواست در ساعت
- تأیید حساب: 30 درخواست در دقیقه

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات API](../api/README.md)** - مستندات لایه API
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24