# مستندات اپلیکیشن Notification

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌ها](#مدل‌ها)
4. [سرویس‌ها](#سرویس‌ها)
5. [وظایف Celery](#وظایف-celery)
6. [سیگنال‌ها](#سیگنال‌ها)
7. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن notification مسئول سیستم اعلان‌ها و پیام‌های کاربران است. این اپلیکیشن امکان ارسال اعلان‌های مختلف به کاربران را فراهم می‌کند و کاربران می‌توانند اعلان‌های خود را مشاهده و مدیریت کنند.

---

## ساختار فایل‌ها

```
notification/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس
├── managers.py              # منیجرهای سفارشی
├── signals.py               # سیگنال‌های Django
├── tasks.py                 # وظایف Celery
├── domain_services.py       # سرویس‌های دامنه
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    └── __init__.py
        └── customer_notification_service.py  # سرویس اعلان
```

---

## مدل‌ها

### 📍 موقعیت: `backend/apps/notification/models.py`

### توضیحات:
مدل‌های مربوط به سیستم اعلان‌ها.

#### 1. **Notification**
**توضیحات:**
مدل اصلی اعلان.

**فیلدهای اصلی:**
```python
class Notification(models.Model):
    # کاربر دریافت‌کننده
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    # محتوای اعلان
    title = models.CharField(
        max_length=200,
        help_text='عنوان اعلان'
    )
    message = models.TextField(
        help_text='متن اعلان'
    )
    
    # نوع اعلان
    TYPE_CHOICES = [
        ('info', 'اطلاعیه'),
        ('success', 'موفقیت'),
        ('warning', 'هشدار'),
        ('error', 'خطا'),
    ]
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='info'
    )
    
    # وضعیت خواندن
    is_read = models.BooleanField(
        default=False,
        help_text='آیا اعلان خوانده شده است'
    )
    read_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='زمان خواندن'
    )
    
    # داده‌های اضافی (برای لینک، دکمه، و ...)
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text='داده‌های اضافی (مثل لینک، action_type)'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # وضعیت فعال بودن
    is_active = models.BooleanField(default=True)
```

**فیلدهای data (JSONField):**
```python
{
    'link': '/orders/123',           # لینک برای کلیک
    'action_type': 'view_order',     # نوع عمل
    'icon': 'shopping-cart',         # آیکون
    'priority': 'high'               # اولویت
}
```

**ویژگی‌ها:**
- هر اعلان به یک کاربر تعلق دارد
- اعلان‌ها می‌توانند انواع مختلف داشته باشند
- اعلان‌ها می‌توانند لینک یا action داشته باشند

---

## managers.py

### 📍 موقعیت: `backend/apps/notification/managers.py`

### توضیحات:
منیجرهای سفارشی برای مدل Notification.

**منیجرهای اصلی:**

```python
class NotificationManager(BaseManager):
    def get_user_notifications(self, 
                              user: User, 
                              unread_only: bool = False) -> QuerySet:
        """
        دریافت اعلان‌های کاربر
        
        Args:
            user: کاربر
            unread_only: فقط اعلان‌های خوانده نشده
        
        Returns:
            QuerySet: اعلان‌های کاربر
        """
        pass
    
    def get_unread_count(self, user: User) -> int:
        """
        تعداد اعلان‌های خوانده نشده
        
        Args:
            user: کاربر
        
        Returns:
            int: تعداد اعلان‌های خوانده نشده
        """
        pass
    
    def mark_all_as_read(self, user: User) -> bool:
        """
        علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده
        
        Args:
            user: کاربر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
```

---

## signals.py

### 📍 موقعیت: `backend/apps/notification/signals.py`

### توضیحات:
سیگنال‌های Django برای ارسال خودکار اعلان در رویدادهای مختلف.

**سیگنال‌های اصلی:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.order.models import Order
from apps.cart.models import Cart

@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    """ارسال اعلان پس از ایجاد سفارش"""
    if created:
        # ارسال اعلان به کاربر
        notification_service.send_notification(
            user=instance.user,
            title='سفارش شما ثبت شد',
            message=f'سفارش با کد {instance.order_code} با موفقیت ثبت شد.',
            type='success',
            data={'link': f'/orders/{instance.id}'}
        )

@receiver(post_save, sender=Cart)
def send_cart_notification(sender, instance, created, **kwargs):
    """ارسال اعلان پس از تبدیل سبد به سفارش"""
    if instance.status == 'converted':
        notification_service.send_notification(
            user=instance.user,
            title='سبد خرید تبدیل شد',
            message='سبد خرید شما با موفقیت به سفارش تبدیل شد.',
            type='success'
        )
```

---

## domain_services.py

### 📍 موقعیت: `backend/apps/notification/domain_services.py`

### توضیحات:
سرویس‌های دامنه برای عملیات مربوط به اعلان‌ها.

**سرویس‌های اصلی:**

```python
class NotificationDomainService:
    def create_notification_data(self, 
                                notification_type: str, 
                                context: dict) -> dict:
        """
        ایجاد داده‌های اعلان بر اساس نوع
        
        Args:
            notification_type: نوع اعلان
            context: context داده‌ها
        
        Returns:
            dict: داده‌های اعلان
        """
        pass
    
    def get_notification_template(self, type: str) -> dict:
        """
        دریافت قالب اعلان
        
        Args:
            type: نوع اعلان
        
        Returns:
            dict: قالب اعلان
        """
        pass
```

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/notification/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن notification.

---

### customer_notification_service.py

#### 📍 موقعیت: `backend/apps/notification/services/customer_notification_service.py`

#### هدف:
مدیریت اعلان‌های کاربران.

#### کلاس اصلی: `CustomerNotificationService`

**متدهای اصلی:**

```python
class CustomerNotificationService:
    def send_notification(self, 
                         user: User, 
                         title: str, 
                         message: str, 
                         type: str = 'info',
                         data: dict = None) -> Notification:
        """
        ارسال اعلان به کاربر
        
        Args:
            user: کاربر دریافت‌کننده
            title: عنوان اعلان
            message: متن اعلان
            type: نوع اعلان (info, success, warning, error)
            data: داده‌های اضافی (اختیاری)
        
        Returns:
            Notification: اعلان ایجاد شده
        """
        pass
    
    def get_notifications(self, 
                         user: User, 
                         page: int = 1, 
                         page_size: int = 20,
                         unread_only: bool = False) -> PaginatedResponse:
        """
        دریافت لیست اعلان‌های کاربر
        
        Args:
            user: کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
            unread_only: فقط اعلان‌های خوانده نشده
        
        Returns:
            PaginatedResponse: لیست اعلان‌ها
        """
        pass
    
    def mark_as_read(self, user: User, notification_id: int) -> bool:
        """
        علامت‌گذاری اعلان به عنوان خوانده شده
        
        Args:
            user: کاربر
            notification_id: ID اعلان
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            NotificationNotFoundError: اگر اعلان وجود نداشته باشد
        """
        pass
    
    def mark_all_as_read(self, user: User) -> bool:
        """
        علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده
        
        Args:
            user: کاربر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def delete_notification(self, user: User, notification_id: int) -> bool:
        """
        حذف اعلان
        
        Args:
            user: کاربر
            notification_id: ID اعلان
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            NotificationNotFoundError: اگر اعلان وجود نداشته باشد
        """
        pass
    
    def delete_all_notifications(self, user: User) -> bool:
        """
        حذف همه اعلان‌های کاربر
        
        Args:
            user: کاربر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def get_unread_count(self, user: User) -> int:
        """
        تعداد اعلان‌های خوانده نشده
        
        Args:
            user: کاربر
        
        Returns:
            int: تعداد اعلان‌های خوانده نشده
        """
        pass
```

**مثال استفاده:**
```python
from apps.notification.services.customer_notification_service import CustomerNotificationService

service = CustomerNotificationService()

# ارسال اعلان ساده
notification = service.send_notification(
    user=user,
    title='خوش آمدید',
    message='به Printoo24 خوش آمدید!',
    type='success'
)

# ارسال اعلان با لینک
notification = service.send_notification(
    user=user,
    title='سفارش شما ثبت شد',
    message='سفارش با کد ORD-2024-001234 ثبت شد.',
    type='success',
    data={
        'link': '/orders/123',
        'action_type': 'view_order'
    }
)

# دریافت لیست اعلان‌ها
notifications = service.get_notifications(
    user=user,
    page=1,
    page_size=20,
    unread_only=True  # فقط خوانده نشده‌ها
)

# علامت‌گذاری به عنوان خوانده شده
service.mark_as_read(user, notification_id=123)

# علامت‌گذاری همه به عنوان خوانده شده
service.mark_all_as_read(user)

# حذف اعلان
service.delete_notification(user, notification_id=456)

# تعداد اعلان‌های خوانده نشده
unread_count = service.get_unread_count(user)
print(f"اعلان‌های خوانده نشده: {unread_count}")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.notification')
```

---

## وظایف Celery

### 📍 موقعیت: `backend/apps/notification/tasks.py`

### توضیحات:
وظایف ناهمزمان برای ارسال اعلان‌های گروهی و زمان‌بندی شده.

**وظایف اصلی:**

```python
from celery import shared_task
from apps.notification.services.customer_notification_service import CustomerNotificationService

@shared_task
def send_bulk_notification(user_ids: list, 
                          title: str, 
                          message: str, 
                          type: str = 'info') -> int:
    """
    ارسال اعلان گروهی به چند کاربر
    
    Args:
        user_ids: لیست ID کاربران
        title: عنوان اعلان
        message: متن اعلان
        type: نوع اعلان
    
    Returns:
        int: تعداد اعلان‌های ارسال شده
    """
    pass

@shared_task
def send_scheduled_notification(user_id: int, 
                               title: str, 
                               message: str, 
                               send_at: datetime) -> bool:
    """
    ارسال اعلان زمان‌بندی شده
    
    Args:
        user_id: ID کاربر
        title: عنوان اعلان
        message: متن اعلان
        send_at: زمان ارسال
    
    Returns:
        bool: موفقیت‌آمیز بودن عملیات
    """
    pass

@shared_task
def cleanup_old_notifications(days: int = 30) -> int:
    """
    پاکسازی اعلان‌های قدیمی
    
    Args:
        days: تعداد روزهای قدیمی
    
    Returns:
        int: تعداد اعلان‌های حذف شده
    """
    pass
```

**مثال استفاده:**
```python
# ارسال اعلان گروهی
from apps.notification.tasks import send_bulk_notification

send_bulk_notification.delay(
    user_ids=[1, 2, 3, 4, 5],
    title='تخفیف ویژه',
    message='تخفیف 20% برای تمام محصولات',
    type='info'
)

# ارسال اعلان زمان‌بندی شده
from apps.notification.tasks import send_scheduled_notification
from datetime import datetime, timedelta

send_at = datetime.now() + timedelta(hours=2)
send_scheduled_notification.delay(
    user_id=123,
    title='یادآوری',
    message='سبد خرید شما در انتظار تکمیل است',
    send_at=send_at
)

# پاکسازی اعلان‌های قدیمی
from apps.notification.tasks import cleanup_old_notifications

cleanup_old_notifications.delay(days=30)
```

---

## انواع اعلان‌ها

### 1. **اطلاعیه (info)**
```python
{
    'type': 'info',
    'title': 'اطلاعیه',
    'message': 'سیستم در تاریخ X تعمیر می‌شود.'
}
```

### 2. **موفقیت (success)**
```python
{
    'type': 'success',
    'title': 'سفارش ثبت شد',
    'message': 'سفارش شما با موفقیت ثبت شد.',
    'data': {'link': '/orders/123'}
}
```

### 3. **هشدار (warning)**
```python
{
    'type': 'warning',
    'title': 'موجودی کم',
    'message': 'موجودی محصول X به اتمام رسیده است.'
}
```

### 4. **خطا (error)**
```python
{
    'type': 'error',
    'title': 'خطا در پرداخت',
    'message': 'پرداخت شما با خطا مواجه شد. لطفاً دوباره تلاش کنید.'
}
```

---

## API Endpoints

### 📍 موقعیت: `backend/api/v1/notification/`

### نمای کلی:

```
GET    /api/v1/notification/notifications/           # لیست اعلان‌ها
GET    /api/v1/notification/notifications/unread/    # اعلان‌های خوانده نشده
POST   /api/v1/notification/notifications/read/      # علامت خوانده شده
POST   /api/v1/notification/notifications/read-all/  # علامت همه خوانده شده
DELETE /api/v1/notification/notifications/{id}/      # حذف اعلان
DELETE /api/v1/notification/notifications/clear/     # حذف همه اعلان‌ها
GET    /api/v1/notification/unread-count/            # تعداد خوانده نشده‌ها
```

---

## نکات مهم

### 1. **انواع اعلان**
- ✅ `info`: اطلاعات عمومی
- ✅ `success`: عملیات موفق
- ✅ `warning`: هشدارها
- ✅ `error`: خطاها

### 2. **وضعیت خواندن**
- ✅ اعلان‌های جدید به صورت پیش‌فرض خوانده نشده هستند
- ✅ کاربر می‌تواند اعلان را به صورت تکی یا گروهی علامت‌گذاری کند
- ✅ زمان خواندن به صورت خودکار ثبت می‌شود

### 3. **داده‌های اضافی**
- ✅ هر اعلان می‌تواند داده‌های اضافی داشته باشد
- ✅ معمولاً شامل لینک و نوع عمل است
- ✅ به صورت JSONField ذخیره می‌شود

### 4. **ارسال خودکار**
- ✅ اعلان‌های خودکار از طریق سیگنال‌ها ارسال می‌شوند
- ✅ رویدادهای مختلف اعلان تولید می‌کنند:
  - ثبت سفارش
  - تغییر وضعیت سفارش
  - تأیید پرداخت
  - ارسال محصول
  - ...

### 5. **اعلان‌های گروهی**
- ✅ از Celery برای ارسال اعلان‌های گروهی استفاده می‌شود
- ✅ ارسال به صورت ناهمزمان انجام می‌شود
- ✅ مناسب برای کمپین‌های تبلیغاتی

### 6. **اعلان‌های زمان‌بندی شده**
- ✅ امکان ارسال اعلان در زمان مشخص
- ✅ از Celery Beat برای زمان‌بندی استفاده می‌شود
- ✅ مناسب برای یادآوری‌ها

### 7. **پاکسازی**
- ✅ اعلان‌های قدیمی به صورت خودکار حذف می‌شوند
- ✅ وظیفه Celery برای پاکسازی
- ✅ پیش‌فرض: حذف اعلان‌های older than 30 days

### 8. **لاگ‌گذاری**
```python
logger = logging.getLogger('userprofile.services.notification')
```

### 9. **بهینه‌سازی**
- ✅ استفاده از select_related برای بهینه‌سازی کوئری‌ها
- ✅ کش کردن تعداد اعلان‌های خوانده نشده
- ✅ Pagination برای لیست اعلان‌ها

---

## فرآیند ارسال اعلان

### نمودار جریان:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. رویداد (مثل ایجاد سفارش)                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. سیگنال Django (post_save)                                │
│    @receiver(post_save, sender=Order)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. فراخوانی NotificationService.send_notification()         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. ایجاد رکورد Notification                                  │
│    - کاربر                                                   │
│    - عنوان                                                   │
│    - متن                                                     │
│    - نوع                                                     │
│    - داده‌های اضافی                                         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. ارسال از طریق کانال‌های مختلف                             │
│    - In-App (ذخیره در دیتابیس)                              │
│    - Email (Celery Task)                                     │
│    - SMS (در صورت نیاز)                                      │
│    - Push Notification (در صورت نیاز)                       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. کاربر اعلان را مشاهده می‌کند                              │
│    GET /api/v1/notification/notifications/                   │
└─────────────────────────────────────────────────────────────┘
```

---

## انواع اعلان‌های خودکار

### 1. **اعلان سفارش**
```python
# پس از ایجاد سفارش
{
    'title': 'سفارش شما ثبت شد',
    'message': 'سفارش با کد ORD-2024-001234 ثبت شد.',
    'type': 'success',
    'data': {'link': '/orders/123'}
}

# پس از تغییر وضعیت به "ارسال شده"
{
    'title': 'سفارش ارسال شد',
    'message': 'سفارش شما ارسال شد. کد رهگیری: XYZ123',
    'type': 'info',
    'data': {'link': '/orders/123'}
}

# پس از تحویل
{
    'title': 'سفارش تحویل داده شد',
    'message': 'سفارش شما تحویل داده شد. از خرید شما متشکریم!',
    'type': 'success'
}
```

### 2. **اعلان پرداخت**
```python
# پرداخت موفق
{
    'title': 'پرداخت موفق',
    'message': 'پرداخت شما با موفقیت انجام شد.',
    'type': 'success'
}

# پرداخت ناموفق
{
    'title': 'پرداخت ناموفق',
    'message': 'پرداخت شما با خطا مواجه شد. لطفاً دوباره تلاش کنید.',
    'type': 'error'
}
```

### 3. **اعلان موجودی**
```python
# موجودی کم
{
    'title': 'موجودی کم',
    'message': 'محصول X در حال حاضر موجود نیست.',
    'type': 'warning'
}

# بازگشت به موجودی
{
    'title': 'بازگشت به موجودی',
    'message': 'محصول X دوباره موجود شد!',
    'type': 'success',
    'data': {'link': '/products/123'}
}
```

### 4. **اعلان سیستم**
```python
# تعمیرات
{
    'title': 'تعمیرات سیستم',
    'message': 'سیستم در تاریخ X تعمیر می‌شود.',
    'type': 'warning'
}

# به‌روزرسانی
{
    'title': 'به‌روزرسانی',
    'message': 'نسخه جدید سایت راه‌اندازی شد.',
    'type': 'info'
}
```

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core
- **[مستندات Order](./order.md)** - مستندات اپلیکیشن Order
- **[مستندات API](../api/README.md)** - مستندات لایه API

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24