# مستندات اپلیکیشن Dashboard

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)
- مطالعه [مستندات API](../api/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [سرویس‌ها](#سرویس‌ها)
4. [وظایف Celery](#وظایف-celery)
5. [API Endpoints](#api-endpoints)
6. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن dashboard مسئول تمام عملیات مدیریتی و پنل ادمین است. این اپلیکیشن امکانات کامل مدیریتی برای مدیریت محصولات، سفارشات، کاربران، گزارشات و استخراج/ایمپورت داده‌ها را فراهم می‌کند. این اپلیکیشن فقط برای کاربران با نقش staff یا admin قابل دسترسی است.

---

## ساختار فایل‌ها

```
dashboard/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس (در صورت وجود)
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

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/dashboard/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن dashboard که منطق تجاری مربوط به عملیات مدیریتی را پیاده‌سازی می‌کنند.

---

### dashboard_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/dashboard_service.py`

#### هدف:
سرویس اصلی داشبورد برای دریافت آمار و اطلاعات کلی.

#### کلاس اصلی: `DashboardService`

**متدهای اصلی:**

```python
class DashboardService:
    def get_dashboard_stats(self) -> dict:
        """
        دریافت آمار کلی داشبورد
        
        Returns:
            dict: {
                'total_users': int,
                'total_orders': int,
                'total_products': int,
                'total_revenue': Decimal,
                'recent_orders': list,
                'top_products': list
            }
        """
        pass
    
    def get_sales_stats(self, 
                       start_date: datetime, 
                       end_date: datetime) -> dict:
        """
        دریافت آمار فروش
        
        Args:
            start_date: تاریخ شروع
            end_date: تاریخ پایان
        
        Returns:
            dict: آمار فروش
        """
        pass
    
    def get_customer_stats(self) -> dict:
        """
        دریافت آمار مشتریان
        
        Returns:
            dict: آمار مشتریان
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.dashboard_service import DashboardService

service = DashboardService()

# دریافت آمار کلی
stats = service.get_dashboard_stats()
print(f"تعداد کاربران: {stats['total_users']}")
print(f"تعداد سفارشات: {stats['total_orders']}")
print(f"درآمد کل: {stats['total_revenue']} تومان")

# دریافت آمار فروش در بازه زمانی
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

sales_stats = service.get_sales_stats(start_date, end_date)
print(f"فروش 30 روز گذشته: {sales_stats['total_sales']} تومان")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.services.product_dashboard')
```

---

### product_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/product_service.py`

#### هدف:
مدیریت محصولات از طریق پنل مدیریت.

#### کلاس اصلی: `ProductService`

**متدهای اصلی:**

```python
class ProductService:
    def create_product(self, product_data: dict, media_files: list = None) -> Product:
        """
        ایجاد محصول جدید
        
        Args:
            product_data: {
                'name': str,
                'description': str,
                'base_price': Decimal,
                'category_id': int,
                'stock': int,
                'is_active': bool,
                'is_featured': bool
            }
            media_files: فایل‌های مدیا (اختیاری)
        
        Returns:
            Product: محصول ایجاد شده
        """
        pass
    
    def update_product(self, 
                      product_id: int, 
                      product_data: dict) -> Product:
        """
        بروزرسانی محصول
        
        Args:
            product_id: ID محصول
            product_data: داده‌های جدید
        
        Returns:
            Product: محصول بروزرسانی شده
        """
        pass
    
    def delete_product(self, product_id: int) -> bool:
        """
        حذف محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def toggle_product_status(self, product_id: int) -> Product:
        """
        تغییر وضعیت فعال/غیرفعال محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            Product: محصول
        """
        pass
    
    def toggle_featured(self, product_id: int) -> Product:
        """
        تغییر وضعیت ویژه محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            Product: محصول
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.product_service import ProductService
from decimal import Decimal

service = ProductService()

# ایجاد محصول جدید
product = service.create_product(
    product_data={
        'name': 'تیشرت مردانه',
        'description': 'تیشرت باکیفیت از پنبه',
        'base_price': Decimal('250000'),
        'category_id': 5,
        'stock': 100,
        'is_active': True,
        'is_featured': True
    },
    media_files=[request.FILES['image']]
)

# بروزرسانی محصول
updated_product = service.update_product(
    product_id=123,
    product_data={
        'base_price': Decimal('280000'),
        'stock': 150
    }
)

# تغییر وضعیت
service.toggle_product_status(product_id=123)

# حذف محصول
service.delete_product(product_id=456)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.services.product_dashboard')
```

---

### product_export_import_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/product_export_import_service.py`

#### هدف:
استخراج و ایمپورت محصولات از/به Excel.

#### کلاس اصلی: `ProductExportImportService`

**متدهای اصلی:**

```python
class ProductExportImportService:
    def export_products(self, 
                       product_ids: list = None,
                       include_fields: bool = True,
                       include_formulas: bool = True) -> dict:
        """
        استخراج محصولات به Excel
        
        Args:
            product_ids: لیست ID محصولات (اگر None باشد، همه محصولات)
            include_fields: شامل کردن فیلدهای داینامیک
            include_formulas: شامل کردن فرمول‌های قیمت‌گذاری
        
        Returns:
            dict: {
                'success': bool,
                'file_path': str,
                'file_name': str,
                'product_count': int
            }
        """
        pass
    
    def import_products(self, 
                       file, 
                       update_existing: bool = False,
                       skip_errors: bool = True) -> dict:
        """
        ایمپورت محصولات از Excel
        
        Args:
            file: فایل Excel
            update_existing: بروزرسانی محصولات تکراری
            skip_errors: ادامه در صورت خطا
        
        Returns:
            dict: {
                'success': bool,
                'imported_count': int,
                'failed_count': int,
                'errors': list
            }
        """
        pass
    
    def generate_template(self) -> dict:
        """
        تولید فایل نمونه برای ایمپورت
        
        Returns:
            dict: {
                'success': bool,
                'file_path': str,
                'file_name': str
            }
        """
        pass
    
    def get_export_history(self) -> list:
        """
        دریافت تاریخچه فایل‌های استخراج شده
        
        Returns:
            list: لیست فایل‌ها
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.product_export_import_service import ProductExportImportService

service = ProductExportImportService()

# استخراج همه محصولات
export_result = service.export_products(
    product_ids=None,
    include_fields=True,
    include_formulas=True
)

print(f"فایل استخراج شد: {export_result['file_name']}")
print(f"تعداد محصولات: {export_result['product_count']}")

# استخراج محصولات انتخابی
export_result = service.export_products(
    product_ids=[1, 5, 12],
    include_fields=True,
    include_formulas=False
)

# ایمپورت محصولات
with open('products.xlsx', 'rb') as file:
    import_result = service.import_products(
        file=file,
        update_existing=True,
        skip_errors=True
    )
    
    print(f"ایمپورت موفق: {import_result['imported_count']}")
    print(f"ایمپورت ناموفق: {import_result['failed_count']}")
    
    if import_result['errors']:
        for error in import_result['errors']:
            print(f"خطا: {error}")

# تولید فایل نمونه
template = service.generate_template()
print(f"فایل نمونه: {template['file_name']}")

# دریافت تاریخچه
history = service.get_export_history()
for file in history:
    print(f"{file['file_name']} - {file['created_at']}")
```

**ساختار فایل Excel:**
```
Sheet 1: اطلاعات اصلی محصولات
  - نام، توضیحات، قیمت، موجودی، دسته‌بندی

Sheet 2: فیلدهای داینامیک
  - ویژگی‌های محصول (سایز، جنس، رنگ)

Sheet 3: فرمول‌های قیمت‌گذاری
  - فرمول‌های محاسبه قیمت

Sheet 4: عکس‌ها
  - URL عکس‌های محصول

Sheet 5: فایل‌های پیوست
  - URL فایل‌های پیوست
```

**ویژگی‌ها:**
- ✅ استخراج کامل با تمام اطلاعات
- ✅ ایمپورت با اعتبارسنجی
- ✅ تراکنش atomic (همه یا هیچ)
- ✅ پردازش ناهمزمان با Celery
- ✅ فایل نمونه برای راهنمایی

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.tasks')
```

---

### order_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/order_service.py`

#### هدف:
مدیریت سفارشات از پنل مدیریت.

#### کلاس اصلی: `OrderService`

**متدهای اصلی:**

```python
class OrderService:
    def get_orders(self, 
                  page: int = 1, 
                  page_size: int = 20,
                  status: str = None,
                  start_date: datetime = None,
                  end_date: datetime = None) -> PaginatedResponse:
        """
        دریافت لیست سفارشات
        
        Args:
            page: شماره صفحه
            page_size: تعداد آیتم
            status: فیلتر بر اساس وضعیت
            start_date: تاریخ شروع
            end_date: تاریخ پایان
        
        Returns:
            PaginatedResponse: لیست سفارشات
        """
        pass
    
    def get_order_detail(self, order_id: int) -> Order:
        """
        دریافت جزئیات سفارش
        
        Args:
            order_id: ID سفارش
        
        Returns:
            Order: سفارش
        """
        pass
    
    def update_order_status(self, 
                          order_id: int, 
                          status: str,
                          description: str = '') -> Order:
        """
        تغییر وضعیت سفارش
        
        Args:
            order_id: ID سفارش
            status: وضعیت جدید
            description: توضیحات
        
        Returns:
            Order: سفارش بروزرسانی شده
        """
        pass
    
    def cancel_order(self, order_id: int, reason: str = '') -> Order:
        """
        لغو سفارش
        
        Args:
            order_id: ID سفارش
            reason: دلیل لغو
        
        Returns:
            Order: سفارش لغو شده
        """
        pass
    
    def get_orders_report(self, 
                         start_date: datetime, 
                         end_date: datetime) -> dict:
        """
        دریافت گزارش سفارشات
        
        Args:
            start_date: تاریخ شروع
            end_date: تاریخ پایان
        
        Returns:
            dict: گزارش سفارشات
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.order_service import OrderService
from datetime import datetime, timedelta

service = OrderService()

# دریافت لیست سفارشات
orders = service.get_orders(
    page=1,
    page_size=20,
    status='pending'
)

# دریافت جزئیات سفارش
order = service.get_order_detail(order_id=123)
print(f"کد سفارش: {order.order_code}")
print(f"مبلغ: {order.final_amount} تومان")

# تغییر وضعیت سفارش
updated_order = service.update_order_status(
    order_id=123,
    status='shipped',
    description='سفارش با کد رهگیری XYZ123 ارسال شد.'
)

# لغو سفارش
cancelled_order = service.cancel_order(
    order_id=456,
    reason='درخواست مشتری'
)

# دریافت گزارش
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

report = service.get_orders_report(start_date, end_date)
print(f"تعداد سفارشات: {report['total_orders']}")
print(f"درآمد کل: {report['total_revenue']} تومان")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.services.cart_dashboard')
```

---

### customer_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/customer_service.py`

#### هدف:
مدیریت کاربران و مشتریان.

#### کلاس اصلی: `CustomerService`

**متدهای اصلی:**

```python
class CustomerService:
    def get_customers(self, 
                     page: int = 1, 
                     page_size: int = 20,
                     search: str = None) -> PaginatedResponse:
        """
        دریافت لیست کاربران
        
        Args:
            page: شماره صفحه
            page_size: تعداد آیتم
            search: جستجو در نام یا ایمیل
        
        Returns:
            PaginatedResponse: لیست کاربران
        """
        pass
    
    def get_customer_detail(self, user_id: int) -> User:
        """
        دریافت جزئیات کاربر
        
        Args:
            user_id: ID کاربر
        
        Returns:
            User: کاربر
        """
        pass
    
    def toggle_user_status(self, user_id: int) -> User:
        """
        تغییر وضعیت فعال/غیرفعال کاربر
        
        Args:
            user_id: ID کاربر
        
        Returns:
            User: کاربر
        """
        pass
    
    def get_customer_orders(self, 
                           user_id: int, 
                           page: int = 1, 
                           page_size: int = 20) -> PaginatedResponse:
        """
        دریافت سفارشات کاربر
        
        Args:
            user_id: ID کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
        
        Returns:
            PaginatedResponse: لیست سفارشات
        """
        pass
    
    def get_customer_stats(self, user_id: int) -> dict:
        """
        دریافت آمار کاربر
        
        Args:
            user_id: ID کاربر
        
        Returns:
            dict: آمار کاربر
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.customer_service import CustomerService

service = CustomerService()

# دریافت لیست کاربران
customers = service.get_customers(
    page=1,
    page_size=20,
    search='علی'
)

# دریافت جزئیات کاربر
user = service.get_customer_detail(user_id=123)
print(f"نام: {user.get_full_name()}")
print(f"ایمیل: {user.email}")

# تغییر وضعیت کاربر
service.toggle_user_status(user_id=123)

# دریافت سفارشات کاربر
orders = service.get_customer_orders(user_id=123, page=1, page_size=20)

# دریافت آمار کاربر
stats = service.get_customer_stats(user_id=123)
print(f"تعداد سفارشات: {stats['total_orders']}")
print(f"مجموع خرید: {stats['total_purchases']} تومان")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.services.customer')
```

---

### wallet_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/wallet_service.py`

#### هدف:
مدیریت کیف پول کاربران از پنل مدیریت.

#### کلاس اصلی: `WalletService`

**متدهای اصلی:**

```python
class WalletService:
    def get_user_wallet(self, user_id: int) -> Wallet:
        """
        دریافت کیف پول کاربر
        
        Args:
            user_id: ID کاربر
        
        Returns:
            Wallet: کیف پول
        """
        pass
    
    def get_wallet_transactions(self, 
                               user_id: int, 
                               page: int = 1, 
                               page_size: int = 20) -> PaginatedResponse:
        """
        دریافت تراکنش‌های کیف پول
        
        Args:
            user_id: ID کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
        
        Returns:
            PaginatedResponse: لیست تراکنش‌ها
        """
        pass
    
    def add_manual_transaction(self, 
                             user_id: int, 
                             amount: Decimal, 
                             type: str, 
                             description: str) -> Transaction:
        """
        افزودن تراکنش دستی
        
        Args:
            user_id: ID کاربر
            amount: مبلغ
            type: نوع تراکنش
            description: توضیحات
        
        Returns:
            Transaction: تراکنش ایجاد شده
        """
        pass
    
    def get_wallet_report(self, 
                         start_date: datetime, 
                         end_date: datetime) -> dict:
        """
        دریافت گزارش مالی
        
        Args:
            start_date: تاریخ شروع
            end_date: تاریخ پایان
        
        Returns:
            dict: گزارش مالی
        """
        pass
```

**مثال استفاده:**
```python
from apps.dashboard.services.wallet_service import WalletService
from decimal import Decimal

service = WalletService()

# دریافت کیف پول کاربر
wallet = service.get_user_wallet(user_id=123)
print(f"موجودی: {wallet.balance} تومان")

# دریافت تراکنش‌ها
transactions = service.get_wallet_transactions(
    user_id=123,
    page=1,
    page_size=20
)

# افزودن تراکنش دستی (مثلاً واریز دستی)
transaction = service.add_manual_transaction(
    user_id=123,
    amount=Decimal('500000'),
    type='deposit',
    description='واریز دستی توسط ادمین'
)

# دریافت گزارش مالی
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

report = service.get_wallet_report(start_date, end_date)
print(f"مجموع واریزها: {report['total_deposits']} تومان")
print(f"مجموع برداشت‌ها: {report['total_withdraws']} تومان")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('dashboard.services.wallet')
```

---

### content_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/content_service.py`

#### هدف:
مدیریت محتوای سایت (بنرها، اسلایدر، وبلاگ).

#### کلاس اصلی: `ContentService`

**متدهای اصلی:**

```python
class ContentService:
    def create_banner(self, banner_data: dict, image_file) -> Banner:
        """
        ایجاد بنر جدید
        
        Args:
            banner_data: {
                'title': str,
                'link': str,
                'order': int,
                'is_active': bool
            }
            image_file: فایل تصویر
        
        Returns:
            Banner: بنر ایجاد شده
        """
        pass
    
    def create_blog_post(self, post_data: dict) -> BlogPost:
        """
        ایجاد پست وبلاگ
        
        Args:
            post_data: {
                'title': str,
                'content': str,
                'is_published': bool
            }
        
        Returns:
            BlogPost: پست ایجاد شده
        """
        pass
```

---

### location_service.py

#### 📍 موقعیت: `backend/apps/dashboard/services/location_service.py`

#### هدف:
مدیریت موقعیت‌های جغرافیایی (استان، شهر).

#### کلاس اصلی: `LocationService`

**متدهای اصلی:**

```python
class LocationService:
    def get_provinces(self) -> QuerySet:
        """
        دریافت لیست استان‌ها
        
        Returns:
            QuerySet: استان‌ها
        """
        pass
    
    def get_cities(self, province_id: int) -> QuerySet:
        """
        دریافت لیست شهرهای یک استان
        
        Args:
            province_id: ID استان
        
        Returns:
            QuerySet: شهرها
        """
        pass
```

---

## وظایف Celery

### 📍 موقعیت: `backend/apps/dashboard/tasks.py`

### توضیحات:
وظایف ناهمزمان برای عملیات زمان‌بر داشبورد.

**وظایف اصلی:**

```python
from celery import shared_task
from apps.dashboard.services.product_export_import_service import ProductExportImportService

@shared_task
def export_products_task(product_ids: list, 
                        include_fields: bool = True,
                        include_formulas: bool = True) -> dict:
    """
    وظیفه ناهمزمان استخراج محصولات
    
    Args:
        product_ids: لیست ID محصولات
        include_fields: شامل کردن فیلدهای داینامیک
        include_formulas: شامل کردن فرمول‌ها
    
    Returns:
        dict: نتیجه استخراج
    """
    pass

@shared_task
def import_products_task(file_path: str, 
                        update_existing: bool = False) -> dict:
    """
    وظیفه ناهمزمان ایمپورت محصولات
    
    Args:
        file_path: مسیر فایل Excel
        update_existing: بروزرسانی محصولات تکراری
    
    Returns:
        dict: نتیجه ایمپورت
    """
    pass

@shared_task
def generate_sales_report(start_date: str, end_date: str) -> dict:
    """
    وظیفه تولید گزارش فروش
    
    Args:
        start_date: تاریخ شروع
        end_date: تاریخ پایان
    
    Returns:
        dict: گزارش
    """
    pass

@shared_task
def cleanup_old_exports(days: int = 7) -> int:
    """
    پاکسازی فایل‌های استخراج قدیمی
    
    Args:
        days: تعداد روزهای قدیمی
    
    Returns:
        int: تعداد فایل‌های حذف شده
    """
    pass
```

**مثال استفاده:**
```python
# استخراج ناهمزمان محصولات
from apps.dashboard.tasks import export_products_task

task = export_products_task.delay(
    product_ids=[1, 2, 3],
    include_fields=True,
    include_formulas=True
)

# بررسی وضعیت وظیفه
result = task.get()
print(f"فایل: {result['file_name']}")

# ایمپورت ناهمزمان
from apps.dashboard.tasks import import_products_task

task = import_products_task.delay(
    file_path='/tmp/products.xlsx',
    update_existing=True
)

# تولید گزارش
from apps.dashboard.tasks import generate_sales_report
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

task = generate_sales_report.delay(
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat()
)
```

---

## API Endpoints

### 📍 موقعیت: `backend/api/v1/dashboard/`

### نمای کلی:

```
# مدیریت محصولات
GET    /api/v1/dashboard/products/
POST   /api/v1/dashboard/products/
PUT    /api/v1/dashboard/products/{id}/
DELETE /api/v1/dashboard/products/{id}/
POST   /api/v1/dashboard/products/{id}/toggle-status/
POST   /api/v1/dashboard/products/{id}/toggle-featured/

# مدیریت سفارشات
GET    /api/v1/dashboard/orders/
GET    /api/v1/dashboard/orders/{id}/
PUT    /api/v1/dashboard/orders/{id}/status/
POST   /api/v1/dashboard/orders/{id}/cancel/

# مدیریت کاربران
GET    /api/v1/dashboard/users/
GET    /api/v1/dashboard/users/{id}/
PUT    /api/v1/dashboard/users/{id}/toggle-status/
GET    /api/v1/dashboard/users/{id}/orders/
GET    /api/v1/dashboard/users/{id}/stats/

# مدیریت کیف پول
GET    /api/v1/dashboard/wallet/{user_id}/
GET    /api/v1/dashboard/wallet/{user_id}/transactions/
POST   /api/v1/dashboard/wallet/{user_id}/add-transaction/
GET    /api/v1/dashboard/wallet/report/

# گزارشات
GET    /api/v1/dashboard/reports/sales/
GET    /api/v1/dashboard/reports/customers/
GET    /api/v1/dashboard/reports/products/

# استخراج و ایمپورت
POST   /api/v1/dashboard/products-export-import/export/
POST   /api/v1/dashboard/products-export-import/import/
GET    /api/v1/dashboard/products-export-import/template/
GET    /api/v1/dashboard/products-export-import/history/

# محتوا
POST   /api/v1/dashboard/banners/
PUT    /api/v1/dashboard/banners/{id}/
DELETE /api/v1/dashboard/banners/{id}/
POST   /api/v1/dashboard/blog/
PUT    /api/v1/dashboard/blog/{id}/
DELETE /api/v1/dashboard/blog/{id}/
```

---

## نکات مهم

### 1. **دسترسی**
- ✅ فقط کاربران با نقش `staff` یا `admin` می‌توانند به این API دسترسی داشته باشند
- ✅ تمام endpointها نیاز به احراز هویت دارند
- ✅ تمام عملیات لاگ می‌شود

### 2. **مدیریت محصولات**
- ✅ امکان استخراج و ایمپورت هزاران محصول
- ✅ پردازش ناهمزمان با Celery
- ✅ اعتبارسنجی کامل در ایمپورت
- ✅ تراکنش atomic

### 3. **مدیریت سفارشات**
- ✅ تغییر وضعیت سفارش
- ✅ لغو سفارش با دلیل
- ✅ گزارش‌گیری پیشرفته
- ✅ فیلتر بر اساس تاریخ و وضعیت

### 4. **مدیریت کاربران**
- ✅ جستجو در نام و ایمیل
- ✅ مشاهده تاریخچه سفارشات
- ✅ مشاهده آمار کاربر
- ✅ تغییر وضعیت فعال/غیرفعال

### 5. **کیف پول**
- ✅ مشاهده موجودی
- ✅ مشاهده تراکنش‌ها
- ✅ افزودن تراکنش دستی
- ✅ گزارش مالی

### 6. **لاگ‌گذاری**
```python
logger = logging.getLogger('dashboard.services.product_dashboard')
logger = logging.getLogger('dashboard.services.cart_dashboard')
logger = logging.getLogger('dashboard.services.customer')
logger = logging.getLogger('dashboard.services.wallet')
logger = logging.getLogger('dashboard.tasks')
```

### 7. **بهینه‌سازی**
- ✅ استفاده از select_related و prefetch_related
- ✅ پاگینیشن برای لیست‌های بزرگ
- ✅ فیلتر کردن در دیتابیس
- ✅ کش کردن آمار

### 8. **امنیت**
- ✅ بررسی نقش کاربر در هر درخواست
- ✅ لاگ تمام عملیات مدیریتی
- ✅ محدودیت نرخ درخواست
- ✅ اعتبارسنجی کامل ورودی‌ها

---

## فرآیند استخراج و ایمپورت

### نمودار جریان استخراج:

```
1. Admin → POST /api/v1/dashboard/products-export-import/export/
   {
     'product_ids': [1, 5, 12],
     'include_fields': true,
     'include_formulas': true
   }

2. ProductExportImportService.export_products()
   - دریافت محصولات
   - جمع‌آوری اطلاعات
   - ایجاد فایل Excel

3. اگر محصولات زیاد باشد:
   - ارسال وظیفه به Celery
   - پردازش ناهمزمان
   - اعلان پس از اتمام

4. Response
   {
     'success': true,
     'file_path': 'exports/products/products_export_20240124.xlsx',
     'file_name': 'products_export_20240124.xlsx',
     'product_count': 100
   }

5. Admin → GET /api/v1/dashboard/products-export-import/download/{file_name}
   - دانلود فایل Excel
```

### نمودار جریان ایمپورت:

```
1. Admin → POST /api/v1/dashboard/products-export-import/import/
   Form Data:
   - file: products.xlsx
   - update_existing: true
   - skip_errors: true

2. ProductExportImportService.import_products()
   - خواندن فایل Excel
   - اعتبارسنجی داده‌ها
   - شروع تراکنش atomic

3. برای هر محصول:
   - بررسی وجود محصول
   - اگر وجود دارد و update_existing=True:
     - بروزرسانی محصول
   - در غیر این صورت:
     - ایجاد محصول جدید
   - ایجاد فیلدهای داینامیک
   - ایجاد فرمول‌های قیمت

4. اگر خطا رخ دهد:
   - rollback تراکنش
   - ثبت خطاها

5. Response
   {
     'success': true,
     'imported_count': 50,
     'failed_count': 2,
     'errors': [
       'سطر 5: نام محصول نمی‌تواند خالی باشد.',
       'سطر 12: خطا در ذخیره محصول: ...'
     ]
   }
```

---

## گزارشات

### 1. **گزارش فروش**
```python
# درخواست
GET /api/v1/dashboard/reports/sales/?start_date=2024-01-01&end_date=2024-01-31

# Response
{
  'total_orders': 150,
  'total_revenue': 50000000,
  'average_order_value': 333333,
  'top_products': [...],
  'sales_by_date': {...}
}
```

### 2. **گزارش مشتریان**
```python
# درخواست
GET /api/v1/dashboard/reports/customers/?start_date=2024-01-01&end_date=2024-01-31

# Response
{
  'total_customers': 200,
  'new_customers': 50,
  'top_customers': [...],
  'customer_growth': {...}
}
```

### 3. **گزارش محصولات**
```python
# درخواست
GET /api/v1/dashboard/reports/products/

# Response
{
  'total_products': 500,
  'active_products': 450,
  'out_of_stock': 10,
  'top_selling': [...],
  'low_stock': [...]
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