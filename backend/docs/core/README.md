# مستندات ماژول Core پروژه Printoo24 Backend

## 📋 پیش‌نیاز
- مطالعه [مستندات معماری کلی](../00_architecture_overview.md)
- مطالعه [مستندات تنظیمات پروژه](../settings/README.md)
- مطالعه [مستندات API](../api/README.md)
- مطالعه [مستندات اپلیکیشن‌ها](../apps/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار ماژول Core](#ساختار-ماژول-core)
3. [مدل‌های کاربران (users)](#مدل‌های-کاربران-users)
4. [مدل‌های محصول (product)](#مدل‌های-محصول-product)
5. [مدل‌های سفارش (order)](#مدل‌های-سفارش-order)
6. [ماژول مالی (financial)](#ماژول-مالی-financial)
7. [زیرساخت‌ها (infrastructure)](#زیرساخت‌ها-infrastructure)
8. [دستورات مدیریتی (management)](#دستورات-مدیریتی-management)

---

## مقدمه

ماژول **Core** هسته مشترک پروژه Printoo24 است که شامل مدل‌های پایه، سرویس‌های مشترک و Managerهای سفارشی است. این ماژول توسط تمام اپلیکیشن‌های پروژه استفاده می‌شود و اطمینان حاصل می‌کند که داده‌ها در سراسر پروژه یکسان باشند.

### 🎯 اهداف ماژول Core:
- ✅ تعریف مدل‌های پایه و reusable
- ✅ ارائه سرویس‌های مشترک بین اپلیکیشن‌ها
- ✅ مدیریت متمرکز منطق دیتابیس (Managers)
- ✅ جلوگیری از تکرار کد
- ✅ یکپارچگی داده‌ها در سراسر پروژه

### اصلاحات کلیدی:

```
┌─────────────────────────────────────────────────────────────┐
│  اپلیکیشن‌های پروژه (apps/)                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ accounts │  │  shop    │  │   cart   │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       └─────────────┼─────────────┘                         │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ماژول Core (core/)                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐      │  │
│  │  │   Models   │  │  Managers  │  │  Services  │      │  │
│  │  └────────────┘  └────────────┘  └────────────┘      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ساختار ماژول Core

### نمای کلی ساختار:

```
core/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── signals.py               # سیگنال‌های سراسری
├── site.py                  # تنظیمات Site framework
├── models/                  # مدل‌های پایه
│   ├── __init__.py
│   └── ticket.py            # مدل تیکت‌ها
├── users/                   # ماژول کاربران
│   ├── __init__.py
│   ├── models.py            # مدل User و Profile
│   ├── exceptions.py        # Exceptionهای سفارشی
│   ├── managers/            # منیجرهای سفارشی
│   │   ├── __init__.py
│   │   ├── base.py          # BaseManager
│   │   ├── users.py         # UserManager
│   │   ├── profiles.py      # ProfileManager
│   │   ├── roles.py         # RoleManager
│   │   └── address.py       # AddressManager
│   └── services/            # سرویس‌های مشترک
│       ├── __init__.py
│       └── ...
├── product/                 # ماژول محصولات
│   ├── __init__.py
│   ├── models.py            # مدل‌های محصول
│   ├── exceptions.py        # Exceptionهای سفارشی
│   ├── exception_handler.py # هندلر خطاهای API
│   ├── schemas.py           # Schemaهای OpenAPI
│   ├── managers/            # منیجرهای سفارشی
│   │   ├── __init__.py
│   │   ├── base.py          # BaseManager
│   │   ├── product.py       # ProductManager
│   │   ├── category.py      # CategoryManager
│   │   ├── feedback.py      # FeedbackManager
│   │   ├── media.py         # MediaManager
│   │   └── options.py       # ProductOptionsManager
│   └── services/            # سرویس‌های مشترک
│       ├── __init__.py
│       ├── calculator.py    # محاسبه قیمت
│       ├── category.py      # مدیریت دسته‌بندی
│       ├── feedback.py      # مدیریت فیدبک
│       ├── media.py         # مدیریت مدیا
│       ├── product_fields.py # مدیریت فیلدهای داینامیک
│       └── product.py       # مدیریت محصول
├── order/                   # ماژول سفارشات
│   ├── __init__.py
│   ├── models.py            # مدل‌های سفارش
│   ├── exceptions.py        # Exceptionهای سفارشی
│   ├── managers/            # منیجرهای سفارشی
│   │   ├── __init__.py
│   │   └── ...
│   └── services/            # سرویس‌های مشترک
│       ├── __init__.py
│       └── ...
└── financial/               # ماژول مالی
    ├── __init__.py
    ├── models.py
    ├── managers/
    └── services/
```

---

## مدل‌های کاربران (users)

### 📍 موقعیت: `backend/core/users/`

### هدف:
مدیریت کامل کاربران سیستم شامل اطلاعات پایه، پروفایل، نقش‌ها و آدرس‌ها.

### مدل‌های اصلی:

#### 1. **User** (`models.py`)
**توضیحات:**
مدل اصلی کاربر سیستم که به جای مدل پیش‌فرض Django استفاده می‌شود.

**فیلدهای اصلی:**
```python
class User(AbstractBaseUser, PermissionsMixin):
    # اطلاعات پایه
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    
    # اطلاعات شخصی
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    # وضعیت
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # تاریخ‌ها
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    # تأیید حساب
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # نقش
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
```

**نقش‌ها (ROLE_CHOICES):**
- `customer`: کاربر عادی
- `staff`: کارمند
- `admin`: مدیر

**متدهای اصلی:**
```python
def get_full_name(self) -> str
def get_short_name(self) -> str
def has_role(self, role) -> bool
```

#### 2. **UserProfile** (`models.py`)
**توضیحات:**
پروفایل تکمیلی کاربر با اطلاعات اضافی.

**فیلدهای اصلی:**
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    national_code = models.CharField(max_length=10, blank=True)
```

#### 3. **Address** (`models.py`)
**توضیحات:**
آدرس‌های کاربر برای ارسال سفارشات.

**فیلدهای اصلی:**
```python
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # عنوان آدرس (خانه، کار، ...)
    full_address = models.TextField()
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False)
```

#### 4. **Wallet** (`models.py`)
**توضیحات:**
کیف پول الکترونیکی کاربر.

**فیلدهای اصلی:**
```python
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 5. **Transaction** (`models.py`)
**توضیحات:**
تراکنش‌های مالی کیف پول.

**فیلدهای اصلی:**
```python
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**انواع تراکنش (TRANSACTION_TYPES):**
- `deposit`: واریز
- `withdraw`: برداشت
- `purchase`: خرید
- `refund`: بازگشت وجه

### Managerهای اصلی:

#### 1. **UserManager** (`managers/users.py`)
**وظایف:**
- ایجاد کاربران
- جستجوی کاربران
- مدیریت نقش‌ها

**متدهای اصلی:**
```python
class UserManager(BaseManager):
    def create_user(self, username, email, password, **extra_fields) -> User
    def create_superuser(self, username, email, password, **extra_fields) -> User
    def get_by_email(self, email) -> User
    def get_by_phone(self, phone) -> User
    def get_active_users(self) -> QuerySet
    def get_staff_users(self) -> QuerySet
```

#### 2. **AddressManager** (`managers/address.py`)
**وظایف:**
- مدیریت آدرس‌های کاربر
- تنظیم آدرس پیش‌فرض

**متدهای اصلی:**
```python
class AddressManager(BaseManager):
    def get_user_addresses(self, user) -> QuerySet
    def get_default_address(self, user) -> Address
    def set_default(self, user, address_id) -> bool
```

---

## مدل‌های محصول (product)

### 📍 موقعیت: `backend/core/product/`

### هدف:
مدیریت کامل محصولات، دسته‌بندی‌ها، ویژگی‌های داینامیک و فرمول‌های قیمت‌گذاری.

### مدل‌های اصلی:

#### 1. **Product** (`models.py`)
**توضیحات:**
مدل اصلی محصول فروشگاه.

**فیلدهای اصلی:**
```python
class Product(models.Model):
    # اطلاعات پایه
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=12, decimal_places=0)
    
    # وضعیت
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # موجودی
    stock = models.IntegerField(default=0)
    track_stock = models.BooleanField(default=True)
    
    # دسته‌بندی
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. **Category** (`models.py`)
**توضیحات:**
دسته‌بندی‌های سلسله‌مراتبی محصولات.

**فیلدهای اصلی:**
```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
```

#### 3. **ProductMedia** (`models.py`)
**توضیحات:**
تصاویر و فایل‌های پیوست محصول.

**فیلدهای اصلی:**
```python
class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to='products/')
    type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
```

**انواع مدیا (MEDIA_TYPES):**
- `image`: تصویر
- `video`: ویدیو
- `document`: سند

#### 4. **ProductField** (`models.py`)
**توضیحات:**
فیلدهای داینامیک محصول (سایز، جنس، رنگ، ...).

**فیلدهای اصلی:**
```python
class ProductField(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=False)
    options = models.JSONField()  # لیست گزینه‌ها
```

**انواع فیلد (FIELD_TYPES):**
- `select`: انتخاب یک گزینه
- `multiselect`: انتخاب چند گزینه
- `text`: متن
- `number`: عدد
- `file`: فایل

#### 5. **ProductOption** (`models.py`)
**توضیحات:**
گزینه‌های هر فیلد داینامیک.

**فیلدهای اصلی:**
```python
class ProductOption(models.Model):
    field = models.ForeignKey(ProductField, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    price_modifier = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    stock = models.IntegerField(default=0)
```

#### 6. **PriceFormula** (`models.py`)
**توضیحات:**
فرمول‌های قیمت‌گذاری بر اساس انتخاب‌های کاربر.

**فیلدهای اصلی:**
```python
class PriceFormula(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    formula = models.JSONField()  # فرمول محاسبه قیمت
    is_active = models.BooleanField(default=True)
```

#### 7. **ProductComment** (`models.py`)
**توضیحات:**
نظرات و امتیازات کاربران برای محصولات.

**فیلدهای اصلی:**
```python
class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Managerهای اصلی:

#### 1. **ProductManager** (`managers/product.py`)
**وظایف:**
- مدیریت محصولات
- فیلتر کردن و جستجو
- مدیریت موجودی

**متدهای اصلی:**
```python
class ProductManager(BaseManager):
    def get_active_products(self) -> QuerySet
    def get_featured_products(self) -> QuerySet
    def search(self, query) -> QuerySet
    def filter_by_category(self, category_id) -> QuerySet
    def filter_by_price_range(self, min_price, max_price) -> QuerySet
    def get_related_products(self, product) -> QuerySet
```

#### 2. **CategoryManager** (`managers/category.py`)
**وظایف:**
- مدیریت دسته‌بندی‌ها
- دریافت ساختار درختی

**متدهای اصلی:**
```python
class CategoryManager(BaseManager):
    def get_active_categories(self) -> QuerySet
    def get_category_tree(self) -> dict
    def get_children(self, parent_id) -> QuerySet
```

#### 3. **FeedbackManager** (`managers/feedback.py`)
**وظایف:**
- مدیریت کامنت‌ها
- محاسبه میانگین امتیاز

**متدهای اصلی:**
```python
class FeedbackManager(BaseManager):
    def get_approved_comments(self, product_id) -> QuerySet
    def get_average_rating(self, product_id) -> float
    def approve_comment(self, comment_id) -> bool
```

### سرویس‌های اصلی:

#### 1. **ProductCalculator** (`services/calculator.py`)
**وظایف:**
- محاسبه قیمت نهایی محصول بر اساس ویژگی‌های انتخابی
- اعمال فرمول‌های قیمت‌گذاری

**متدهای اصلی:**
```python
class ProductCalculator:
    def calculate_price(self, product, selected_options) -> Decimal
    def apply_formula(self, product, selections) -> Decimal
    def get_price_breakdown(self, product, options) -> dict
```

#### 2. **ProductService** (`services/product.py`)
**وظایف:**
- مدیریت کامل محصول
- ایجاد و بروزرسانی محصول
- مدیریت مدیا و فیلدها

**متدهای اصلی:**
```python
class ProductService:
    def create_product(self, product_data, media_files) -> Product
    def update_product(self, product_id, product_data) -> Product
    def delete_product(self, product_id) -> bool
    def upload_media(self, product, file, type) -> ProductMedia
```

#### 3. **CategoryService** (`services/category.py`)
**وظایف:**
- مدیریت دسته‌بندی‌ها
- دریافت ساختار درختی

**متدهای اصلی:**
```python
class CategoryService:
    def get_categories(self) -> QuerySet
    def get_category_tree(self) -> dict
    def create_category(self, category_data) -> Category
```

---

## مدل‌های سفارش (order)

### 📍 موقعیت: `backend/core/order/`

### هدف:
مدیریت مدل‌های مربوط به سفارشات.

### مدل‌های اصلی:

#### 1. **Order**
**توضیحات:**
مدل اصلی سفارش.

**فیلدهای اصلی:**
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. **OrderItem**
**توضیحات:**
آیتم‌های هر سفارش.

**فیلدهای اصلی:**
```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    selected_options = models.JSONField()
```

#### 3. **OrderStatus**
**توضیحات:**
تاریخچه تغییرات وضعیت سفارش.

**فیلدهای اصلی:**
```python
class OrderStatus(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=20, choices=ORDER_STATUSES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## ماژول مالی (financial)

### 📍 موقعیت: `backend/core/financial/`

### هدف:
مدیریت عملیات مالی سیستم شامل تراکنش‌ها، گزارشات و حسابداری.

### ساختار:

```
financial/
├── __init__.py
├── models.py                # مدل‌های مالی
├── managers/                # منیجرهای مالی
│   ├── __init__.py
│   └── ...
└── services/                # سرویس‌های مالی
    ├── __init__.py
    ├── transaction_service.py
    ├── report_service.py
    └── wallet_service.py
```

### مدل‌های اصلی:

#### 1. **Transaction** (در core.users.models)
- تراکنش‌های کیف پول

#### 2. **Invoice**
**توضیحات:**
فاکتور سفارشات.

**فیلدهای اصلی:**
```python
class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    tax = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

### سرویس‌های اصلی:

#### 1. **TransactionService**
**وظایف:**
- ثبت تراکنش‌های مالی
- مدیریت کیف پول
- گزارش مالی

**متدهای اصلی:**
```python
class TransactionService:
    def create_transaction(self, user, amount, type, description) -> Transaction
    def get_wallet_balance(self, user) -> Decimal
    def get_transactions(self, user, filters) -> QuerySet
    def generate_financial_report(self, start_date, end_date) -> dict
```

---

## زیرساخت‌ها (infrastructure)

### 📍 موقعیت: `backend/core/infrastructure/`

### هدف:
ابزارها و کلاس‌های پایه برای استفاده در سراسر پروژه.

### ساختار:

```
infrastructure/
├── __init__.py
├── base_managers.py         # BaseManager برای تمام Managerها
├── base_services.py         # BaseService برای تمام سرویس‌ها
├── exceptions.py            # Exceptionهای پایه
├── utils.py                 # ابزارهای کمکی
└── constants.py             # ثابت‌های پروژه
```

### کلاس‌های اصلی:

#### 1. **BaseManager**
```python
class BaseManager(models.Manager):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None
```

#### 2. **BaseService**
```python
class BaseService:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _log_error(self, message, exception):
        self.logger.error(f"{message}: {str(exception)}", exc_info=True)
```

---

## دستورات مدیریتی (management)

### 📍 موقعیت: `backend/core/management/`

### هدف:
دستورات سفارشی Django برای عملیات مدیریتی.

### ساختار:

```
management/
├── __init__.py
└── commands/
    ├── __init__.py
    ├── cleanup_logs.py      # پاکسازی لاگ‌های قدیمی
    ├── generate_reports.py  # تولید گزارشات
    └── seed_data.py         # پر کردن دیتابیس با داده‌های نمونه
```

### دستورات موجود:

#### 1. **cleanup_logs**
**توضیحات:**
پاکسازی فایل‌های لاگ قدیمی.

**استفاده:**
```bash
python manage.py cleanup_logs --days=30
```

#### 2. **generate_reports**
**توضیحات:**
تولید گزارشات مالی و آماری.

**استفاده:**
```bash
python manage.py generate_reports --type=sales --start-date=2024-01-01 --end-date=2024-12-31
```

---

## 🔗 ارتباط Core با اپلیکیشن‌ها

```
┌─────────────────────────────────────────────────────────────┐
│  اپلیکیشن‌ها از Core استفاده می‌کنند:                       │
└─────────────────────────────────────────────────────────────┘

accounts/
├── استفاده از core.User به جای User پیش‌فرض Django
├── استفاده از core.UserProfile
├── استفاده از core.Wallet و Transaction
└── استفاده از AddressManager

shop/
├── استفاده از Product، Category، ProductMedia
├── استفاده از ProductManager برای فیلتر کردن
├── استفاده از ProductCalculator برای محاسبه قیمت
└── استفاده از ProductComment

cart/
├── استفاده از Product برای بررسی موجودی
├── استفاده از ProductOption برای ویژگی‌های انتخابی
└── استفاده از ProductManager

order/
├── استفاده از Order، OrderItem، OrderStatus
├── استفاده از Product برای کم کردن موجودی
└── استفاده از Address برای آدرس ارسال

userprofile/
├── استفاده از UserProfile
├── استفاده از Address
├── استفاده از Wallet و Transaction
└── استفاده از UserManager

notification/
└── استفاده از User برای ارسال اعلان

dashboard/
├── استفاده از تمام مدل‌های بالا
├── استفاده از تمام Managerها
└── استفاده از تمام سرویس‌های Core
```

---

## 📋 Checklist استفاده از Core

### هنگام ایجاد مدل جدید:
- [ ] آیا مدل می‌تواند در چند اپلیکیشن استفاده شود؟
- [ ] آیا باید در core قرار گیرد؟
- [ ] آیا Manager سفارشی نیاز است؟
- [ ] آیا Exception سفارشی نیاز است؟

### هنگام ایجاد سرویس جدید:
- [ ] آیا منطق تجاری مشترک است؟
- [ ] آیا می‌تواند در core.services قرار گیرد؟
- [ ] آیا توسط چند اپلیکیشن استفاده می‌شود؟

### هنگام ایجاد Manager:
- [ ] از BaseManager ارث‌بری کنید
- [ ] متدهای مشترک را در BaseManager قرار دهید
- [ ] از get_or_none() استفاده کنید به جای get()

---

## 📚 مستندات مرتبط

- **[مستندات معماری کلی](../00_architecture_overview.md)** - پیش‌نیاز این مستند
- **[مستندات تنظیمات پروژه](../settings/README.md)** - پیش‌نیاز این مستند
- **[مستندات API](../api/README.md)** - پیش‌نیاز این مستند
- **[مستندات اپلیکیشن‌ها](../apps/README.md)** - پیش‌نیاز این مستند

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24