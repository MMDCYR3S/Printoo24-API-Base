# مستندات اپلیکیشن‌های پروژه Printoo24 Backend

## 📋 پیش‌نیاز
- مطالعه [مستندات معماری کلی](../00_architecture_overview.md)
- مطالعه [مستندات تنظیمات پروژه](../settings/README.md)
- مطالعه [مستندات API](../api/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [فهرست اپلیکیشن‌ها](#فهرست-اپلیکیشن‌ها)
3. [Accounts](#accounts)
4. [Shop](#shop)
5. [Cart](#cart)
6. [Order](#order)
7. [UserProfile](#userprofile)
8. [Notification](#notification)
9. [Dashboard](#dashboard)
10. [Blog](#blog)
11. [Home](#home)

---

## مقدمه

اپلیکیشن‌های پروژه Printoo24، هسته اصلی عملکرد سیستم هستند. هر اپلیکیشن مسئولیت مشخصی را بر عهده دارد و از ساختار ماژولار پیروی می‌کند.

### ساختار کلی هر اپلیکیشن:

```
apps/
└── {app_name}/
    ├── __init__.py
    ├── admin.py              # تنظیمات پنل مدیریت Django
    ├── apps.py               # تنظیمات اپلیکیشن
    ├── models.py             # مدل‌های دیتابیس
    ├── managers.py           # منیجرهای سفارشی (در صورت وجود)
    ├── exceptions.py         # Exceptionهای سفارشی (در صورت وجود)
    ├── signals.py            # سیگنال‌های Django (در صورت وجود)
    ├── middleware.py         # میان‌افزار سفارشی (در صورت وجود)
    ├── filters.py            # فیلترهای سفارشی (در صورت وجود)
    ├── tasks.py              # وظایف Celery (در صورت وجود)
    ├── migrations/           # فایل‌های مهاجرت دیتابیس
    ├── services/             # لایه سرویس‌ها (منطق تجاری)
    │   ├── __init__.py
    │   └── *_service.py
    ├── templates/            # قالب‌های HTML (در صورت وجود)
    ├── tests/                # تست‌های unit (در صورت وجود)
    └── utils/                # ابزارهای کمکی (در صورت وجود)
```

### لایه‌بندی درون اپلیکیشن:

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (api/v1/{app}/)                 │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   Views      │  │  Serializers │                         │
│  │  (دریافت    │  │  (اعتبار    │                         │
│  │   درخواست)  │  │   سنجی)     │                         │
│  └──────────────┘  └──────────────┘                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Layer (apps/{app}/)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services (منطق تجاری)                               │  │
│  │  - اعتبارسنجی                                         │  │
│  │  - هماهنگی                                           │  │
│  │  - مدیریت تراکنش                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Layer (core/)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Models    │  │   Managers   │  │   Services   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │     Redis    │  │     Media    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## فهرست اپلیکیشن‌ها

| اپلیکیشن | توضیحات | مستندات |
|---------|---------|---------|
| **accounts** | احراز هویت و حساب کاربری | [accounts.md](./accounts.md) |
| **shop** | مدیریت محصولات و فروشگاه | [shop.md](./shop.md) |
| **cart** | مدیریت سبد خرید | [cart.md](./cart.md) |
| **order** | مدیریت سفارشات | [order.md](./order.md) |
| **userprofile** | پروفایل و اطلاعات کاربران | [userprofile.md](./userprofile.md) |
| **notification** | سیستم اعلان‌ها | [notification.md](./notification.md) |
| **dashboard** | داشبورد مدیریت | [dashboard.md](./dashboard.md) |
| **blog** | وبلاگ | [blog.md](./blog.md) |
| **home** | صفحه اصلی | [home.md](./home.md) |

---

## Accounts

### 📍 موقعیت: `backend/apps/accounts/`

### 🎯 هدف:
اپلیکیشن accounts مسئول تمام فرآیندهای مربوط به احراز هویت و حساب کاربری است.

### وظایف اصلی:
- ✅ ثبت‌نام کاربران جدید
- ✅ ورود و خروج از حساب
- ✅ تأیید ایمیل
- ✅ بازنشانی رمز عبور
- ✅ مدیریت توکن‌های JWT
- ✅ ارسال ایمیل‌های مربوط به حساب کاربری

### ساختار:

```
accounts/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── managers.py              # منیجرهای سفارشی
├── exceptions.py            # Exceptionهای سفارشی
├── signals.py               # سیگنال‌های post_save و ...
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

### مدل‌های اصلی:

#### 1. **User** (از core.users.models)
- مدل اصلی کاربر
- فیلدهای: username، email، phone، first_name، last_name
- نقش‌ها: customer، staff، admin

### سرویس‌های اصلی:

#### 1. **AuthService** (`services/auth_service.py`)
**وظایف:**
- ورود به حساب (Login)
- ثبت‌نام (Register)
- خروج از حساب (Logout)
- تولید و مدیریت توکن‌های JWT

**متدهای اصلی:**
```python
class AuthService:
    def login(self, username, password) -> dict
    def register(self, user_data) -> User
    def logout(self, token) -> bool
    def refresh_token(self, refresh_token) -> dict
```

#### 2. **PasswordResetService** (`services/password_reset_service.py`)
**وظایف:**
- درخواست بازنشانی رمز عبور
- تأیید و بازنشانی رمز

**متدهای اصلی:**
```python
class PasswordResetService:
    def request_reset(self, email) -> bool
    def confirm_reset(self, token, new_password) -> bool
```

#### 3. **VerifyService** (`services/verify_service.py`)
**وظایف:**
- ارسال ایمیل تأیید
- تأیید ایمیل با توکن

**متدهای اصلی:**
```python
class VerifyService:
    def send_verification_email(self, user) -> bool
    def verify_email(self, token) -> bool
```

#### 4. **WalletService** (`services/wallet_service.py`)
**وظایف:**
- مدیریت کیف پول کاربر
- ثبت تراکنش‌ها

**متدهای اصلی:**
```python
class WalletService:
    def get_balance(self, user) -> Decimal
    def add_transaction(self, user, amount, type) -> Transaction
```

### وظایف Celery:

#### **emails.py**
```python
# وظایف ناهمزمان ارسال ایمیل
@shared_task
def send_verification_email_task(user_id)
@shared_task
def send_password_reset_email_task(user_id)
```

### API Endpoints:

```
POST   /api/v1/accounts/login/                 # ورود
POST   /api/v1/accounts/register/              # ثبت‌نام
POST   /api/v1/accounts/verify-email/          # تأیید ایمیل
POST   /api/v1/accounts/password-reset/        # درخواست بازنشانی
POST   /api/v1/accounts/password-reset/confirm/ # تأیید بازنشانی
POST   /api/v1/accounts/token/refresh/         # تمدید توکن
POST   /api/v1/accounts/token/verify/          # بررسی توکن
POST   /api/v1/accounts/logout/                # خروج
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('accounts.services.auth')
logger = logging.getLogger('accounts.services.password_reset')
logger = logging.getLogger('accounts.services.token')
logger = logging.getLogger('accounts.services.verification')
logger = logging.getLogger('accounts.services.security')
```

### نکات مهم:
- ✅ تمام ایمیل‌ها از طریق Celery ارسال می‌شوند (ناهمزمان)
- ✅ توکن‌های JWT با Simple JWT مدیریت می‌شوند
- ✅ در حالت دیباگ، ادمین به صورت خودکار وارد سیستم می‌شود (AutoLoginSuperuserMiddleware)
- ✅ لاگ‌های امنیتی برای تشخیص فعالیت‌های مشکوک

---

## Shop

### 📍 موقعیت: `backend/apps/shop/`

### 🎯 هدف:
اپلیکیشن shop مسئول مدیریت محصولات، دسته‌بندی‌ها و عملیات مربوط به فروشگاه است.

### وظایف اصلی:
- ✅ نمایش لیست محصولات
- ✅ نمایش جزئیات محصول
- ✅ فیلتر و جستجوی محصولات
- ✅ محاسبه قیمت نهایی
- ✅ مدیریت دسته‌بندی‌ها
- ✅ مدیریت کامنت‌ها و امتیازات

### ساختار:

```
shop/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── filters.py               # فیلترهای سفارشی
├── tasks.py                 # وظایف Celery
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    ├── __init__.py
    ├── product_list_service.py      # لیست محصولات
    ├── product_detail_service.py    # جزئیات محصول
    ├── product_category_service.py  # دسته‌بندی‌ها
    └── product_comment_service.py   # کامنت‌ها
```

### مدل‌های اصلی:

#### 1. **Product** (از core.product.models)
- نام، توضیحات، قیمت پایه
- تصاویر، فایل‌های پیوست
- ویژگی‌های داینامیک
- فرمول‌های قیمت‌گذاری

#### 2. **Category**
- نام دسته‌بندی
- والد و فرزند (سلسله مراتبی)

#### 3. **ProductComment**
- کاربر، محصول، متن نظر
- امتیاز، تاریخ

### سرویس‌های اصلی:

#### 1. **ProductListService** (`services/product_list_service.py`)
**وظایف:**
- دریافت لیست محصولات با فیلتر
- پاگینیشن
- جستجو و مرتب‌سازی

**متدهای اصلی:**
```python
class ProductListService:
    def get_products(self, filters, page, page_size) -> PaginatedResponse
    def search_products(self, query) -> QuerySet
```

#### 2. **ProductDetailService** (`services/product_detail_service.py`)
**وظایف:**
- دریافت جزئیات کامل محصول
- محاسبه قیمت نهایی با ویژگی‌های انتخابی

**متدهای اصلی:**
```python
class ProductDetailService:
    def get_product(self, product_id) -> Product
    def calculate_price(self, product, selected_options) -> Decimal
```

#### 3. **ProductCategoryService** (`services/product_category_service.py`)
**وظایف:**
- مدیریت دسته‌بندی‌ها
- دریافت لیست سلسله‌مراتبی

**متدهای اصلی:**
```python
class ProductCategoryService:
    def get_categories(self) -> QuerySet
    def get_category_tree(self) -> dict
```

#### 4. **ProductCommentService** (`services/product_comment_service.py`)
**وظایف:**
- ایجاد کامنت جدید
- دریافت کامنت‌های محصول

**متدهای اصلی:**
```python
class ProductCommentService:
    def create_comment(self, user, product, text, rating) -> Comment
    def get_product_comments(self, product_id) -> QuerySet
```

### API Endpoints:

```
GET    /api/v1/shop/products/              # لیست محصولات
GET    /api/v1/shop/products/{id}/         # جزئیات محصول
GET    /api/v1/shop/categories/            # لیست دسته‌بندی‌ها
GET    /api/v1/shop/categories/{id}/       # جزئیات دسته‌بندی
POST   /api/v1/shop/comments/              # ارسال نظر
GET    /api/v1/shop/comments/{id}/         # جزئیات نظر
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('shop.services.product_list')
logger = logging.getLogger('shop.services.product_detail')
logger = logging.getLogger('shop.services.price_calculator')
logger = logging.getLogger('shop.services.order_creation')
logger = logging.getLogger('shop.services.feedback')
```

### نکات مهم:
- ✅ قیمت‌گذاری پیچیده با استفاده از Calculator Service
- ✅ فیلترهای پیشرفته با django-filter
- ✅ محاسبه قیمت بر اساس ویژگی‌های انتخابی
- ✅ پشتیبانی از محصولات با ویژگی‌های داینامیک

---

## Cart

### 📍 موقعیت: `backend/apps/cart/`

### 🎯 هدف:
اپلیکیشن cart مسئول مدیریت سبد خرید کاربران است.

### وظایف اصلی:
- ✅ افزودن محصول به سبد خرید
- ✅ بروزرسانی تعداد محصولات
- ✅ حذف محصول از سبد خرید
- ✅ مشاهده سبد خرید
- ✅ اعتبارسنجی سبد خرید
- ✅ مدیریت فایل‌های آپلودی

### ساختار:

```
cart/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── managers.py              # منیجرهای سفارشی
├── exceptions.py            # Exceptionهای سفارشی
├── migrations/              # مهاجرت‌های دیتابیس
├── services/                # لایه سرویس‌ها
│   ├── __init__.py
│   ├── add_to_cart_service.py       # افزودن به سبد
│   ├── cart_item_service.py         # مدیریت آیتم‌ها
│   ├── cart_item_upload_service.py  # آپلود فایل
│   ├── cart_validator_service.py    # اعتبارسنجی
│   ├── delete_cart_service.py       # حذف از سبد
│   └── update_cart_service.py       # بروزرسانی
└── utils/                   # ابزارهای کمکی
```

### مدل‌های اصلی:

#### 1. **Cart**
- کاربر
- تاریخ ایجاد
- وضعیت (فعال، تبدیل به سفارش، ...)

#### 2. **CartItem**
- سبد خرید
- محصول
- تعداد
- ویژگی‌های انتخابی
- فایل‌های آپلودی
- قیمت در زمان افزودن

### سرویس‌های اصلی:

#### 1. **AddToCartService** (`services/add_to_cart_service.py`)
**وظایف:**
- افزودن محصول به سبد خرید
- بررسی موجودی
- اعتبارسنجی داده‌ها

**متدهای اصلی:**
```python
class AddToCartService:
    def add_item(self, user, product_id, quantity, options) -> CartItem
```

#### 2. **CartItemService** (`services/cart_item_service.py`)
**وظایف:**
- مدیریت آیتم‌های سبد خرید
- مشاهده جزئیات

**متدهای اصلی:**
```python
class CartItemService:
    def get_cart_items(self, user) -> QuerySet
    def get_cart_item(self, item_id) -> CartItem
```

#### 3. **CartItemUploadService** (`services/cart_item_upload_service.py`)
**وظایف:**
- آپلود فایل‌های مرتبط با آیتم سبد خرید
- مدیریت فایل‌های موقت

**متدهای اصلی:**
```python
class CartItemUploadService:
    def upload_file(self, cart_item, file) -> str
    def delete_file(self, file_path) -> bool
```

#### 4. **CartValidatorService** (`services/cart_validator_service.py`)
**وظایف:**
- اعتبارسنجی سبد خرید قبل از تبدیل به سفارش
- بررسی موجودی
- بررسی قیمت‌ها

**متدهای اصلی:**
```python
class CartValidatorService:
    def validate_cart(self, user) -> ValidationResult
    def check_stock(self, cart_items) -> bool
```

#### 5. **DeleteCartService** (`services/delete_cart_service.py`)
**وظایف:**
- حذف آیتم از سبد خرید
- پاک کردن کامل سبد خرید

**متدهای اصلی:**
```python
class DeleteCartService:
    def remove_item(self, user, item_id) -> bool
    def clear_cart(self, user) -> bool
```

#### 6. **UpdateCartService** (`services/update_cart_service.py`)
**وظایف:**
- بروزرسانی تعداد آیتم
- تغییر ویژگی‌های انتخابی

**متدهای اصلی:**
```python
class UpdateCartService:
    def update_quantity(self, user, item_id, quantity) -> CartItem
    def update_options(self, user, item_id, options) -> CartItem
```

### API Endpoints:

```
GET    /api/v1/cart/                      # مشاهده سبد خرید
POST   /api/v1/cart/add/                  # افزودن به سبد
PUT    /api/v1/cart/update/{id}/          # بروزرسانی تعداد
DELETE /api/v1/cart/remove/{id}/          # حذف از سبد
DELETE /api/v1/cart/clear/                # پاک کردن سبد
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('cart.services.add_to_cart')
logger = logging.getLogger('cart.services.cart_file')
logger = logging.getLogger('cart.services.list')
logger = logging.getLogger('cart.services.detail')
logger = logging.getLogger('cart.services.delete')
logger = logging.getLogger('cart.services.temp_file')
logger = logging.getLogger('cart.services.cart_validator')
logger = logging.getLogger('cart.services.update')
logger = logging.getLogger('cart.services.file_upload')
```

### نکات مهم:
- ✅ هر کاربر می‌تواند فقط یک سبد خرید فعال داشته باشد
- ✅ فایل‌های آپلودی در پوشه موقت ذخیره می‌شوند
- ✅ قبل از تبدیل به سفارش، سبد خرید اعتبارسنجی می‌شود
- ✅ قیمت محصول در زمان افزودن به سبد ذخیره می‌شود (برای جلوگیری از تغییرات قیمت)

---

## Order

### 📍 موقعیت: `backend/apps/order/`

### 🎯 هدف:
اپلیکیشن order مسئول مدیریت کامل فرآیند سفارش‌گیری است.

### وظایف اصلی:
- ✅ ایجاد سفارش از سبد خرید
- ✅ مدیریت وضعیت سفارش
- ✅ لغو سفارش
- ✅ تاریخچه سفارشات
- ✅ محاسبه قیمت نهایی

### ساختار:

```
order/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── domain_services.py       # سرویس‌های دامنه
├── exceptions.py            # Exceptionهای سفارشی
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    └── __init__.py
        └── order_create_service.py   # ایجاد سفارش
```

### مدل‌های اصلی:

#### 1. **Order**
- کاربر
- کد سفارش (یکتا)
- وضعیت (در انتظار، پرداخت شده، ارسال شده، ...)
- قیمت کل
- آدرس ارسال
- تاریخ ایجاد

#### 2. **OrderItem**
- سفارش
- محصول
- تعداد
- قیمت واحد
- ویژگی‌های انتخابی

#### 3. **OrderStatus**
- سفارش
- وضعیت
- تاریخ تغییر
- توضیحات

### سرویس‌های اصلی:

#### 1. **OrderCreateService** (`services/order_create_service.py`)
**وظایف:**
- ایجاد سفارش از سبد خرید
- اعتبارسنجی سبد خرید
- محاسبه قیمت نهایی
- کم کردن موجودی انبار
- پاک کردن سبد خرید

**متدهای اصلی:**
```python
class OrderCreateService:
    def create_order(self, user, address_id) -> Order
    def calculate_total(self, cart_items) -> Decimal
    def reduce_stock(self, order_items) -> bool
```

### API Endpoints:

```
POST   /api/v1/order/create/         # ایجاد سفارش
GET    /api/v1/order/list/           # لیست سفارشات
GET    /api/v1/order/detail/{id}/    # جزئیات سفارش
POST   /api/v1/order/cancel/{id}/    # لغو سفارش
```

### فرآیند ایجاد سفارش:

```
1. Client → POST /api/v1/order/create/
2. اعتبارسنجی آدرس ارسال
3. دریافت سبد خرید کاربر
4. اعتبارسنجی سبد خرید (CartValidatorService)
5. محاسبه قیمت نهایی
6. شروع تراکنش دیتابیس (atomic)
7. ایجاد رکورد Order
8. ایجاد رکوردهای OrderItem
9. کم کردن موجودی انبار (Product Manager)
10. پاک کردن سبد خرید
11. ارسال اعلان به کاربر (Notification Service)
12. ثبت لاگ
13. پایان تراکنش
14. برگرداندن Response
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('shop.services.order_creation')
```

### نکات مهم:
- ✅ تمام عملیات در یک تراکنش atomic انجام می‌شود
- ✅ در صورت خطا، همه چیز rollback می‌شود
- ✅ موجودی انبار به صورت خودکار کم می‌شود
- ✅ پس از ایجاد سفارش، سبد خرید پاک می‌شود

---

## UserProfile

### 📍 موقعیت: `backend/apps/userprofile/`

### 🎯 هدف:
اپلیکیشن userprofile مسئول مدیریت پروفایل و اطلاعات کاربران است.

### وظایف اصلی:
- ✅ مشاهده و بروزرسانی پروفایل
- ✅ مدیریت آدرس‌ها
- ✅ مشاهده تاریخچه سفارشات
- ✅ مدیریت کیف پول
- ✅ ارسال فیدبک

### ساختار:

```
userprofile/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    ├── __init__.py
    ├── user_address_service.py      # مدیریت آدرس
    ├── user_detail_service.py       # جزئیات پروفایل
    ├── user_feedback_service.py     # فیدبک
    ├── user_order_service.py        # سفارشات کاربر
    └── user_transaction_service.py  # تراکنش‌های مالی
```

### مدل‌های اصلی:

#### 1. **UserProfile** (از core.users.models)
- کاربر
- تصویر پروفایل
- تاریخ تولد
- بیوگرافی

#### 2. **Address**
- کاربر
- عنوان
- آدرس کامل
- کد پستی
- شهر
- شماره تماس
- آدرس پیش‌فرض

#### 3. **Wallet**
- کاربر
- موجودی
- تاریخ ایجاد

#### 4. **Transaction**
- کیف پول
- مبلغ
- نوع (واریز، برداشت، خرید)
- توضیحات
- تاریخ

### سرویس‌های اصلی:

#### 1. **UserAddressService** (`services/user_address_service.py`)
**وظایف:**
- افزودن آدرس جدید
- بروزرسانی آدرس
- حذف آدرس
- دریافت لیست آدرس‌ها

**متدهای اصلی:**
```python
class UserAddressService:
    def add_address(self, user, address_data) -> Address
    def update_address(self, user, address_id, address_data) -> Address
    def delete_address(self, user, address_id) -> bool
    def get_addresses(self, user) -> QuerySet
    def set_default_address(self, user, address_id) -> bool
```

#### 2. **UserDetailService** (`services/user_detail_service.py`)
**وظایف:**
- مشاهده پروفایل
- بروزرسانی پروفایل
- آپلود تصویر پروفایل

**متدهای اصلی:**
```python
class UserDetailService:
    def get_profile(self, user) -> UserProfile
    def update_profile(self, user, profile_data) -> UserProfile
    def upload_avatar(self, user, image_file) -> str
```

#### 3. **UserFeedbackService** (`services/user_feedback_service.py`)
**وظایف:**
- ارسال فیدبک
- مشاهده فیدبک‌های کاربر

**متدهای اصلی:**
```python
class UserFeedbackService:
    def create_feedback(self, user, text, rating) -> Feedback
    def get_user_feedbacks(self, user) -> QuerySet
```

#### 4. **UserOrderService** (`services/user_order_service.py`)
**وظایف:**
- مشاهده تاریخچه سفارشات
- مشاهده جزئیات سفارش

**متدهای اصلی:**
```python
class UserOrderService:
    def get_orders(self, user, page, page_size) -> PaginatedResponse
    def get_order_detail(self, user, order_id) -> Order
```

#### 5. **UserTransactionService** (`services/user_transaction_service.py`)
**وظایف:**
- مشاهده تراکنش‌های مالی
- مشاهده موجودی کیف پول

**متدهای اصلی:**
```python
class UserTransactionService:
    def get_wallet_balance(self, user) -> Decimal
    def get_transactions(self, user, page, page_size) -> PaginatedResponse
    def add_transaction(self, user, amount, type, description) -> Transaction
```

### API Endpoints:

```
GET    /api/v1/userprofile/profile/           # مشاهده پروفایل
PUT    /api/v1/userprofile/profile/           # بروزرسانی پروفایل
POST   /api/v1/userprofile/address/           # افزودن آدرس
GET    /api/v1/userprofile/addresses/         # لیست آدرس‌ها
PUT    /api/v1/userprofile/address/{id}/      # بروزرسانی آدرس
DELETE /api/v1/userprofile/address/{id}/      # حذف آدرس
GET    /api/v1/userprofile/orders/            # تاریخچه سفارشات
GET    /api/v1/userprofile/wallet/            # اطلاعات کیف پول
POST   /api/v1/userprofile/feedback/          # ارسال فیدبک
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('userprofile.services.address')
logger = logging.getLogger('userprofile.services.profile')
logger = logging.getLogger('userprofile.services.orders')
logger = logging.getLogger('userprofile.services.wallet')
logger = logging.getLogger('userprofile.services.notification')
```

### نکات مهم:
- ✅ هر کاربر می‌تواند چند آدرس داشته باشد
- ✅ فقط یک آدرس می‌تواند پیش‌فرض باشد
- ✅ تصویر پروفایل در پوشه media ذخیره می‌شود
- ✅ تراکنش‌های مالی فقط توسط ادمین قابل تغییر هستند

---

## Notification

### 📍 موقعیت: `backend/apps/notification/`

### 🎯 هدف:
اپلیکیشن notification مسئول سیستم اعلان‌ها و پیام‌های کاربران است.

### وظایف اصلی:
- ✅ ارسال اعلان به کاربران
- ✅ مشاهده لیست اعلان‌ها
- ✅ علامت‌گذاری اعلان به عنوان خوانده شده
- ✅ حذف اعلان

### ساختار:

```
notification/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── managers.py              # منیجرهای سفارشی
├── signals.py               # سیگنال‌ها
├── tasks.py                 # وظایف Celery
├── domain_services.py       # سرویس‌های دامنه
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    └── __init__.py
        └── customer_notification_service.py  # سرویس اعلان
```

### مدل‌های اصلی:

#### 1. **Notification**
- کاربر
- عنوان
- متن
- نوع (اطلاعیه، هشدار، موفقیت، خطا)
- خوانده شده / نخوانده شده
- تاریخ ایجاد
- تاریخ خواندن

### سرویس‌های اصلی:

#### 1. **CustomerNotificationService** (`services/customer_notification_service.py`)
**وظایف:**
- ارسال اعلان به کاربر
- دریافت لیست اعلان‌های کاربر
- علامت‌گذاری به عنوان خوانده شده

**متدهای اصلی:**
```python
class CustomerNotificationService:
    def send_notification(self, user, title, message, type) -> Notification
    def get_notifications(self, user, unread_only=False) -> QuerySet
    def mark_as_read(self, user, notification_id) -> bool
    def mark_all_as_read(self, user) -> bool
    def delete_notification(self, user, notification_id) -> bool
```

### API Endpoints:

```
GET    /api/v1/notification/notifications/       # لیست اعلان‌ها
POST   /api/v1/notification/notifications/read/  # علامت خوانده شده
DELETE /api/v1/notification/notifications/{id}/  # حذف اعلان
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('userprofile.services.notification')
```

### نکات مهم:
- ✅ اعلان‌ها به صورت real-time و ناهمزمان ارسال می‌شوند
- ✅ از Celery برای ارسال اعلان‌های گروهی استفاده می‌شود
- ✅ اعلان‌ها می‌توانند از طریق ایمیل، SMS یا push notification ارسال شوند

---

## Dashboard

### 📍 موقعیت: `backend/apps/dashboard/`

### 🎯 هدف:
اپلیکیشن dashboard مسئول تمام عملیات مدیریتی و پنل ادمین است.

### وظایف اصلی:
- ✅ مدیریت محصولات (CRUD)
- ✅ مدیریت سفارشات
- ✅ مدیریت کاربران
- ✅ گزارشات و آمار
- ✅ استخراج و ایمپورت محصولات
- ✅ مدیریت محتوا

### ساختار:

```
dashboard/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── tasks.py                 # وظایف Celery
├── migrations/              # مهاجرت‌های دیتابیس
├── services/                # لایه سرویس‌ها
│   ├── __init__.py
│   ├── dashboard_service.py
│   ├── product_service.py
│   ├── product_export_import_service.py
│   ├── order_service.py
│   ├── cart_service.py
│   ├── customer_service.py
│   ├── staff_service.py
│   ├── wallet_service.py
│   ├── content_service.py
│   └── location_service.py
└── templates/               # قالب‌های HTML
```

### سرویس‌های اصلی:

#### 1. **ProductService** (`services/product_service.py`)
**وظایف:**
- ایجاد محصول
- بروزرسانی محصول
- حذف محصول
- مدیریت ویژگی‌های داینامیک

#### 2. **ProductExportImportService** (`services/product_export_import_service.py`)
**وظایف:**
- استخراج محصولات به Excel
- ایمپورت محصولات از Excel
- دانلود فایل نمونه

**ویژگی‌ها:**
- ✅ استخراج کامل با عکس‌ها، فیلدها و فرمول‌ها
- ✅ ایمپورت با اعتبارسنجی
- ✅ تراکنش atomic (همه یا هیچ)
- ✅ پردازش ناهمزمان با Celery

#### 3. **OrderService** (`services/order_service.py`)
**وظایف:**
- مشاهده لیست سفارشات
- تغییر وضعیت سفارش
- لغو سفارش

#### 4. **CustomerService** (`services/customer_service.py`)
**وظایف:**
- مدیریت کاربران
- مشاهده اطلاعات مشتریان
- مسدود کردن/رفع مسدودی کاربر

#### 5. **WalletService** (`services/wallet_service.py`)
**وظایف:**
- مدیریت کیف پول کاربران
- ثبت تراکنش‌های مالی
- گزارش مالی

### API Endpoints:

```
# مدیریت محصولات
GET    /api/v1/dashboard/products/
POST   /api/v1/dashboard/products/
PUT    /api/v1/dashboard/products/{id}/
DELETE /api/v1/dashboard/products/{id}/

# مدیریت سفارشات
GET    /api/v1/dashboard/orders/
PUT    /api/v1/dashboard/orders/{id}/status/

# مدیریت کاربران
GET    /api/v1/dashboard/users/
PUT    /api/v1/dashboard/users/{id}/

# گزارشات
GET    /api/v1/dashboard/reports/sales/
GET    /api/v1/dashboard/reports/customers/

# استخراج و ایمپورت
POST   /api/v1/dashboard/products-export-import/export/
POST   /api/v1/dashboard/products-export-import/import/
GET    /api/v1/dashboard/products-export-import/template/
GET    /api/v1/dashboard/products-export-import/history/
```

### لاگ‌گذاری:
```python
logger = logging.getLogger('dashboard.services.product_dashboard')
logger = logging.getLogger('dashboard.services.cart_dashboard')
logger = logging.getLogger('dashboard.services.customer')
logger = logging.getLogger('dashboard.services.wallet')
logger = logging.getLogger('dashboard.tasks')
```

### نکات مهم:
- ✅ فقط کاربران با نقش staff/admin می‌توانند به این API دسترسی داشته باشند
- ✅ عملیات استخراج و ایمپورت برای محصولات بزرگ، Celery استفاده می‌کنند
- ✅ تمام تغییرات وضعیت سفارش لاگ می‌شود

---

## Blog

### 📍 موقعیت: `backend/apps/blog/`

### 🎯 هدف:
اپلیکیشن blog مسئول مدیریت محتوای وبلاگ است.

### وظایف اصلی:
- ✅ ایجاد و مدیریت پست‌های وبلاگ
- ✅ مشاهده لیست پست‌ها
- ✅ مشاهده جزئیات پست

### ساختار:

```
blog/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── migrations/
└── services/
```

### نکات:
- اپلیکیشن blog در حال حاضر در مراحل اولیه توسعه است
- ساختار پایه ایجاد شده است

---

## Home

### 📍 موقعیت: `backend/apps/home/`

### 🎯 هدف:
اپلیکیشن home مسئول محتوای صفحه اصلی سایت است.

### وظایف اصلی:
- ✅ نمایش بنرها
- ✅ نمایش اسلایدر
- ✅ نمایش محتوای صفحه اصلی

### ساختار:

```
home/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── migrations/
└── services/
```

### نکات:
- اپلیکیشن home در حال حاضر در مراحل اولیه توسعه است
- ساختار پایه ایجاد شده است

---

## 📊 مقایسه اپلیکیشن‌ها

| اپلیکیشن | تعداد سرویس‌ها | تعداد مدل‌ها | پیچیدگی | اولویت |
|---------|---------------|-------------|---------|--------|
| accounts | 4 | 3+ | بالا | بالا |
| shop | 4 | 3+ | بالا | بالا |
| cart | 6 | 2 | متوسط | بالا |
| order | 1 | 3 | متوسط | بالا |
| userprofile | 5 | 4+ | متوسط | متوسط |
| notification | 1 | 1 | پایین | متوسط |
| dashboard | 10+ | 5+ | بالا | بالا |
| blog | - | 1+ | پایین | پایین |
| home | - | 1+ | پایین | پایین |

---

## 🔗 ارتباط بین اپلیکیشن‌ها

```
┌─────────────────────────────────────────────────────────────┐
│                      جریان داده بین اپلیکیشن‌ها              │
└─────────────────────────────────────────────────────────────┘

accounts (احراز هویت)
    ↓
    ├──→ cart (افزودن به سبد خرید نیاز به احراز هویت دارد)
    ├──→ order (ایجاد سفارش نیاز به احراز هویت دارد)
    └──→ userprofile (دسترسی به پروفایل)

shop (محصولات)
    ↓
    ├──→ cart (افزودن محصول به سبد)
    └──→ order (ایجاد سفارش از محصول)

cart (سبد خرید)
    ↓
    └──→ order (تبدیل سبد به سفارش)

order (سفارشات)
    ↓
    ├──→ notification (ارسال اعلان پس از ایجاد سفارش)
    └──→ userprofile (افزودن به تاریخچه سفارشات)

dashboard (مدیریت)
    ↓
    ├──→ shop (مدیریت محصولات)
    ├──→ order (مدیریت سفارشات)
    ├──→ accounts (مدیریت کاربران)
    └──→ notification (ارسال اعلان‌های مدیریتی)
```

---

## 📚 مستندات مرتبط

- **[مستندات معماری کلی](../00_architecture_overview.md)** - پیش‌نیاز این مستند
- **[مستندات تنظیمات پروژه](../settings/README.md)** - پیش‌نیاز این مستند
- **[مستندات API](../api/README.md)** - پیش‌نیاز این مستند
- **[مستندات Core](../core/README.md)** - بعد از این مستند

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24