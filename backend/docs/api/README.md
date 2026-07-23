# مستندات لایه API پروژه Printoo24 Backend

## 📋 پیش‌نیاز
- مطالعه [مستندات معماری کلی](../00_architecture_overview.md)
- مطالعه [مستندات تنظیمات پروژه](../settings/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار کلی API](#ساختار-کلی-api)
3. [نسخه‌بندی API](#نسخه‌بندی-api)
4. [احراز هویت](#احراز-هویت)
5. [Endpointهای اصلی](#endpointهای-اصلی)
6. [مشخصات فنی](#مشخصات-فنی)
7. [مستندات تعاملی](#مستندات-تعاملی)

---

## مقدمه

لایه API پروژه Printoo24، نقطه ورود تمام کلاینت‌ها (وب، موبایل، third-party) به سیستم است. این لایه با استفاده از Django REST Framework پیاده‌سازی شده و از معماری RESTful پیروی می‌کند.

### 🎯 اهداف لایه API:
- ✅ ارائه یک رابط یکپارچه و استاندارد برای کلاینت‌ها
- ✅ نسخه‌بندی برای backward compatibility
- ✅ اعتبارسنجی ورودی‌ها
- ✅ مدیریت احراز هویت و مجوزها
- ✅ مستندسازی خودکار API
- ✅ محدودیت نرخ درخواست (Rate Limiting)

---

## ساختار کلی API

### نمای کلی ساختار:

```
backend/
└── api/
    ├── __init__.py
    ├── urls.py                    # مسیریابی اصلی API
    └── v1/                        # نسخه 1 از API
        ├── __init__.py
        ├── urls.py                # مسیریابی نسخه 1
        ├── accounts/              # API احراز هویت
        │   ├── urls.py
        │   ├── serializers/
        │   │   ├── __init__.py
        │   │   ├── email_verify_serializer.py
        │   │   ├── login_register_serializer.py
        │   │   └── password_reset_serializer.py
        │   └── views/
        │       ├── __init__.py
        │       ├── email_verify_view.py
        │       ├── login_register_view.py
        │       ├── password_reset_view.py
        │       └── tokens_view.py
        ├── shop/                  # API فروشگاه
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── cart/                  # API سبد خرید
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── order/                 # API سفارشات
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── dashboard/             # API داشبورد مدیریت
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── userprofile/           # API پروفایل کاربر
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── notification/          # API اعلان‌ها
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        ├── blog/                  # API وبلاگ
        │   ├── urls.py
        │   ├── serializers/
        │   └── views/
        └── home/                  # API صفحه اصلی
            ├── urls.py
            ├── serializers/
            └── views/
```

### جریان درخواست در لایه API:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Client Request                                           │
│    POST /api/v1/accounts/login/                             │
│    Headers: {Authorization: Bearer <token>}                 │
│    Body: {username: "user", "password": "pass"}             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. URL Routing                                              │
│    backend/urls.py → api/urls.py → api/v1/urls.py          │
│    → accounts/urls.py                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. View (accounts/views/login_register_view.py)             │
│    - دریافت درخواست                                          │
│    - فراخوانی Serializer                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Serializer (accounts/serializers/login_register_serializer)│
│    - اعتبارسنجی داده‌های ورودی                               │
│    - تبدیل داده‌ها به فرمت قابل قبول                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Service Layer (apps/accounts/services/auth_service.py)   │
│    - منطق تجاری                                              │
│    - فراخوانی سرویس‌های دیگر                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Response                                                 │
│    - فرمت JSON                                               │
│    - کد وضعیت HTTP                                           │
│    - Headers مناسب                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## نسخه‌بندی API

### استراتژی نسخه‌بندی:

پروژه Printoo24 از **نسخه‌بندی URL** استفاده می‌کند:

```
Base URL: /api/
├── v1/        # نسخه 1 (فعلی)
│   ├── accounts/
│   ├── shop/
│   ├── cart/
│   └── ...
└── v2/        # نسخه 2 (آینده - برای breaking changes)
```

### مزایای این روش:
- ✅ وضوح کامل برای کلاینت‌ها
- ✅ امکان نگهداری چند نسخه همزمان
- ✅ آدرس‌دهی واضح و ساده
- ✅ مستندسازی آسان

### نسخه‌های آینده:
وقتی نیاز به تغییرات بزرگ (breaking changes) باشد:
1. کپی پوشه `v1/` به `v2/`
2. اعمال تغییرات در `v2/`
3. به‌روزرسانی `api/v2/urls.py`
4. اضافه کردن مسیرهای جدید در `api/urls.py`
5. نسخه قدیمی (`v1/`) برای backward compatibility نگهداری می‌شود

---

## احراز هویت

### روش احراز هویت: JWT (JSON Web Token)

### فرآیند احراز هویت:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Login Request                                            │
│    POST /api/v1/accounts/login/                             │
│    {username: "user", "password": "pass"}                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Token Generation                                         │
│    - Access Token (5 ساعت اعتبار)                           │
│    - Refresh Token (1 روز اعتبار)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Response                                                 │
│    {                                                         │
│      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", │
│      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." │
│    }                                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Subsequent Requests                                      │
│    Headers: {Authorization: Bearer <access_token>}          │
└─────────────────────────────────────────────────────────────┘
```

### استفاده از توکن:

```http
GET /api/v1/shop/products/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### تمدید توکن:

```http
POST /api/v1/accounts/token/refresh/
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### بلاک‌لیست توکن:
- با خروج از حساب، توکن در بلاک‌لیست قرار می‌گیرد
- توکن‌های بلاک‌شده دیگر معتبر نیستند

---

## Endpointهای اصلی

### ساختار URL:

```
Base URL: /api/v1/

┌─────────────────────────────────────────────────────────────┐
│ ماژول‌های اصلی API                                          │
├─────────────────────────────────────────────────────────────┤
│ accounts/        # احراز هویت و حساب کاربری                 │
│ shop/            # محصولات و فروشگاه                        │
│ cart/            # سبد خرید                                 │
│ order/           # سفارشات                                  │
│ userprofile/     # پروفایل کاربر                            │
│ notification/    # اعلان‌ها                                 │
│ dashboard/       # داشبورد مدیریت                           │
│ blog/            # وبلاگ                                    │
│ home/            # صفحه اصلی                                │
└─────────────────────────────────────────────────────────────┘
```

### نمای کلی Endpointها:

#### 1. **Accounts API** (`/api/v1/accounts/`)
**مسیر**: `backend/api/v1/accounts/`

**Endpointهای اصلی:**
```
POST   /login/                    # ورود به حساب
POST   /register/                 # ثبت‌نام
POST   /verify-email/             # تأیید ایمیل
POST   /password-reset/           # درخواست بازنشانی رمز
POST   /password-reset/confirm/   # تأیید بازنشانی رمز
POST   /token/refresh/            # تمدید توکن
POST   /token/verify/             # بررسی اعتبار توکن
POST   /logout/                   # خروج از حساب
```

**مستندات مربوطه**: [Accounts API Documentation](./accounts.md)

#### 2. **Shop API** (`/api/v1/shop/`)
**مسیر**: `backend/api/v1/shop/`

**Endpointهای اصلی:**
```
GET    /products/                 # لیست محصولات
GET    /products/{id}/            # جزئیات محصول
GET    /categories/               # لیست دسته‌بندی‌ها
GET    /categories/{id}/          # جزئیات دسته‌بندی
POST   /comments/                 # ارسال نظر
GET    /comments/{id}/            # جزئیات نظر
```

**مستندات مربوطه**: [Shop API Documentation](./shop.md)

#### 3. **Cart API** (`/api/v1/cart/`)
**مسیر**: `backend/api/v1/cart/`

**Endpointهای اصلی:**
```
GET    /cart/                     # مشاهده سبد خرید
POST   /cart/add/                 # افزودن به سبد خرید
PUT    /cart/update/{id}/         # بروزرسانی تعداد
DELETE /cart/remove/{id}/         # حذف از سبد خرید
DELETE /cart/clear/               # پاک کردن سبد خرید
```

**مستندات مربوطه**: [Cart API Documentation](./cart.md)

#### 4. **Order API** (`/api/v1/order/`)
**مسیر**: `backend/api/v1/order/`

**Endpointهای اصلی:**
```
POST   /create/                   # ایجاد سفارش
GET    /list/                     # لیست سفارشات کاربر
GET    /detail/{id}/              # جزئیات سفارش
POST   /cancel/{id}/              # لغو سفارش
```

**مستندات مربوطه**: [Order API Documentation](./order.md)

#### 5. **UserProfile API** (`/api/v1/userprofile/`)
**مسیر**: `backend/api/v1/userprofile/`

**Endpointهای اصلی:**
```
GET    /profile/                  # مشاهده پروفایل
PUT    /profile/                  # بروزرسانی پروفایل
POST   /address/                  # افزودن آدرس
GET    /addresses/                # لیست آدرس‌ها
PUT    /address/{id}/             # بروزرسانی آدرس
DELETE /address/{id}/             # حذف آدرس
GET    /orders/                   # تاریخچه سفارشات
GET    /wallet/                   # اطلاعات کیف پول
```

**مستندات مربوطه**: [UserProfile API Documentation](./userprofile.md)

#### 6. **Notification API** (`/api/v1/notification/`)
**مسیر**: `backend/api/v1/notification/`

**Endpointهای اصلی:**
```
GET    /notifications/            # لیست اعلان‌ها
POST   /notifications/read/       # علامت‌گذاری به عنوان خوانده شده
DELETE /notifications/{id}/       # حذف اعلان
```

**مستندات مربوطه**: [Notification API Documentation](./notification.md)

#### 7. **Dashboard API** (`/api/v1/dashboard/`)
**مسیر**: `backend/api/v1/dashboard/`

**Endpointهای اصلی:**
```
# مدیریت محصولات
GET    /products/                 # لیست محصولات
POST   /products/                 # ایجاد محصول
PUT    /products/{id}/            # بروزرسانی محصول
DELETE /products/{id}/            # حذف محصول

# مدیریت سفارشات
GET    /orders/                   # لیست سفارشات
PUT    /orders/{id}/status/       # تغییر وضعیت سفارش

# مدیریت کاربران
GET    /users/                    # لیست کاربران
PUT    /users/{id}/               # بروزرسانی کاربر

# گزارشات
GET    /reports/sales/            # گزارش فروش
GET    /reports/customers/        # گزارش مشتریان

# استخراج و ایمپورت
POST   /products-export-import/export/      # استخراج محصولات
POST   /products-export-import/import/      # ایمپورت محصولات
GET    /products-export-import/template/    # دانلود فایل نمونه
GET    /products-export-import/history/     # تاریخچه استخراج‌ها
```

**مستندات مربوطه**: [Dashboard API Documentation](./dashboard.md)

---

## مشخصات فنی

### 1. **فرمت داده**
- **Request**: JSON
- **Response**: JSON
- **Content-Type**: `application/json`

### 2. **کدهای وضعیت HTTP**

| کد | توضیحات | مثال |
|-----|---------|------|
| 200 | موفقیت‌آمیز | دریافت داده‌ها |
| 201 | ایجاد شد | ایجاد محصول جدید |
| 204 | بدون محتوا | حذف موفق |
| 400 | درخواست نامعتبر | اعتبارسنجی ناموفق |
| 401 | غیرمجاز | توکن نامعتبر یا منقضی |
| 403 | ممنوع | عدم دسترسی |
| 404 | یافت نشد | محصول وجود ندارد |
| 429 | درخواست بیش از حد | Rate limit exceeded |
| 500 | خطای سرور | خطای داخلی |

### 3. **ساختار Response استاندارد:**

#### موفق:
```json
{
  "success": true,
  "message": "عملیات با موفقیت انجام شد",
  "data": {
    // داده‌های مورد نظر
  }
}
```

#### ناموفق:
```json
{
  "success": false,
  "message": "پیام خطا",
  "errors": {
    // جزئیات خطاها
  }
}
```

### 4. **پاگینیشن (Pagination)**

```json
{
  "count": 100,
  "next": "http://api.example.org/accounts/?page=5",
  "previous": "http://api.example.org/accounts/?page=3",
  "results": [
    // لیست آیتم‌ها
  ]
}
```

**پارامترهای پاگینیشن:**
- `page`: شماره صفحه (پیش‌فرض: 1)
- `page_size`: تعداد آیتم در هر صفحه (پیش‌فرض: 20، حداکثر: 100)

**مثال:**
```
GET /api/v1/shop/products/?page=2&page_size=50
```

### 5. **فیلتر کردن (Filtering)**

```http
GET /api/v1/shop/products/?category=1&min_price=1000&max_price=5000
```

**فیلترهای رایج:**
- `category`: فیلتر بر اساس دسته‌بندی
- `min_price`, `max_price`: محدوده قیمت
- `search`: جستجو در نام و توضیحات
- `ordering`: مرتب‌سازی (`?ordering=-created_at`)

### 6. **جستجو (Search)**

```http
GET /api/v1/shop/products/?search=تیشرت
```

### 7. **مرتب‌سازی (Ordering)**

```http
# مرتب‌سازی صعودی
GET /api/v1/shop/products/?ordering=price

# مرتب‌سازی نزولی
GET /api/v1/shop/products/?ordering=-price

# مرتب‌سازی بر اساس چند فیلد
GET /api/v1/shop/products/?ordering=-created_at,price
```

### 8. **محدودیت نرخ (Rate Limiting)**

| نوع کاربر | محدودیت |
|-----------|---------|
| کاربران ناشناس | 100 درخواست در روز |
| کاربران عادی | 1000 درخواست در روز |
| ورود به حساب | 50 درخواست در دقیقه |
| ثبت‌نام | 30 درخواست در ساعت |

**هدرهای مربوطه:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

---

## مستندات تعاملی

### Swagger UI:
```
http://localhost:8000/api/docs/
```

### ReDoc:
```
http://localhost:8000/api/schema/
```

### OpenAPI Schema:
```
http://localhost:8000/api/schema/
```

**ویژگی‌های مستندات تعاملی:**
- ✅ تست مستقیم APIها از مرورگر
- ✅ مشاهده ساختار Request/Response
- ✅ دانلود Schema به فرمت JSON/YAML
- ✅ نمایش خودکار تغییرات API

---

## خطاهای رایج

### 1. خطای 401 (Unauthorized)
**علت**: توکن نامعتبر یا منقضی شده
**راه‌حل**: استفاده از توکن جدید یا تمدید توکن

### 2. خطای 403 (Forbidden)
**علت**: عدم دسترسی به منبع
**راه‌حل**: بررسی مجوزهای کاربر

### 3. خطای 429 (Too Many Requests)
**علت**: ارسال درخواست بیش از حد مجاز
**راه‌حل**: کاهش تعداد درخواست‌ها یا انتظار تا reset

### 4. خطای 400 (Bad Request)
**علت**: داده‌های ورودی نامعتبر
**راه‌حل**: بررسی خطاهای اعتبارسنجی در response

---

## نکات مهم برای توسعه‌دهندگان

### 1. **الگوی نام‌گذاری URL**
```python
# خوب
/api/v1/shop/products/
/api/v1/cart/add/

# بد
/api/v1/shop/get_products
/api/v1/cart/addToCart
```

### 2. **استفاده از HTTP Methods**
```python
GET    # دریافت داده
POST   # ایجاد داده جدید
PUT    # بروزرسانی کامل
PATCH  # بروزرسانی جزئی
DELETE # حذف داده
```

### 3. **مدیریت خطا**
```python
# همیشه از exception handler سفارشی استفاده کنید
# فایل: core/product/exception_handler.py
```

### 4. **مستندسازی**
```python
# از docstrings در views استفاده کنید
# از drf-spectacular برای مستندات خودکار استفاده کنید
```

---

## 📚 مستندات مرتبط

- **[مستندات معماری کلی](../00_architecture_overview.md)** - پیش‌نیاز این مستند
- **[مستندات تنظیمات پروژه](../settings/README.md)** - پیش‌نیاز این مستند
- **[مستندات اپلیکیشن‌ها](../apps/README.md)** - بعد از این مستند

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24