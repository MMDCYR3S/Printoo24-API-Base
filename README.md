# کتابخانه مشترک Printoo24 (shared_libs)

## 📖 معرفی

کتابخانه `shared_libs` هسته اصلی و کتابخانه مشترک پروژه Printoo24 است که منطق تجاری (Business Logic)، مدل‌های داده (Data Models)، سرویس‌های دامنه (Domain Services) و زیرساخت‌های مشترک را برای تمام سرویس‌های پروژه (مانند `admin_site` و `customer_site`) فراهم می‌کند.

### ✨ ویژگی‌های کلیدی

- **معماری Domain-Driven Design (DDD)**: جداسازی کامل منطق تجاری از لایه نمایش
- **قابل استفاده مجدد**: یک کتابخانه قابل نصب که در چندین سرویس استفاده می‌شود
- **Repository Pattern**: دسترسی به داده از طریق Repositoryهای تخصصی
- **Domain Services**: منطق تجاری پیچیده در سرویس‌های مستقل
- **مدیریت خطا**: Exceptionهای اختصاصی برای هر دامنه
- **زیرساخت مشترک**: سرویس‌های کش و ایمیل

---

## 🏗️ ساختار پروژه

```
shared_libs/
├── core/                          # اپلیکیشن اصلی Django
│   ├── users/                     # دامنه کاربران
│   │   ├── models.py             # مدل‌های کاربر، نقش، پروفایل
│   │   ├── managers/             # Repositoryهای دسترسی به داده
│   │   ├── services/             # سرویس‌های دامنه کاربران
│   │   └── exceptions.py         # Exceptionهای مربوط به کاربران
│   │
│   ├── product/                   # دامنه محصولات
│   │   ├── models.py             # مدل‌های محصول، دسته‌بندی، ویژگی‌ها
│   │   ├── managers/             # Repositoryهای محصول
│   │   ├── services/             # سرویس‌های محاسبه قیمت، مدیریت محصول
│   │   └── exceptions.py         # Exceptionهای مربوط به محصول
│   │
│   ├── order/                     # دامنه سفارشات
│   │   ├── models.py             # مدل‌های سفارش، آیتم‌ها، وضعیت
│   │   ├── managers/             # Repositoryهای سفارش
│   │   ├── services/             # سرویس‌های مدیریت سفارش
│   │   └── exceptions.py         # Exceptionهای مربوط به سفارش
│   │
│   ├── financial/                 # دامنه مالی
│   │   ├── models.py             # مدل‌های فاکتور، پیش‌فاکتور
│   │   └── managers/             # Repositoryهای مالی
│   │
│   ├── infrastructure/            # زیرساخت‌های مشترک
│   │   ├── cache.py              # سرویس کش
│   │   └── email.py              # سرویس ایمیل
│   │
│   ├── models/                    # مدل‌های اضافی
│   │   └── ticket.py             # سیستم تیکت
│   │
│   ├── management/                # دستورات Django Management
│   │   └── commands/             # دستورات seed و utility
│   │
│   ├── signals.py                 # Django Signals
│   ├── site.py                    # تنظیمات Admin Site
│   └── apps.py                    # تنظیمات اپلیکیشن
│
├── docs/                          # مستندات
│   ├── README.md                  # این فایل
│   ├── ARCHITECTURE.md            # مستندات معماری
│   ├── MODELS.md                  # مستندات مدل‌ها
│   ├── SERVICES.md                # مستندات سرویس‌ها
│   └── DEVELOPMENT.md             # راهنمای توسعه
│
└── setup.py                       # فایل نصب پکیج
```

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8+
- Django 4.0+
- pip

### نصب در محیط محلی (برای توسعه)

```bash
# نصب در حالت قابل ویرایش (editable mode)
cd backend/shared_libs
pip install -e .
```

### نصب در Docker

در فایل `docker-compose.yml`، پکیج به صورت خودکار نصب می‌شود:

```yaml
command: >
  sh -c "pip install -e /usr/src/shared_libs/core/ && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
volumes:
  - ./shared_libs/core:/usr/src/shared_libs/core
```

فلگ `-e` (editable) به این معنی است که تغییرات در کد به صورت زنده (Live Reload) در کانتینر اعمال می‌شود.

---

## 📦 استفاده در پروژه

پس از نصب، می‌توانید از ماژول‌ها به صورت زیر استفاده کنید:

### Import مدل‌ها

```python
from core.models import User, Product, Order, CustomerProfile
from core.users.models import Role, UserRole
from core.product.models import ProductCategory, ProductOption
from core.order.models import OrderStatus, OrderItem
```

### استفاده از Repositoryها (Managers)

```python
from core.models import Product

# استفاده از متدهای Repository
product = Product.objects.get_product_by_slug('product-slug')
products = Product.objects.get_active_products()
categories = ProductCategory.objects.get_root_categories()
```

### استفاده از Domain Services

```python
from core.product.services import ProductPriceCalculator
from core.order.services import OrderService

# محاسبه قیمت محصول
calculator = ProductPriceCalculator(
    product=product,
    quantity=100,
    width=50,
    height=30,
    selected_values=option_values
)
price_info = calculator.calculate()

# مدیریت سفارش
order_service = OrderService()
order = order_service.get_order_details(user_id=1, order_id=123)
```

### استفاده از Infrastructure Services

```python
from core.infrastructure.cache import CacheService
from core.infrastructure.email import EmailService

# استفاده از کش
cache = CacheService()
cache.set('key', 'value', timeout=3600)
value = cache.get('key')

# ارسال ایمیل
email_service = EmailService()
email_service.send(
    subject='خوش‌آمدید',
    template_name='emails/welcome.html',
    context={'user': user},
    from_email='noreply@printoo24.com',
    to_email=user.email
)
```

---

## 🎯 دامنه‌های اصلی

### 👤 Users (کاربران)
- مدیریت کاربران و احراز هویت
- سیستم نقش‌ها و دسترسی‌ها (RBAC)
- پروفایل مشتری
- آدرس‌ها و اطلاعات تماس
- کیف پول (Wallet)

**فایل‌های کلیدی:**
- `core/users/models.py` - مدل‌های کاربر
- `core/users/services/identity.py` - سرویس احراز هویت
- `core/users/services/customers.py` - سرویس مدیریت مشتریان

### 📦 Product (محصولات)
- مدیریت محصولات و دسته‌بندی‌ها
- سیستم ویژگی‌ها و آپشن‌ها
- محاسبه قیمت پیشرفته
- مدیریت رسانه‌ها (تصاویر، فایل‌ها)
- نظرات و امتیازدهی

**فایل‌های کلیدی:**
- `core/product/models.py` - مدل‌های محصول
- `core/product/services/calculator.py` - موتور محاسبه قیمت
- `core/product/services/product.py` - سرویس مدیریت محصول

### 🛒 Order (سفارشات)
- مدیریت سفارش‌ها و آیتم‌ها
- سیستم وضعیت‌های سفارش (Workflow)
- مدیریت فایل‌های طراحی
- گزارش‌های سفارش

**فایل‌های کلیدی:**
- `core/order/models.py` - مدل‌های سفارش
- `core/order/services/order.py` - سرویس مدیریت سفارش

### 💰 Financial (مالی)
- مدیریت فاکتورها (Invoice)
- پیش‌فاکتورها (Quotation)
- تراکنش‌های مالی

---

## 🔧 مدیریت خطاها

هر دامنه Exceptionهای اختصاصی خود را دارد:

```python
from core.users.exceptions import (
    EmailAlreadyExistsException,
    UserNotFoundException
)
from core.product.exceptions import (
    ProductNotFoundException,
    ProductCategoryNotFoundException
)
from core.order.exceptions import (
    OrderNotFoundException,
    InvalidOrderOperationException
)

try:
    user = User.objects.get(email='test@example.com')
except User.DoesNotExist:
    raise UserNotFoundException("کاربر یافت نشد")
```

---

## 📚 مستندات بیشتر

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - معماری، الگوهای طراحی، لایه‌ها
- **[MODELS.md](./MODELS.md)** - مستندات کامل مدل‌ها و روابط
- **[SERVICES.md](./SERVICES.md)** - مستندات سرویس‌ها و منطق تجاری
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - راهنمای توسعه و Contribution

---

## 🤝 مشارکت

برای مشارکت در پروژه، لطفاً [DEVELOPMENT.md](./DEVELOPMENT.md) را مطالعه کنید.

---

## 📝 مجوز

این پروژه بخشی از پروژه Printoo24 است.

---

## 👥 تیم

- **Developer**: Mohammad Amin Gholami
- **Email**: amingholami06@gmail.com

---

**نسخه**: 0.1.0  
**آخرین به‌روزرسانی**: ۱۴۰۴

