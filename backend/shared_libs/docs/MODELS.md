# مستندات مدل‌های داده (Data Models)

## 📖 مقدمه

این مستند به بررسی کامل مدل‌های داده پروژه Printoo24 می‌پردازد. مدل‌ها با استفاده از Django ORM تعریف شده‌اند و ساختار پایگاه داده، روابط بین موجودیت‌ها و منطق اولیه داده‌ها را مشخص می‌کنند.

---

## 📁 ساختار دامنه‌ها

مدل‌ها در چهار دامنه اصلی سازماندهی شده‌اند:

- **Users** (`core/users/models.py`) - کاربران، نقش‌ها، پروفایل‌ها، آدرس‌ها
- **Product** (`core/product/models.py`) - محصولات، دسته‌بندی‌ها، ویژگی‌ها
- **Order** (`core/order/models.py`) - سفارشات، آیتم‌ها، وضعیت‌ها
- **Financial** (`core/financial/models.py`) - فاکتورها، پیش‌فاکتورها

---

## 👤 دامنه Users (کاربران)

### User (کاربر)

مدل اصلی کاربر سیستم با ارث‌بری از `AbstractBaseUser` و `PermissionsMixin`.

**فیلدهای کلیدی:**
- `username` (CharField, unique) - نام کاربری (USERNAME_FIELD)
- `email` (EmailField, unique) - ایمیل
- `is_active` (BooleanField) - وضعیت فعال/غیرفعال
- `is_staff` (BooleanField) - دسترسی به پنل ادمین
- `is_superuser` (BooleanField) - دسترسی ابرکاربر
- `is_verified` (BooleanField) - تأیید ایمیل
- `created_at`, `updated_at` (DateTimeField) - تاریخچه

**روابط:**
- OneToOne → `CustomerProfile` (customer_profile)
- OneToOne → `Wallet` (wallet)
- ForeignKey ← `UserRole` (user_role)
- ForeignKey ← `Address` (addresses)
- ManyToMany → `Permission` (از طریق PermissionsMixin)

**استفاده:**
```python
from core.models import User

user = User.objects.get(username='testuser')
print(user.email)
print(user.customer_profile.fullname())
```

---

### Role (نقش)

مدل نقش کاربران برای سیستم RBAC (Role-Based Access Control).

**فیلدهای کلیدی:**
- `name` (CharField) - نام نقش
- `slug` (SlugField, unique) - کد سیستمی
- `type` (CharField) - نوع نقش: admin یا normal
- `is_customer` (BooleanField) - آیا نقش برای مشتری است؟
- `description` (TextField) - توضیحات

**روابط:**
- ManyToMany → `Permission` (permission)
- ManyToMany → `OrderStatusGroup` (allowed_groups)
- ForeignKey ← `UserRole` (role_user)

**Property:**
- `allowed_status_groups` - لیست کدهای گروه‌های وضعیت مجاز

**استفاده:**
```python
from core.models import Role

role = Role.objects.get(slug='designer')
print(role.allowed_status_groups)  # ['design', 'qc']
```

---

### UserRole (واسط نقش کاربر)

جدول واسط برای ارتباط User و Role (Many-to-Many).

**فیلدهای کلیدی:**
- `user` (ForeignKey → User)
- `role` (ForeignKey → Role)
- `created_at`, `updated_at`

**نکته:** هر کاربر می‌تواند چندین نقش داشته باشد.

---

### CustomerProfile (پروفایل مشتری)

اطلاعات تکمیلی مشتری، جداسازی از مدل User.

**فیلدهای کلیدی:**
- `user` (OneToOne → User)
- `first_name` (CharField)
- `last_name` (CharField)
- `phone_number` (CharField)
- `company` (CharField, nullable)
- `bio` (TextField, nullable)

**متدها:**
- `fullname()` - نام و نام خانوادگی کامل

**استفاده:**
```python
from core.models import CustomerProfile

profile = user.customer_profile
print(profile.fullname())
```

---

### Province (استان) و City (شهر)

مدل‌های جغرافیایی برای مدیریت آدرس‌ها.

**Province:**
- `name` (CharField)
- `slug` (SlugField, unique, auto-generated)

**City:**
- `name` (CharField)
- `slug` (SlugField, unique, auto-generated)
- `province` (ForeignKey → Province)

**روابط:**
- Province → City (cities) - OneToMany

---

### Address (آدرس)

آدرس‌های کاربران.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User)
- `province` (ForeignKey → Province)
- `city` (ForeignKey → City)
- `postal_code` (CharField)
- `address` (TextField) - آدرس دقیق
- `created_at`, `updated_at`

**استفاده:**
```python
from core.models import Address

addresses = user.addresses.all()
```

---

### Wallet (کیف پول)

کیف پول کاربر برای مدیریت موجودی.

**فیلدهای کلیدی:**
- `user` (OneToOne → User)
- `balance` (DecimalField) - موجودی فعلی
- `created_at`, `updated_at`

**روابط:**
- OneToMany → `WalletTransaction` (transactions)

**نکته مهم:** برای عملیات مالی از `select_for_update()` استفاده می‌شود تا از Race Condition جلوگیری شود.

---

### WalletTransaction (تراکنش کیف پول)

ثبت تمام تراکنش‌های مالی کیف پول.

**فیلدهای کلیدی:**
- `wallet` (ForeignKey → Wallet)
- `transaction_type` (CharField) - نوع تراکنش (deposit, withdraw, payment, ...)
- `amount` (DecimalField) - مبلغ
- `balance_after` (DecimalField) - موجودی پس از تراکنش
- `description` (TextField)
- `created_at`

---

## 📦 دامنه Product (محصولات)

### ProductCategory (دسته‌بندی محصول)

دسته‌بندی درختی محصولات با استفاده از `django-mptt`.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User) - کاربر ایجادکننده
- `name` (CharField)
- `slug` (SlugField, unique, auto-generated)
- `parent` (TreeForeignKey → self) - دسته‌بندی والد
- `description` (TextField, nullable) - برای SEO
- `banner_wide` (ImageField) - بنر عریض صفحه
- `banner_box` (ImageField) - بنر مربعی لیست
- `is_active` (BooleanField)

**متدهای مهم:**
- `get_banner_wide_url()` - دریافت بنر با بررسی والد
- `get_descendants_active()` - زیرمجموعه‌های فعال

**استفاده:**
```python
from core.models import ProductCategory

# دریافت دسته‌بندی‌های ریشه
root_categories = ProductCategory.objects.filter(parent=None, is_active=True)

# دریافت زیرمجموعه‌ها
category = ProductCategory.objects.get(slug='business-cards')
children = category.get_children()
all_descendants = category.get_descendants_active()
```

---

### ProductCategoryRelation (رابطه محصول-دسته)

جدول واسط برای ارتباط Product و ProductCategory با متادیتا.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `category` (ForeignKey → ProductCategory)
- `created_at`

**نکته:** در `save()` کد محصول به صورت خودکار تولید می‌شود (Signal).

---

### Product (محصول)

مدل اصلی محصولات.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User) - کاربر ایجادکننده
- `name` (CharField)
- `slug` (SlugField, unique, auto-generated)
- `code` (CharField, unique) - کد محصول (تولید خودکار)
- `has_price` (BooleanField) - آیا دارای قیمت است؟
- `price` (DecimalField) - قیمت پایه
- `price_per_unit` (PositiveIntegerField) - گام شمارش (مثلاً 1000)
- `description` (TextField)
- `is_active` (BooleanField)
- `has_quantity` (BooleanField) - آیا دارای تیراژ است؟
- `created_at`, `updated_at`

**روابط:**
- ManyToMany → `ProductCategory` (categories, through ProductCategoryRelation)
- OneToOne → `ProductPricingConfig` (pricing_config)
- OneToMany → `ProductSize` (product_size)
- OneToMany → `ProductQuantity` (product_quantity)
- OneToMany → `ProductOption` (options)
- OneToMany → `ProductImage` (product_image)
- OneToMany → `ProductAttachment` (product_attachment_product)

**میکسین‌ها:**
- `HasGuide` - راهنما و هشدار برای کاربر

**متدها:**
- `validate_has_price()` - اعتبارسنجی قیمت

**استفاده:**
```python
from core.models import Product

# دریافت محصول فعال با جزئیات
product = Product.objects.get_product_by_slug('business-card')
print(product.categories.all())
print(product.pricing_config)
```

---

### ProductPricingConfig (تنظیمات قیمت)

تنظیمات پیشرفته محاسبه قیمت برای محصول.

**فیلدهای کلیدی:**
- `product` (OneToOne → Product)
- `allow_custom_quantity` (BooleanField) - تیراژ دلخواه
- `min_quantity`, `max_quantity` (PositiveIntegerField) - محدودیت تیراژ
- `accepts_custom_dimensions` (BooleanField) - ابعاد دلخواه
- `min_width`, `max_width` (FloatField) - محدودیت ابعاد
- `base_setup_price` (DecimalField) - هزینه ثابت اولیه
- `design_service_available` (BooleanField) - خدمات طراحی
- `design_fee` (DecimalField) - هزینه طراحی

**استفاده:**
```python
product = Product.objects.get(id=1)
config = product.pricing_config
if config.accepts_custom_dimensions:
    # محاسبه قیمت با ابعاد دلخواه
    pass
```

---

### Size (سایز)

مدل سایزهای استاندارد.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User)
- `name` (CharField) - نام (مثلاً A4)
- `width` (FloatField) - عرض بر حسب سانتی‌متر
- `height` (FloatField) - طول بر حسب سانتی‌متر

---

### ProductSize (محصول-سایز)

جدول واسط برای اتصال Product و Size.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `size` (ForeignKey → Size)
- `price_impact` (DecimalField) - تأثیر بر قیمت (افزایش/کاهش)

**میکسین‌ها:**
- `HasGuide` - راهنمای انتخاب سایز

---

### Quantity (تیراژ)

مدل تیراژهای استاندارد.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User)
- `value` (PositiveIntegerField, unique) - مقدار تیراژ (مثلاً 1000)

---

### ProductQuantity (محصول-تیراژ)

جدول واسط برای اتصال Product و Quantity.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `quantity` (ForeignKey → Quantity)

---

### ProductOption (گزینه/ویژگی محصول)

تعریف ویژگی‌های قابل انتخاب برای محصول (مثل نوع کاغذ، نوع چاپ).

**ارث‌بری:** `BaseOptionDefinition` (که خود از `HasGuide` ارث می‌برد)

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `name` (CharField) - نام سیستمی (مثلاً paper_type)
- `label` (CharField) - عنوان نمایشی
- `input_type` (CharField) - نوع ورودی (text, select, checkbox, ...)
- `order` (IntegerField) - ترتیب نمایش

**روابط:**
- OneToMany → `ProductOptionValue` (choices)

**انواع input_type:**
- `text` - ورودی متنی
- `textarea` - متن بلند
- `number` - عددی
- `select` - لیست کشویی
- `radio` - رادیو باتن
- `checkbox` - چک‌باکس
- `multi_select` - انتخاب چندگانه

---

### ProductOptionValue (مقدار گزینه)

مقادیر قابل انتخاب برای هر ProductOption.

**ارث‌بری:** `BaseOptionValueDefinition` (که خود از `HasGuide` ارث می‌برد)

**فیلدهای کلیدی:**
- `option` (ForeignKey → ProductOption)
- `label` (CharField) - عنوان (مثلاً "کاغذ گلاسه")
- `value` (CharField) - کد سیستمی (مثلاً "glossy")
- `order` (IntegerField) - ترتیب نمایش

**روابط:**
- ForeignKey ← `ProductOptionPricingStrategy` (pricing_strategies)

---

### ProductOptionPricingStrategy (استراتژی قیمت‌گذاری گزینه)

تعیین تأثیر انتخاب هر مقدار گزینه بر قیمت نهایی.

**فیلدهای کلیدی:**
- `option_value` (ForeignKey → ProductOptionValue)
- `strategy_type` (CharField) - نوع استراتژی: fixed, percentage, per_unit
- `amount` (DecimalField) - مبلغ/درصد

---

### ProductImage (تصویر محصول)

تصاویر محصول.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `image` (ImageField)
- `order` (IntegerField) - ترتیب نمایش
- `is_primary` (BooleanField) - تصویر اصلی

---

### ProductAttachment (فایل پیوست محصول)

فایل‌های قابل دانلود مربوط به محصول (مثلاً راهنمای چاپ).

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `attachment` (ForeignKey → Attachment)
- `title` (CharField)
- `order` (IntegerField)

---

### Attachment (فایل پیوست)

مدل عمومی فایل‌های پیوست.

**فیلدهای کلیدی:**
- `file` (FileField)
- `title` (CharField)
- `created_at`

---

### ProductRating (امتیاز محصول)

امتیازدهی کاربران به محصول.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `user` (ForeignKey → User)
- `rating` (IntegerField) - امتیاز (1-5)
- `created_at`

**Constraint:** یک کاربر فقط یک بار به هر محصول امتیاز می‌دهد.

---

### ProductComment (نظرات محصول)

نظرات کاربران روی محصول.

**فیلدهای کلیدی:**
- `product` (ForeignKey → Product)
- `user` (ForeignKey → User)
- `comment` (TextField)
- `is_approved` (BooleanField) - تأیید ادمین
- `created_at`, `updated_at`

---

## 🛒 دامنه Order (سفارشات)

### OrderStatusGroup (گروه وضعیت سفارش)

گروه‌بندی وضعیت‌ها برای کنترل دسترسی (مثلاً "واحد طراحی"، "واحد چاپ").

**فیلدهای کلیدی:**
- `name` (CharField) - عنوان (مثلاً "واحد طراحی")
- `code` (SlugField, unique) - کد سیستمی (مثلاً "design")
- `description` (TextField)

**روابط:**
- OneToMany → `OrderStatus` (order_status)
- ManyToMany → `Role` (roles) - نقش‌های مجاز

**استفاده:**
```python
from core.models import OrderStatusGroup

design_group = OrderStatusGroup.objects.get(code='design')
statuses = design_group.order_status.all()
```

---

### OrderStatus (وضعیت سفارش)

وضعیت‌های مختلف سفارش در workflow.

**فیلدهای کلیدی:**
- `name` (CharField) - عنوان نمایشی
- `internal_code` (SlugField, unique) - کد سیستمی (تولید خودکار)
- `status_type` (CharField) - نوع: initial, progress, approve, reject, cancel
- `sort_order` (PositiveIntegerField) - ترتیب نمایش
- `group` (ForeignKey → OrderStatusGroup)
- `description` (TextField)

**فرمت internal_code:** `{NAME}_{TYPE}_{GROUP}` (مثلاً DESIGN_REVIEW_PROGRESS_DESIGN)

**روابط:**
- OneToMany → `Order` (orders)

**متدها:**
- `clean()` - اعتبارسنجی (فقط یک initial status در هر گروه)

---

### Order (سفارش)

مدل اصلی سفارش - نقطه ثقل سیستم.

**فیلدهای کلیدی:**
- `user` (ForeignKey → User, nullable) - مشتری (nullable برای مهمان)
- `order_code` (CharField, unique) - کد پیگیری (تولید خودکار)
- `type` (CharField) - نوع: "1" (معمولی), "2" (اختصاصی)
- `current_status` (ForeignKey → OrderStatus)
- `recipient_name` (CharField, nullable) - نام گیرنده
- `recipient_phone` (CharField, nullable) - شماره تماس
- `company_name` (CharField, nullable) - نام شرکت
- `full_address` (TextField, nullable) - آدرس کامل متنی
- `address` (ForeignKey → Address, nullable) - آدرس از سیستم
- `total_price` (DecimalField) - مبلغ کل سفارش
- `base_products_price` (DecimalField) - مبلغ پایه اقلام
- `created_at`, `updated_at`

**روابط:**
- OneToMany → `OrderItem` (order_item_order)
- OneToOne → `Invoice` (invoice)

**Properties:**
- `items_count` - تعداد آیتم‌ها
- `is_locked` - آیا سفارش قفل است؟

**استفاده:**
```python
from core.models import Order

# دریافت سفارش با جزئیات
order = Order.objects.get_order_with_items(user_id=1, order_id=123)
print(order.order_code)
print(order.items_count)
for item in order.order_item_order.all():
    print(item.product.name, item.quantity, item.price)
```

---

### OrderItem (آیتم سفارش)

هر آیتم در سفارش.

**فیلدهای کلیدی:**
- `order` (ForeignKey → Order)
- `product` (ForeignKey → Product, nullable) - nullable برای سفارشات اختصاصی
- `name` (CharField, nullable) - نام آیتم (برای سفارشات اختصاصی)
- `quantity` (PositiveIntegerField) - تعداد
- `price` (DecimalField) - قیمت نهایی این آیتم
- `status` (CharField) - وضعیت: pending, approved, rejected, cancelled
- `items` (JSONField) - ویژگی‌های انتخاب شده (سایز، جنس، آپشن‌ها)
- `description` (TextField, nullable) - توضیحات مشتری
- `admin_note` (TextField) - یادداشت اپراتور
- `created_at`, `updated_at`

**روابط:**
- OneToMany → `OrderItemFile` (files)

**نکته:** فیلد `items` (JSONField) تمام اطلاعات انتخاب شده توسط کاربر را ذخیره می‌کند:
```json
{
  "size": {"id": 1, "name": "A4"},
  "material": {"id": 2, "name": "گلاسه"},
  "options": {
    "paper_type": "glossy",
    "finish": "matte"
  },
  "custom_dimensions": {"width": 50, "height": 30}
}
```

---

### OrderItemFile (فایل طراحی آیتم)

فایل‌های طراحی مربوط به هر آیتم سفارش (با نسخه‌بندی).

**فیلدهای کلیدی:**
- `order_item` (ForeignKey → OrderItem)
- `file` (FileField)
- `version` (IntegerField) - نسخه فایل
- `is_latest` (BooleanField) - آخرین نسخه
- `uploaded_by` (ForeignKey → User, nullable)
- `uploaded_at` (DateTimeField)

**نکته:** برای هر آیتم، فقط یک فایل با `is_latest=True` وجود دارد.

---

## 💰 دامنه Financial (مالی)

### Invoice (فاکتور)

فاکتور مرتبط با سفارش.

**فیلدهای کلیدی:**
- `order` (OneToOne → Order)
- `invoice_number` (CharField, unique) - شماره فاکتور
- `status` (CharField) - وضعیت: PENDING, PAID_PARTIAL, PAID_FULL, CANCELED, FINALIZE
- `items_amount` (DecimalField) - جمع اقلام
- `services_amount` (DecimalField) - جمع خدمات
- `tax_amount` (DecimalField) - مالیات
- `discount_amount` (DecimalField) - تخفیف
- `final_amount` (DecimalField) - مبلغ قابل پرداخت
- `paid_amount` (DecimalField) - مبلغ پرداخت شده
- `issued_at` (DateTimeField) - تاریخ صدور
- `due_date` (DateTimeField, nullable) - سررسید
- `finalized_at` (DateTimeField, nullable) - تاریخ قطعی شدن

**Properties:**
- `remaining_amount` - مبلغ باقیمانده
- `is_paid` - آیا پرداخت شده است؟

**روابط:**
- OneToMany → `InvoiceItem` (items)

---

### InvoiceItem (آیتم فاکتور)

آیتم‌های فاکتور.

**فیلدهای کلیدی:**
- `invoice` (ForeignKey → Invoice)
- `description` (CharField) - توضیحات
- `quantity` (DecimalField) - تعداد
- `unit_price` (DecimalField) - قیمت واحد
- `total_price` (DecimalField) - قیمت کل

---

### Quotation (پیش‌فاکتور)

پیش‌فاکتور مستقل (می‌تواند به سفارش تبدیل شود).

**فیلدهای کلیدی:**
- `quotation_number` (CharField, unique) - شماره پیش‌فاکتور
- `created_by` (ForeignKey → User, nullable) - ایجادکننده
- `converted_order` (OneToOne → Order, nullable) - سفارش تبدیل شده
- `customer_name` (CharField) - نام مشتری
- `product_name` (CharField) - نام محصول
- `status` (CharField) - وضعیت: draft, sent, accepted, rejected, expired, converted
- `total_amount` (DecimalField) - مبلغ کل
- `valid_until` (DateTimeField, nullable) - اعتبار تا تاریخ
- `created_at`, `updated_at`

---

## 🔗 روابط کلیدی بین دامنه‌ها

### دیاگرام روابط اصلی:

```
User
 ├── OneToOne → CustomerProfile
 ├── OneToOne → Wallet
 ├── OneToMany → Address
 ├── OneToMany → Order
 └── ManyToMany → Role (through UserRole)

Product
 ├── ManyToMany → ProductCategory (through ProductCategoryRelation)
 ├── OneToOne → ProductPricingConfig
 ├── OneToMany → ProductSize, ProductQuantity, ProductOption
 └── OneToMany → ProductImage, ProductAttachment

Order
 ├── ForeignKey → User
 ├── ForeignKey → OrderStatus
 ├── ForeignKey → Address
 ├── OneToMany → OrderItem
 └── OneToOne → Invoice

OrderItem
 ├── ForeignKey → Order
 ├── ForeignKey → Product (nullable)
 └── OneToMany → OrderItemFile
```

---

## 📝 نکات مهم

### 1. کدهای خودکار

- **کد محصول:** به صورت خودکار پس از اختصاص دسته‌بندی تولید می‌شود (Signal)
- **کد سفارش:** به صورت خودکار در زمان ایجاد سفارش تولید می‌شود
- **کد وضعیت:** به صورت خودکار در `save()` تولید می‌شود

### 2. JSONField

فیلد `items` در `OrderItem` و `CartItem` از JSONField استفاده می‌کند تا ویژگی‌های انتخاب شده را ذخیره کند. این طراحی انعطاف‌پذیری بالایی دارد.

### 3. Soft Delete

در حال حاضر از Soft Delete استفاده نمی‌شود. حذف رکوردها واقعی است (CASCADE).

### 4. Timestamps

تمامی مدل‌ها دارای `created_at` و `updated_at` هستند (به صورت خودکار).

### 5. Multi-tenancy

مدل‌ها به صورت مستقیم Multi-tenancy ندارند، اما بسیاری از مدل‌ها دارای فیلد `user` برای مشخص کردن ایجادکننده هستند.

---

## 🎯 بهترین روش‌ها

### ✅ انجام دهید:

1. **استفاده از Repository:**
   ```python
   # ✅ صحیح
   product = Product.objects.get_product_by_slug('slug')
   
   # ❌ غلط
   product = Product.objects.get(slug='slug')
   ```

2. **استفاده از select_related و prefetch_related:**
   ```python
   # ✅ صحیح (در Repository)
   products = Product.objects.select_related('pricing_config').prefetch_related('categories')
   ```

3. **استفاده از Transaction برای عملیات چند مرحله‌ای:**
   ```python
   @transaction.atomic
   def create_order(...):
       # عملیات چند مرحله‌ای
   ```

### ❌ انجام ندهید:

1. ❌ کوئری مستقیم بدون استفاده از Repository
2. ❌ N+1 Query
3. ❌ تغییر مستقیم مدل‌ها در View
4. ❌ حذف cascade بدون بررسی

---

## 📚 منابع بیشتر

- [ARCHITECTURE.md](./ARCHITECTURE.md) - معماری و الگوهای طراحی
- [SERVICES.md](./SERVICES.md) - سرویس‌ها و منطق تجاری
- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)

---

**آخرین به‌روزرسانی:** ۱۴۰۴

