# مستندات اپلیکیشن Order

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)
- مطالعه [مستندات اپلیکیشن Cart](./cart.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌ها](#مدل‌ها)
4. [سرویس‌ها](#سرویس‌ها)
5. [فرآیند ایجاد سفارش](#فرآیند-ایجاد-سفارش)
6. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن order مسئول مدیریت کامل فرآیند سفارش‌گیری است. این اپلیکیشن نقطه اوج سیستم فروش است که سبد خرید کاربر را به سفارش تبدیل می‌کند، وضعیت سفارش را مدیریت می‌کند و تاریخچه سفارشات را نگهداری می‌کند.

---

## ساختار فایل‌ها

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

---

## مدل‌ها

### 📍 موقعیت: `backend/apps/order/models.py` و `backend/core/order/models.py`

### توضیحات:
مدل‌های مربوط به سفارشات.

#### 1. **Order**
**توضیحات:**
مدل اصلی سفارش.

**فیلدهای اصلی:**
```python
class Order(models.Model):
    # کاربر
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # کد سفارش (یکتا)
    order_code = models.CharField(
        max_length=50, 
        unique=True,
        help_text='کد یکتا برای سفارش'
    )
    
    # وضعیت
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت وجه'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # قیمت‌ها
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        help_text='مبلغ کل سفارش'
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        default=0
    )
    final_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        help_text='مبلغ نهایی بعد از تخفیف'
    )
    
    # آدرس ارسال
    address = models.ForeignKey(
        Address, 
        on_delete=models.SET_NULL,
        null=True
    )
    
    # یادداشت‌ها
    customer_note = models.TextField(
        blank=True,
        help_text='یادداشت کاربر'
    )
    admin_note = models.TextField(
        blank=True,
        help_text='یادداشت ادمین'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # پرداخت
    payment_method = models.CharField(
        max_length=50,
        blank=True
    )
    payment_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text='شماره مرجع پرداخت'
    )
    
    # وضعیت فعال بودن
    is_active = models.BooleanField(default=True)
```

**ویژگی‌ها:**
- کد سفارش به صورت خودکار تولید می‌شود
- تاریخ‌های مختلف برای ردیابی وضعیت
- پشتیبانی از تخفیف و مالیات

#### 2. **OrderItem**
**توضیحات:**
آیتم‌های هر سفارش.

**فیلدهای اصلی:**
```python
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    
    # قیمت‌ها (در زمان ایجاد سفارش)
    unit_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        help_text='قیمت واحد در زمان سفارش'
    )
    total_price = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        help_text='قیمت کل این آیتم'
    )
    
    # ویژگی‌های انتخابی
    selected_options = models.JSONField(
        default=dict,
        help_text='ویژگی‌های انتخابی محصول'
    )
    
    # فایل‌های آپلودی
    uploaded_files = models.JSONField(
        default=list,
        help_text='فایل‌های آپلود شده'
    )
    
    # نام محصول در زمان سفارش (برای تاریخچه)
    product_name = models.CharField(
        max_length=200,
        help_text='نام محصول در زمان سفارش'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
```

**ویژگی‌ها:**
- قیمت در زمان سفارش ذخیره می‌شود (تاریخچه)
- نام محصول در زمان سفارش ذخیره می‌شود
- ویژگی‌های انتخابی و فایل‌ها ذخیره می‌شوند

#### 3. **OrderStatus**
**توضیحات:**
تاریخچه تغییرات وضعیت سفارش.

**فیلدهای اصلی:**
```python
class OrderStatus(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='statuses'
    )
    status = models.CharField(
        max_length=20, 
        choices=Order.STATUS_CHOICES
    )
    description = models.TextField(
        blank=True,
        help_text='توضیحات تغییر وضعیت'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='کاربری که وضعیت را تغییر داد'
    )
    created_at = models.DateTimeField(auto_now_add=True)
```

**ویژگی‌ها:**
- تمام تغییرات وضعیت لاگ می‌شود
- هر تغییر با کاربر و تاریخ ثبت می‌شود

---

## exceptions.py

### 📍 موقعیت: `backend/apps/order/exceptions.py`

### توضیحات:
Exceptionهای سفارشی برای اپلیکیشن order.

**Exceptionهای اصلی:**
```python
class OrderError(Exception):
    """خطای عمومی سفارش"""
    pass

class OrderNotFoundError(OrderError):
    """سفارش پیدا نشد"""
    pass

class InvalidOrderStatusError(OrderError):
    """وضعیت سفارش نامعتبر"""
    pass

class OrderCreationError(OrderError):
    """خطا در ایجاد سفارش"""
    pass

class InsufficientStockError(OrderError):
    """موجودی کافی نیست"""
    pass

class CartEmptyError(OrderError):
    """سبد خرید خالی است"""
    pass
```

---

## domain_services.py

### 📍 موقعیت: `backend/apps/order/domain_services.py`

### توضیحات:
سرویس‌های دامنه برای عملیات مربوط به سفارشات.

**سرویس‌های اصلی:**

```python
class OrderDomainService:
    def generate_order_code(self) -> str:
        """
        تولید کد یکتا برای سفارش
        
        Returns:
            str: کد سفارش (مثلاً: ORD-2024-001234)
        """
        pass
    
    def calculate_order_total(self, cart_items: QuerySet) -> dict:
        """
        محاسبه مجموع سفارش
        
        Args:
            cart_items: آیتم‌های سبد خرید
        
        Returns:
            dict: {
                'subtotal': Decimal,
                'tax': Decimal,
                'discount': Decimal,
                'total': Decimal
            }
        """
        pass
    
    def can_cancel_order(self, order: Order) -> bool:
        """
        بررسی امکان لغو سفارش
        
        Args:
            order: سفارش
        
        Returns:
            bool: آیا سفارش قابل لغو است
        """
        pass
```

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/order/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن order.

---

### order_create_service.py

#### 📍 موقعیت: `backend/apps/order/services/order_create_service.py`

#### هدف:
ایجاد سفارش از سبد خرید کاربر.

#### کلاس اصلی: `OrderCreateService`

**متدهای اصلی:**

```python
class OrderCreateService:
    def create_order(self, 
                    user: User, 
                    address_id: int,
                    customer_note: str = '') -> Order:
        """
        ایجاد سفارش از سبد خرید
        
        Args:
            user: کاربر
            address_id: ID آدرس ارسال
            customer_note: یادداشت کاربر
        
        Returns:
            Order: سفارش ایجاد شده
        
        Raises:
            CartEmptyError: اگر سبد خرید خالی باشد
            InsufficientStockError: اگر موجودی کافی نباشد
            OrderCreationError: اگر خطا در ایجاد سفارش باشد
        """
        pass
    
    def calculate_total(self, cart_items: QuerySet) -> Decimal:
        """
        محاسبه مبلغ کل سفارش
        
        Args:
            cart_items: آیتم‌های سبد
        
        Returns:
            Decimal: مبلغ کل
        """
        pass
    
    def reduce_stock(self, order_items: list) -> bool:
        """
        کم کردن موجودی انبار
        
        Args:
            order_items: لیست آیتم‌های سفارش
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def cancel_order(self, user: User, order_id: int) -> Order:
        """
        لغو سفارش
        
        Args:
            user: کاربر
            order_id: ID سفارش
        
        Returns:
            Order: سفارش لغو شده
        
        Raises:
            OrderNotFoundError: اگر سفارش وجود نداشته باشد
            InvalidOrderStatusError: اگر سفارش قابل لغو نباشد
        """
        pass
```

**فرآیند کامل ایجاد سفارش:**
```
1. دریافت سبد خرید کاربر
2. اعتبارسنجی سبد (CartValidatorService)
   - بررسی خالی نبودن
   - بررسی موجودی
   - بررسی فعال بودن محصولات
3. دریافت آدرس ارسال
4. محاسبه مبلغ کل
5. شروع تراکنش atomic
6. تولید کد سفارش
7. ایجاد رکورد Order
8. برای هر آیتم سبد:
   - ایجاد OrderItem
   - کم کردن موجودی ProductOption
9. تغییر وضعیت سبد به 'converted'
10. پاک کردن سبد خرید
11. ارسال اعلان به کاربر (Notification Service)
12. ثبت لاگ
13. پایان تراکنش
14. برگرداندن سفارش
```

**مثال استفاده:**
```python
from apps.order.services.order_create_service import OrderCreateService

service = OrderCreateService()

# ایجاد سفارش
order = service.create_order(
    user=user,
    address_id=123,
    customer_note='لطفاً قبل از تحویل تماس بگیرید'
)

print(f"سفارش با کد {order.order_code} ایجاد شد")
print(f"مبلغ کل: {order.final_amount} تومان")

# لغو سفارش
cancelled_order = service.cancel_order(user, order_id=456)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('shop.services.order_creation')
```

---

## فرآیند ایجاد سفارش (جزئیات)

### نمودار جریان:

```
┌─────────────────────────────────────────────────────────────┐
│ شروع: کاربر روی دکمه "تکمیل سفارش" کلیک می‌کند              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. اعتبارسنجی داده‌های ورودی                                │
│    - بررسی آدرس ارسال                                       │
│    - بررسی وجود سبد خرید                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. اعتبارسنجی سبد خرید (CartValidatorService)               │
│    - بررسی خالی نبودن سبد                                   │
│    - بررسی موجودی محصولات                                   │
│    - بررسی فعال بودن محصولات                                 │
│    - بررسی ویژگی‌های انتخابی                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. محاسبه مبلغ سفارش                                        │
│    - جمع قیمت تمام آیتم‌ها                                   │
│    - محاسبه مالیات                                           │
│    - اعمال تخفیف                                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. شروع تراکنش atomic                                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. تولید کد سفارش (OrderDomainService)                      │
│    فرمت: ORD-{year}-{sequential_number}                     │
│    مثال: ORD-2024-001234                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. ایجاد رکورد Order                                        │
│    - کاربر                                                   │
│    - آدرس ارسال                                              │
│    - مبلغ‌ها                                                 │
│    - کد سفارش                                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. ایجاد OrderItemها                                        │
│    برای هر آیتم سبد:                                         │
│    - کپی اطلاعات محصول                                       │
│    - ذخیره قیمت در زمان سفارش                                │
│    - ذخیره ویژگی‌های انتخابی                                 │
│    - ذخیره فایل‌های آپلودی                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. کم کردن موجودی انبار                                      │
│    - برای هر ProductOption:                                  │
│      - کم کردن stock                                        │
│      - ثبت لاگ                                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. تغییر وضعیت سبد خرید به 'converted'                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. پاک کردن سبد خرید                                       │
│     - حذف تمام CartItemها                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. ارسال اعلان به کاربر                                    │
│     (Notification Service)                                   │
│     - عنوان: "سفارش شما با موفقیت ثبت شد"                   │
│     - متن: شامل کد سفارش و مبلغ                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 12. ثبت لاگ                                                 │
│     logger.info(f"Order created: {order.order_code}")       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 13. پایان تراکنش atomic                                      │
│     - Commit تمام تغییرات                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 14. برگرداندن Response                                       │
│     {                                                         │
│       'success': true,                                       │
│       'order_code': 'ORD-2024-001234',                       │
│       'total_amount': 1500000,                               │
│       'message': 'سفارش با موفقیت ثبت شد'                   │
│     }                                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## نکات مهم

### 1. **تراکنش Atomic**
- ✅ تمام عملیات ایجاد سفارش در یک تراکنش atomic انجام می‌شود
- ✅ در صورت خطا در هر مرحله، همه چیز rollback می‌شود
- ✅ هیچ داده ناقصی در دیتابیس ذخیره نمی‌شود

### 2. **کد سفارش**
- ✅ کد سفارش به صورت خودکار تولید می‌شود
- ✅ فرمت: `ORD-{year}-{sequential_number}`
- ✅ مثال: `ORD-2024-001234`
- ✅ کد سفارش یکتا است

### 3. **قیمت‌گذاری**
- ✅ قیمت محصول در زمان سفارش ذخیره می‌شود
- ✅ تغییرات قیمت بعد از سفارش تأثیر نمی‌گذارد
- ✅ تاریخچه قیمت برای گزارشات نگهداری می‌شود

### 4. **موجودی**
- ✅ موجودی انبار به صورت خودکار کم می‌شود
- ✅ در صورت عدم کافی بودن موجودی، خطا داده می‌شود
- ✅ موجودی منفی مجاز نیست

### 5. **وضعیت سفارش**
- ✅ وضعیت‌های مختلف: pending، paid، processing، shipped، delivered، cancelled، refunded
- ✅ هر تغییر وضعیت لاگ می‌شود
- ✅ فقط سفارشات pending و processing قابل لغو هستند

### 6. **تاریخچه**
- ✅ تمام تغییرات وضعیت در OrderStatus ذخیره می‌شود
- ✅ هر تغییر با کاربر و تاریخ ثبت می‌شود
- ✅ امکان ردیابی کامل سفارش وجود دارد

### 7. **لاگ‌گذاری**
```python
logger = logging.getLogger('shop.services.order_creation')
```

### 8. **اعلان**
- ✅ پس از ایجاد سفارش، اعلان به کاربر ارسال می‌شود
- ✅ اعلان شامل کد سفارش و مبلغ است
- ✅ اعلان از طریق Notification Service ارسال می‌شود

---

## فرآیند لغو سفارش

```
1. User → POST /api/v1/order/cancel/{order_id}/

2. OrderCreateService.cancel_order(user, order_id)
   - بررسی وجود سفارش
   - بررسی مالکیت سفارش
   - بررسی قابل لغو بودن وضعیت
   - تغییر وضعیت به 'cancelled'
   - برگرداندن موجودی انبار
   - ارسال اعلان به کاربر

3. Response
   {
     'success': true,
     'message': 'سفارش با موفقیت لغو شد'
   }
```

**قوانین لغو سفارش:**
- ✅ فقط سفارشات با وضعیت `pending` و `processing` قابل لغو هستند
- ✅ سفارشات `shipped` و `delivered` قابل لغو نیستند
- ❌ سفارشات `cancelled` و `refunded` قبلاً لغو شده‌اند

---

## گزارشات سفارشات

### گزارشات قابل تولید:

#### 1. **گزارش فروش**
```python
# تعداد سفارشات در بازه زمانی
orders = Order.objects.filter(
    created_at__range=[start_date, end_date]
)
total_sales = orders.aggregate(total=Sum('final_amount'))
```

#### 2. **گزارش مشتریان**
```python
# مشتریان برتر
top_customers = Order.objects.filter(
    created_at__range=[start_date, end_date]
).values('user__username').annotate(
    total_orders=Count('id'),
    total_amount=Sum('final_amount')
).order_by('-total_amount')[:10]
```

#### 3. **گزارش محصولات**
```python
# محصولات پرفروش
top_products = OrderItem.objects.filter(
    order__created_at__range=[start_date, end_date]
).values('product__name').annotate(
    total_quantity=Sum('quantity'),
    total_amount=Sum('total_price')
).order_by('-total_quantity')[:10]
```

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core (مدل‌های سفارش)
- **[مستندات Cart](./cart.md)** - مستندات اپلیکیشن Cart (سبد خرید)
- **[مستندات API](../api/README.md)** - مستندات لایه API

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24