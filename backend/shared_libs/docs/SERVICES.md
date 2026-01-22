# مستندات سرویس‌های دامنه (Domain Services)

## 📖 مقدمه

سرویس‌های دامنه (Domain Services) قلب تپنده سیستم Printoo24 هستند. این سرویس‌ها منطق تجاری (Business Logic) را کپسوله می‌کنند و از Repositoryها برای دسترسی به داده استفاده می‌کنند.

**ویژگی‌های کلیدی:**
- ✅ مستقل از لایه نمایش (بدون وابستگی به Request/Response)
- ✅ قابل تست (Unit Testing)
- ✅ قابل استفاده مجدد در admin_site و customer_site
- ✅ استفاده از Transaction برای عملیات چند مرحله‌ای

---

## 🏗️ ساختار کلی

هر دامنه دارای سرویس‌های تخصصی خود است:

```
domain/
├── services/
│   ├── __init__.py
│   ├── service_name.py      # سرویس‌های مختلف
│   └── ...
```

---

## 👤 دامنه Users (کاربران)

### UserIdentityService

**مسئولیت:** مدیریت هویت و عملیات سمت مشتری (Customer-Facing)

**متدهای کلیدی:**

#### `register_new_customer(data: Dict) -> User`
ثبت نام مشتری جدید با بررسی یکتایی.

```python
from core.users.services import UserIdentityService

service = UserIdentityService()
user = service.register_new_customer({
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'secure_password'
})
```

**نکته:** این متد به صورت `@transaction.atomic` است تا در صورت خطا، تمام تغییرات rollback شوند.

#### `check_uniqueness(username, email, exclude_user_id)`
بررسی یکتایی نام کاربری و ایمیل.

```python
try:
    service.check_uniqueness(username='testuser', email='test@example.com')
except UsernameAlreadyExistsException:
    # مدیریت خطا
    pass
```

#### `verify_user(user: User) -> User`
تأیید حساب کاربری (فعال‌سازی).

```python
user = service.verify_user(user)
# user.is_verified = True
# user.is_active = True
```

#### `update_profile_credentials(user, data) -> User`
ویرایش اطلاعات حساس (نام کاربری/ایمیل).

#### `change_password(user, new_password)`
تغییر رمز عبور.

---

### CustomerService

**مسئولیت:** مدیریت مشتریان (توسط ادمین یا سیستم)

**متدهای کلیدی:**

#### `get_all_customers() -> QuerySet`
دریافت لیست تمام مشتریان.

```python
from core.users.services import CustomerService

service = CustomerService()
customers = service.get_all_customers()
```

#### `get_customer_by_id(user_id: int) -> User`
دریافت یک مشتری خاص با پروفایل کامل.

```python
customer = service.get_customer_by_id(user_id=1)
print(customer.customer_profile.fullname())
```

#### `create_customer(data: Dict) -> User`
ایجاد مشتری جدید (شامل User، Profile، Role، Wallet).

**مراحل:**
1. بررسی یکتایی ایمیل
2. ایجاد User
3. ایجاد CustomerProfile
4. تخصیص نقش مشتری
5. ایجاد Wallet (از طریق Signal)

```python
customer = service.create_customer({
    'username': 'customer1',
    'email': 'customer@example.com',
    'password': 'password',
    'first_name': 'نام',
    'last_name': 'نام خانوادگی',
    'phone_number': '09123456789'
})
```

#### `update_customer(user_id, data) -> User`
ویرایش اطلاعات مشتری (شامل User و Profile).

---

### CustomerProfileService

**مسئولیت:** مدیریت منطق پروفایل کاربر

**متدهای کلیدی:**

#### `get_or_create_profile(user) -> CustomerProfile`
تضمین وجود پروفایل برای کاربر.

```python
from core.users.services import CustomerProfileService

service = CustomerProfileService()
profile = service.get_or_create_profile(user)
```

#### `update_profile(user, data) -> CustomerProfile`
ویرایش اطلاعات پروفایل با اعمال قوانین بیزنس.

**فیلدهای قابل ویرایش:**
- `first_name`
- `last_name`
- `phone_number`
- `company`
- `bio`

---

### UserAdminService

**مسئولیت:** مدیریت کارکنان (توسط ادمین)

**متدهای کلیدی:**

#### `create_staff(data, role_id) -> User`
استخدام کارمند جدید.

```python
from core.users.services import UserAdminService

service = UserAdminService()
staff = service.create_staff({
    'username': 'staff1',
    'email': 'staff@example.com',
    'password': 'temp_password'
}, role_id=1)
```

#### `update_staff(user_id, data, role_id) -> User`
ویرایش اطلاعات کارمند.

---

### RoleAdminService

**مسئولیت:** مدیریت نقش‌ها و دسترسی‌ها

**متدهای کلیدی:**
- `create_role(data) -> Role`
- `update_role(role_id, data) -> Role`
- `assign_permissions_to_role(role_id, permission_ids)`

---

## 📦 دامنه Product (محصولات)

### ProductService

**مسئولیت:** مدیریت منطق محصولات

**متدهای کلیدی:**

#### `get_all_active_products() -> QuerySet`
دریافت تمام محصولات فعال.

```python
from core.product.services import ProductService

service = ProductService()
products = service.get_all_active_products()
```

#### `get_product_detail_by_slug(slug: str) -> Dict`
دریافت جزئیات کامل محصول با اسلاگ.

```python
result = service.get_product_detail_by_slug('business-card')
product = result['product']
# product شامل تمام روابط (categories, options, images, ...)
```

#### `get_product_detail_by_id(product_id: int) -> Dict`
دریافت جزئیات کامل محصول با ID.

#### `create_product_shell(user, data) -> Product`
ایجاد محصول اولیه (پوسته).

**مراحل:**
1. ایجاد Product
2. اختصاص دسته‌بندی‌ها
3. ایجاد ProductPricingConfig

```python
product = service.create_product_shell(user, {
    'name': 'کارت ویزیت',
    'price': 10000,
    'category_ids': [1, 2],
    'has_price': True
})
```

#### `update_product_shell(pk, data) -> Product`
ویرایش محصول.

#### `sync_sizes(product_id, user, size_configs)`
همگام‌سازی سایزهای محصول (Full Sync Strategy).

```python
service.sync_sizes(product_id=1, user=user, size_configs=[
    {'id': 1, 'price_impact': 5000},
    {'id': 2, 'price_impact': 0}
])
```

**نکته:** این متد سایزهای قبلی را حذف و جدید‌ها را ایجاد می‌کند.

---

### ProductPriceCalculator

**مسئولیت:** موتور محاسبه قیمت محصول

این سرویس یکی از پیچیده‌ترین بخش‌های سیستم است و قیمت نهایی را بر اساس:
- قیمت پایه محصول
- تیراژ (Quantity)
- ابعاد (Width, Height)
- سایز انتخابی
- گزینه‌های انتخابی (Options)
- هزینه‌های سربار (Setup, Design)

محاسبه می‌کند.

**مثال استفاده:**

```python
from core.product.services import ProductPriceCalculator

calculator = ProductPriceCalculator(
    product=product,
    quantity=1000,
    width=50,  # سانتی‌متر
    height=30,  # سانتی‌متر
    selected_values=option_values,  # لیست ProductOptionValue
    selected_size_id=1,
    has_design=True  # آیا کاربر فایل دارد؟
)

result = calculator.calculate()
# {
#     "final_price": 150000.0,
#     "breakdown": {
#         "base_price": 100000,
#         "size_impact": 10000,
#         "options_impact": 20000,
#         "setup_cost": 15000,
#         "design_cost": 5000,
#         "quantity_multiplier": 1.0
#     }
# }
```

**منطق محاسبه:**

1. **محاسبه قیمت پایه برای یک واحد:**
   - استفاده از `price_per_unit` (مثلاً 1000)
   - محاسبه ضریب تیراژ: `quantity / price_per_unit`

2. **محاسبه هزینه گزینه‌ها:**
   - جمع تأثیر تمام گزینه‌های انتخابی

3. **محاسبه قیمت کل اقلام:**
   - `(base_unit_cost + options_unit_cost) * qty_multiplier`

4. **هزینه‌های سربار:**
   - `base_setup_price` (یکبار)
   - `design_fee` (اگر کاربر فایل ندارد)

5. **اعمال مودیفایر درصدی:**
   - `price_modifier_percent` (تخفیف یا افزایش کلی)

6. **گرد کردن نهایی:**
   - به نزدیک‌ترین 100 تومان

---

### SizeService

**مسئولیت:** مدیریت منطق سایزها

**متدهای کلیدی:**
- `get_all() -> QuerySet`
- `get_by_id(size_id) -> Size`
- `create_size(user, data) -> Size`
- `update_size(size_id, data) -> Size`
- `delete_size(size_id)`

---

### QuantityService

**مسئولیت:** مدیریت منطق تیراژها

**متدهای کلیدی:**
- `get_all() -> QuerySet`
- `create_quantity(user, value) -> Quantity`
- `update_quantity(quantity_id, value) -> Quantity`

---

### OptionService

**مسئولیت:** مدیریت منطق گزینه‌ها و ویژگی‌ها

**متدهای کلیدی:**
- `create_option(product_id, data) -> ProductOption`
- `update_option(option_id, data) -> ProductOption`
- `add_option_value(option_id, data) -> ProductOptionValue`

---

### FeedbackService

**مسئولیت:** مدیریت نظرات و امتیازدهی

**متدهای کلیدی:**
- `create_rating(product_id, user_id, rating) -> ProductRating`
- `create_comment(product_id, user_id, comment) -> ProductComment`
- `get_product_feedback(product_id) -> Dict`

---

## 🛒 دامنه Order (سفارشات)

### OrderService

**مسئولیت:** مدیریت منطق سفارشات

**متدهای کلیدی:**

#### `get_order_details(user_id, order_id) -> Order`
دریافت جزئیات سفارش برای کاربر.

```python
from core.order.services import OrderService
from core.order.exceptions import OrderNotFoundException

service = OrderService()
try:
    order = service.get_order_details(user_id=1, order_id=123)
    print(order.order_code)
    for item in order.order_item_order.all():
        print(item.product.name, item.quantity)
except OrderNotFoundException:
    # مدیریت خطا
    pass
```

#### `get_user_orders_summary(user_id) -> List[Order]`
دریافت خلاصه سفارشات کاربر.

```python
orders = service.get_user_orders_summary(user_id=1)
for order in orders:
    print(order.order_code, order.total_price, order.current_status.name)
```

#### `create_order_direct(user_id, address_id, items_data, total_price_override) -> Order`
ایجاد مستقیم سفارش (توسط ادمین) بدون استفاده از سبد خرید.

**ورودی:**
```python
items_data = [
    {
        'product_slug': 'business-card',
        'item_price': 100000,  # اختیاری
        'selections': {
            'quantity': 1000,
            'size_id': 1,
            'options': {...},
            'name': 'نام سفارش',
            'description': 'توضیحات'
        }
    }
]
```

**مراحل:**
1. دریافت و اعتبارسنجی کاربر و آدرس
2. دریافت وضعیت اولیه
3. استخراج و اعتبارسنجی آیتم‌ها
4. محاسبه قیمت
5. ایجاد Order (Atomic)
6. ایجاد OrderItemها
7. بازگرداندن Order

**نکته:** این متد به صورت `@transaction.atomic` است.

---

## 🏗️ Infrastructure Services (زیرساخت)

### CacheService

**مسئولیت:** مدیریت کش سیستم

**متدهای کلیدی:**

```python
from core.infrastructure.cache import CacheService

cache = CacheService()

# ذخیره
cache.set('key', 'value', timeout=3600)  # timeout اختیاری

# دریافت
value = cache.get('key', default=None)

# حذف
cache.delete('key')
```

**استفاده:**
```python
# ذخیره لیست محصولات صفحه اول
cache.set('homepage_products', products_list, timeout=1800)

# دریافت
products = cache.get('homepage_products')
if not products:
    products = fetch_products_from_db()
    cache.set('homepage_products', products, timeout=1800)
```

---

### EmailService

**مسئولیت:** ارسال ایمیل

**متدهای کلیدی:**

```python
from core.infrastructure.email import EmailService

email_service = EmailService()

email_service.send(
    subject='خوش‌آمدید',
    template_name='emails/welcome.html',
    context={'user': user, 'activation_link': link},
    from_email='noreply@printoo24.com',
    to_email=user.email
)
```

**ویژگی‌ها:**
- تولید خودکار نسخه HTML و Text
- استفاده از Django Templates
- پشتیبانی از Context برای متغیرهای دینامیک

---

## 🔄 الگوهای استفاده

### 1. استفاده در View (API)

```python
# customer_site/api/v1/products/views.py
from rest_framework.views import APIView
from core.product.services import ProductService
from core.product.exceptions import ProductNotFoundException

class ProductDetailView(APIView):
    def get(self, request, slug):
        service = ProductService()
        try:
            result = service.get_product_detail_by_slug(slug)
            serializer = ProductSerializer(result['product'])
            return Response(serializer.data)
        except ProductNotFoundException:
            return Response({'error': 'محصول یافت نشد'}, status=404)
```

### 2. استفاده در View دیگر (Admin)

```python
# admin_site/api/v1/products/views.py
from core.product.services import ProductService

class ProductCreateView(APIView):
    def post(self, request):
        service = ProductService()
        product = service.create_product_shell(
            user=request.user,
            data=request.data
        )
        return Response({'id': product.id}, status=201)
```

### 3. استفاده در Management Commands

```python
# core/management/commands/seed_products.py
from core.product.services import ProductService

class Command(BaseCommand):
    def handle(self, *args, **options):
        service = ProductService()
        product = service.create_product_shell(user, data)
        # ...
```

---

## ⚠️ مدیریت خطاها

### Exceptionهای اختصاصی

هر دامنه Exceptionهای اختصاصی خود را دارد:

```python
# Users
from core.users.exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
    UserNotFoundException
)

# Product
from core.product.exceptions import (
    ProductNotFoundException,
    ProductCategoryNotFoundException,
    InvalidProductDataException
)

# Order
from core.order.exceptions import (
    OrderNotFoundException,
    InvalidOrderOperationException
)
```

### الگوی استفاده

```python
from core.product.services import ProductService
from core.product.exceptions import ProductNotFoundException

service = ProductService()
try:
    product = service.get_product_detail_by_slug('slug')
except ProductNotFoundException as e:
    # مدیریت خطا
    return Response({'error': str(e)}, status=404)
```

---

## 🔐 مدیریت تراکنش‌ها

### استفاده از @transaction.atomic

برای عملیات چند مرحله‌ای، از `@transaction.atomic` استفاده می‌شود:

```python
from django.db import transaction

class OrderService:
    @transaction.atomic
    def create_order(self, user, items):
        # اگر هر کدام از این خطوط fail شود، همه rollback می‌شوند
        order = Order.objects.create(...)
        for item in items:
            OrderItem.objects.create(order=order, ...)
        Wallet.objects.deduct(user, order.total_price)
        return order
```

**نکته:** در صورت خطا، تمام تغییرات در دیتابیس rollback می‌شوند.

---

## ✅ بهترین روش‌ها

### ✅ انجام دهید:

1. **همیشه از Services استفاده کنید:**
   ```python
   # ✅ صحیح
   service = ProductService()
   product = service.get_product_detail_by_slug('slug')
   
   # ❌ غلط
   product = Product.objects.get(slug='slug')
   ```

2. **مدیریت Exceptionها:**
   ```python
   # ✅ صحیح
   try:
       product = service.get_product_detail_by_slug('slug')
   except ProductNotFoundException:
       return Response({'error': 'یافت نشد'}, status=404)
   ```

3. **استفاده از Transaction برای عملیات چند مرحله‌ای:**
   ```python
   @transaction.atomic
   def create_order(...):
       # عملیات چند مرحله‌ای
   ```

### ❌ انجام ندهید:

1. ❌ دسترسی مستقیم به Repository در View
2. ❌ منطق تجاری در View
3. ❌ عدم مدیریت Exceptionها
4. ❌ تراکنش‌های ناامن
5. ❌ وابستگی Service به Request/Response

---

## 📚 منابع بیشتر

- [ARCHITECTURE.md](./ARCHITECTURE.md) - معماری و الگوهای طراحی
- [MODELS.md](./MODELS.md) - مستندات مدل‌ها
- [README.md](./README.md) - راهنمای شروع

---

**آخرین به‌روزرسانی:** ۱۴۰۴

