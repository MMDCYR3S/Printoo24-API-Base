# مستندات اپلیکیشن Cart

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌ها](#مدل‌ها)
4. [سرویس‌ها](#سرویس‌ها)
5. [ابزارهای کمکی](#ابزارهای-کمکی)
6. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن cart مسئول مدیریت کامل سبد خرید کاربران است. این اپلیکیشن شامل عملیات افزودن، بروزرسانی، حذف و اعتبارسنجی آیتم‌های سبد خرید می‌باشد. همچنین مدیریت فایل‌های آپلودی مرتبط با محصولات را نیز انجام می‌دهد.

---

## ساختار فایل‌ها

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
    └── ...
```

---

## مدل‌ها

### 📍 موقعیت: `backend/apps/cart/models.py`

### توضیحات:
مدل‌های دیتابیس مربوط به سبد خرید.

#### 1. **Cart**
**توضیحات:**
مدل اصلی سبد خرید کاربر.

**فیلدهای اصلی:**
```python
class Cart(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # وضعیت سبد
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('converted', 'تبدیل به سفارش'),
        ('abandoned', 'رها شده'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
```

**ویژگی‌ها:**
- هر کاربر فقط یک سبد خرید فعال دارد
- با تبدیل به سفارش، وضعیت به `converted` تغییر می‌کند

#### 2. **CartItem**
**توضیحات:**
آیتم‌های موجود در سبد خرید.

**فیلدهای اصلی:**
```python
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=1)
    
    # قیمت در زمان افزودن (برای جلوگیری از تغییرات قیمت)
    unit_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0
    )
    
    # ویژگی‌های انتخابی محصول
    selected_options = models.JSONField(
        default=dict,
        blank=True
    )
    
    # فایل‌های آپلودی (در صورت نیاز)
    uploaded_files = models.JSONField(
        default=list,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**ویژگی‌ها:**
- قیمت محصول در زمان افزودن ذخیره می‌شود
- ویژگی‌های انتخابی به صورت JSON ذخیره می‌شوند
- فایل‌های آپلودی به صورت لیست URL ذخیره می‌شوند

---

## managers.py

### 📍 موقعیت: `backend/apps/cart/managers.py`

### توضیحات:
منیجرهای سفارشی برای مدل‌های cart.

**منیجرهای اصلی:**

```python
class CartManager(BaseManager):
    def get_user_cart(self, user: User) -> Cart:
        """دریافت سبد خرید فعال کاربر"""
        pass
    
    def get_active_carts(self) -> QuerySet:
        """دریافت تمام سبدهای خرید فعال"""
        pass

class CartItemManager(BaseManager):
    def get_cart_items(self, cart: Cart) -> QuerySet:
        """دریافت تمام آیتم‌های سبد"""
        pass
    
    def get_item_by_product(self, cart: Cart, product_id: int) -> CartItem:
        """دریافت آیتم بر اساس محصول"""
        pass
```

---

## exceptions.py

### 📍 موقعیت: `backend/apps/cart/exceptions.py`

### توضیحات:
Exceptionهای سفارشی برای اپلیکیشن cart.

**Exceptionهای اصلی:**
```python
class CartError(Exception):
    """خطای عمومی سبد خرید"""
    pass

class CartNotFoundError(CartError):
    """سبد خرید پیدا نشد"""
    pass

class InsufficientStockError(CartError):
    """موجودی کافی نیست"""
    pass

class InvalidProductError(CartError):
    """محصول نامعتبر"""
    pass

class CartItemNotFoundError(CartError):
    """آیتم سبد خرید پیدا نشد"""
    pass

class CartValidationError(CartError):
    """خطا در اعتبارسنجی سبد"""
    pass
```

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/cart/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن cart که منطق تجاری مربوط به سبد خرید را پیاده‌سازی می‌کنند.

---

### add_to_cart_service.py

#### 📍 موقعیت: `backend/apps/cart/services/add_to_cart_service.py`

#### هدف:
افزودن محصول به سبد خرید.

#### کلاس اصلی: `AddToCartService`

**متدهای اصلی:**

```python
class AddToCartService:
    def add_item(self, 
                user: User, 
                product_id: int, 
                quantity: int = 1, 
                selected_options: dict = None,
                uploaded_files: list = None) -> CartItem:
        """
        افزودن محصول به سبد خرید
        
        Args:
            user: کاربر
            product_id: ID محصول
            quantity: تعداد
            selected_options: ویژگی‌های انتخابی
            uploaded_files: فایل‌های آپلودی
        
        Returns:
            CartItem: آیتم ایجاد شده
        
        Raises:
            InvalidProductError: اگر محصول وجود نداشته باشد
            InsufficientStockError: اگر موجودی کافی نباشد
            CartValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def get_or_create_cart(self, user: User) -> Cart:
        """
        دریافت یا ایجاد سبد خرید برای کاربر
        
        Args:
            user: کاربر
        
        Returns:
            Cart: سبد خرید
        """
        pass
```

**فرآیند افزودن به سبد:**
```
1. دریافت سبد خرید کاربر (یا ایجاد جدید)
2. بررسی وجود محصول
3. بررسی فعال بودن محصول
4. بررسی موجودی محصول
5. محاسبه قیمت نهایی با ویژگی‌های انتخابی
6. ایجاد CartItem
7. بروزرسانی قیمت‌ها
8. برگرداندن آیتم ایجاد شده
```

**مثال استفاده:**
```python
from apps.cart.services.add_to_cart_service import AddToCartService

service = AddToCartService()

# افزودن محصول ساده
cart_item = service.add_item(
    user=user,
    product_id=123,
    quantity=2
)

# افزودن محصول با ویژگی‌های انتخابی
cart_item = service.add_item(
    user=user,
    product_id=456,
    quantity=1,
    selected_options={
        'size': 'large',
        'color': 'red'
    }
)

# افزودن محصول با فایل
cart_item = service.add_item(
    user=user,
    product_id=789,
    quantity=1,
    uploaded_files=[
        'https://example.com/uploads/file1.pdf'
    ]
)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.add_to_cart')
```

---

### cart_item_service.py

#### 📍 موقعیت: `backend/apps/cart/services/cart_item_service.py`

#### هدف:
مدیریت آیتم‌های سبد خرید.

#### کلاس اصلی: `CartItemService`

**متدهای اصلی:**

```python
class CartItemService:
    def get_cart_items(self, user: User) -> QuerySet:
        """
        دریافت تمام آیتم‌های سبد خرید کاربر
        
        Args:
            user: کاربر
        
        Returns:
            QuerySet: آیتم‌های سبد
        """
        pass
    
    def get_cart_item(self, user: User, item_id: int) -> CartItem:
        """
        دریافت یک آیتم خاص
        
        Args:
            user: کاربر
            item_id: ID آیتم
        
        Returns:
            CartItem: آیتم
        
        Raises:
            CartItemNotFoundError: اگر آیتم وجود نداشته باشد
        """
        pass
    
    def get_cart_total(self, user: User) -> dict:
        """
        محاسبه مجموع سبد خرید
        
        Args:
            user: کاربر
        
        Returns:
            dict: {
                'subtotal': Decimal,
                'tax': Decimal,
                'total': Decimal,
                'items_count': int
            }
        """
        pass
```

**مثال استفاده:**
```python
from apps.cart.services.cart_item_service import CartItemService

service = CartItemService()

# دریافت تمام آیتم‌ها
items = service.get_cart_items(user)

# دریافت یک آیتم
item = service.get_cart_item(user, item_id=123)

# محاسبه مجموع
total = service.get_cart_total(user)
print(f"جمع کل: {total['total']} تومان")
print(f"تعداد آیتم‌ها: {total['items_count']}")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.list')
logger = logging.getLogger('cart.services.detail')
```

---

### cart_item_upload_service.py

#### 📍 موقعیت: `backend/apps/cart/services/cart_item_upload_service.py`

#### هدف:
مدیریت فایل‌های آپلودی مرتبط با آیتم‌های سبد خرید.

#### کلاس اصلی: `CartItemUploadService`

**متدهای اصلی:**

```python
class CartItemUploadService:
    def upload_file(self, 
                   cart_item: CartItem, 
                   file) -> str:
        """
        آپلود فایل برای آیتم سبد
        
        Args:
            cart_item: آیتم سبد
            file: فایل آپلودی
        
        Returns:
            str: URL فایل آپلود شده
        
        Raises:
            ValidationError: اگر فایل نامعتبر باشد
        """
        pass
    
    def delete_file(self, file_url: str) -> bool:
        """
        حذف فایل آپلود شده
        
        Args:
            file_url: URL فایل
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def validate_file(self, file) -> bool:
        """
        اعتبارسنجی فایل
        
        Args:
            file: فایل
        
        Returns:
            bool: آیا فایل معتبر است
        
        Raises:
            ValidationError: اگر فایل نامعتبر باشد
        """
        pass
```

**مثال استفاده:**
```python
from apps.cart.services.cart_item_upload_service import CartItemUploadService

service = CartItemUploadService()

# آپلود فایل
file_url = service.upload_file(
    cart_item=cart_item,
    file=request.FILES['file']
)

# حذف فایل
service.delete_file(file_url)
```

**قابلیت‌های آپلود:**
- ✅ پشتیبانی از فرمت‌های مختلف (PDF, JPG, PNG, ...)
- ✅ محدودیت حجم فایل (مثلاً 10MB)
- ✅ ذخیره در پوشه موقت تا تبدیل به سفارش
- ✅ پس از تبدیل به سفارش، فایل‌ها به پوشه دائمی منتقل می‌شوند

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.file_upload')
logger = logging.getLogger('cart.services.temp_file')
```

---

### cart_validator_service.py

#### 📍 موقعیت: `backend/apps/cart/services/cart_validator_service.py`

#### هدف:
اعتبارسنجی سبد خرید قبل از تبدیل به سفارش.

#### کلاس اصلی: `CartValidatorService`

**متدهای اصلی:**

```python
class CartValidatorService:
    def validate_cart(self, user: User) -> ValidationResult:
        """
        اعتبارسنجی کامل سبد خرید
        
        Args:
            user: کاربر
        
        Returns:
            ValidationResult: {
                'is_valid': bool,
                'errors': list,
                'warnings': list
            }
        """
        pass
    
    def check_stock(self, cart_items: QuerySet) -> bool:
        """
        بررسی موجودی تمام آیتم‌ها
        
        Args:
            cart_items: آیتم‌های سبد
        
        Returns:
            bool: آیا موجودی کافی است
        
        Raises:
            InsufficientStockError: اگر موجودی کافی نباشد
        """
        pass
    
    def check_product_availability(self, product_id: int) -> bool:
        """
        بررسی فعال بودن محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            bool: آیا محصول فعال است
        """
        pass
    
    def validate_options(self, product_id: int, selected_options: dict) -> bool:
        """
        اعتبارسنجی ویژگی‌های انتخابی
        
        Args:
            product_id: ID محصول
            selected_options: ویژگی‌های انتخابی
        
        Returns:
            bool: آیا ویژگی‌ها معتبر هستند
        """
        pass
```

**فرآیند اعتبارسنجی:**
```
1. بررسی خالی نبودن سبد خرید
2. برای هر آیتم:
   - بررسی فعال بودن محصول
   - بررسی موجودی محصول
   - بررسی اعتبار ویژگی‌های انتخابی
   - بررسی اعتبار فایل‌های آپلودی
3. بررسی آدرس ارسال کاربر
4. برگرداندن نتیجه اعتبارسنجی
```

**مثال استفاده:**
```python
from apps.cart.services.cart_validator_service import CartValidatorService

service = CartValidatorService()

# اعتبارسنجی سبد
result = service.validate_cart(user)

if result.is_valid:
    print("سبد خرید معتبر است")
else:
    for error in result.errors:
        print(f"خطا: {error}")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.cart_validator')
```

---

### delete_cart_service.py

#### 📍 موقعیت: `backend/apps/cart/services/delete_cart_service.py`

#### هدف:
حذف آیتم از سبد خرید یا پاک کردن کامل سبد.

#### کلاس اصلی: `DeleteCartService`

**متدهای اصلی:**

```python
class DeleteCartService:
    def remove_item(self, user: User, item_id: int) -> bool:
        """
        حذف آیتم از سبد خرید
        
        Args:
            user: کاربر
            item_id: ID آیتم
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            CartItemNotFoundError: اگر آیتم وجود نداشته باشد
        """
        pass
    
    def clear_cart(self, user: User) -> bool:
        """
        پاک کردن کامل سبد خرید
        
        Args:
            user: کاربر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def remove_items_by_product(self, user: User, product_id: int) -> int:
        """
        حذف تمام آیتم‌های یک محصول
        
        Args:
            user: کاربر
            product_id: ID محصول
        
        Returns:
            int: تعداد آیتم‌های حذف شده
        """
        pass
```

**مثال استفاده:**
```python
from apps.cart.services.delete_cart_service import DeleteCartService

service = DeleteCartService()

# حذف یک آیتم
service.remove_item(user, item_id=123)

# پاک کردن کامل سبد
service.clear_cart(user)

# حذف تمام آیتم‌های یک محصول
count = service.remove_items_by_product(user, product_id=456)
print(f"{count} آیتم حذف شد")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.delete')
```

---

### update_cart_service.py

#### 📍 موقعیت: `backend/apps/cart/services/update_cart_service.py`

#### هدف:
بروزرسانی آیتم‌های سبد خرید.

#### کلاس اصلی: `UpdateCartService`

**متدهای اصلی:**

```python
class UpdateCartService:
    def update_quantity(self, 
                       user: User, 
                       item_id: int, 
                       quantity: int) -> CartItem:
        """
        بروزرسانی تعداد آیتم
        
        Args:
            user: کاربر
            item_id: ID آیتم
            quantity: تعداد جدید
        
        Returns:
            CartItem: آیتم بروزرسانی شده
        
        Raises:
            CartItemNotFoundError: اگر آیتم وجود نداشته باشد
            InsufficientStockError: اگر موجودی کافی نباشد
        """
        pass
    
    def update_options(self, 
                      user: User, 
                      item_id: int, 
                      selected_options: dict) -> CartItem:
        """
        تغییر ویژگی‌های انتخابی
        
        Args:
            user: کاربر
            item_id: ID آیتم
            selected_options: ویژگی‌های جدید
        
        Returns:
            CartItem: آیتم بروزرسانی شده
        
        Raises:
            CartItemNotFoundError: اگر آیتم وجود نداشته باشد
            CartValidationError: اگر ویژگی‌ها نامعتبر باشند
        """
        pass
    
    def increment_quantity(self, user: User, item_id: int) -> CartItem:
        """
        افزایش تعداد یک آیتم
        
        Args:
            user: کاربر
            item_id: ID آیتم
        
        Returns:
            CartItem: آیتم بروزرسانی شده
        """
        pass
    
    def decrement_quantity(self, user: User, item_id: int) -> CartItem:
        """
        کاهش تعداد یک آیتم
        
        Args:
            user: کاربر
            item_id: ID آیتم
        
        Returns:
            CartItem: آیتم بروزرسانی شده
        
        Raises:
            CartValidationError: اگر تعداد به صفر برسد
        """
        pass
```

**مثال استفاده:**
```python
from apps.cart.services.update_cart_service import UpdateCartService

service = UpdateCartService()

# بروزرسانی تعداد
updated_item = service.update_quantity(
    user=user,
    item_id=123,
    quantity=5
)

# تغییر ویژگی‌های انتخابی
updated_item = service.update_options(
    user=user,
    item_id=123,
    selected_options={
        'size': 'xlarge',
        'color': 'blue'
    }
)

# افزایش تعداد
service.increment_quantity(user, item_id=123)

# کاهش تعداد
service.decrement_quantity(user, item_id=123)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('cart.services.update')
```

---

## utils/

### 📍 موقعیت: `backend/apps/cart/utils/`

### توضیحات:
ابزارهای کمکی برای عملیات سبد خرید.

**ابزارهای اصلی:**
- `cart_calculator.py`: محاسبه قیمت سبد
- `file_validator.py`: اعتبارسنجی فایل‌ها
- `price_utils.py`: ابزارهای محاسبه قیمت

---

## نکات مهم

### 1. **یک سبد خرید فعال**
- ✅ هر کاربر فقط یک سبد خرید فعال دارد
- ✅ با افزودن اولین آیتم، سبد به صورت خودکار ایجاد می‌شود
- ✅ پس از تبدیل به سفارش، سبد جدید ایجاد می‌شود

### 2. **قیمت‌گذاری**
- ✅ قیمت محصول در زمان افزودن به سبد ذخیره می‌شود
- ✅ تغییرات قیمت بعد از افزودن به سبد تأثیر نمی‌گذارد
- ✅ قیمت نهایی با ویژگی‌های انتخابی محاسبه می‌شود

### 3. **اعتبارسنجی**
- ✅ قبل از تبدیل به سفارش، سبد اعتبارسنجی می‌شود
- ✅ بررسی موجودی محصولات
- ✅ بررسی فعال بودن محصولات
- ✅ بررسی ویژگی‌های انتخابی

### 4. **فایل‌های آپلودی**
- ✅ فایل‌ها در پوشه موقت ذخیره می‌شوند
- ✅ پس از تبدیل به سفارش، به پوشه دائمی منتقل می‌شوند
- ✅ حداکثر حجم فایل: 10MB
- ✅ فرمت‌های مجاز: PDF, JPG, PNG, DOC, DOCX

### 5. **تراکنش‌ها**
- ✅ تمام عملیات سبد خرید در تراکنش atomic انجام می‌شوند
- ✅ در صورت خطا، همه چیز rollback می‌شود

### 6. **لاگ‌گذاری**
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

### 7. **بهینه‌سازی**
- ✅ استفاده از select_related برای بهینه‌سازی کوئری‌ها
- ✅ کش کردن سبد خرید با Redis
- ✅ به‌روزرسانی خودکار قیمت‌ها

---

## فرآیند تبدیل سبد به سفارش

```
1. User → POST /api/v1/order/create/
   {address_id: 123}

2. CartValidatorService.validate_cart(user)
   - بررسی موجودی
   - بررسی فعال بودن محصولات
   - بررسی آدرس ارسال

3. OrderCreateService.create_order()
   - شروع تراکنش atomic
   - ایجاد Order
   - ایجاد OrderItemها
   - کم کردن موجودی انبار
   - پاک کردن سبد خرید
   - ارسال اعلان
   - پایان تراکنش

4. Response به کاربر
```

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core
- **[مستندات Order](./order.md)** - مستندات اپلیکیشن Order (تبدیل سبد به سفارش)

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24