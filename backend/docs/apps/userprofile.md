# مستندات اپلیکیشن UserProfile

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌های استفاده شده](#مدل‌های-استفاده-شده)
4. [سرویس‌ها](#سرویس‌ها)
5. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن userprofile مسئول مدیریت پروفایل و اطلاعات شخصی کاربران است. این اپلیکیشن شامل مدیریت آدرس‌ها، تاریخچه سفارشات، کیف پول و تراکنش‌های مالی کاربران می‌باشد.

---

## ساختار فایل‌ها

```
userprofile/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس (در صورت وجود)
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    ├── __init__.py
    ├── user_address_service.py      # مدیریت آدرس
    ├── user_detail_service.py       # جزئیات پروفایل
    ├── user_feedback_service.py     # فیدبک
    ├── user_order_service.py        # سفارشات کاربر
    └── user_transaction_service.py  # تراکنش‌های مالی
```

---

## مدل‌های استفاده شده

### 📍 موقعیت: `backend/core/users/models.py`

### توضیحات:
اپلیکیشن userprofile از مدل‌های تعریف شده در `core.users` استفاده می‌کند:

#### 1. **User**
- مدل اصلی کاربر
- اطلاعات پایه: username، email، phone، first_name، last_name
- وضعیت: is_active، is_staff، is_superuser
- نقش‌ها: customer، staff، admin

#### 2. **UserProfile**
- پروفایل تکمیلی کاربر
- تصویر پروفایل (avatar)
- اطلاعات شخصی: bio، birth_date، national_code

#### 3. **Address**
- آدرس‌های کاربر برای ارسال سفارشات
- عنوان، آدرس کامل، کد پستی، شهر، استان
- شماره تماس
- آدرس پیش‌فرض

#### 4. **Wallet**
- کیف پول الکترونیکی کاربر
- موجودی (balance)

#### 5. **Transaction**
- تراکنش‌های مالی کیف پول
- مبلغ، نوع (deposit، withdraw، purchase، refund)
- توضیحات، تاریخ

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/userprofile/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن userprofile که منطق تجاری مربوط به پروفایل کاربران را پیاده‌سازی می‌کنند.

---

### user_address_service.py

#### 📍 موقعیت: `backend/apps/userprofile/services/user_address_service.py`

#### هدف:
مدیریت آدرس‌های کاربران.

#### کلاس اصلی: `UserAddressService`

**متدهای اصلی:**

```python
class UserAddressService:
    def add_address(self, 
                   user: User, 
                   address_data: dict) -> Address:
        """
        افزودن آدرس جدید
        
        Args:
            user: کاربر
            address_data: {
                'title': str,
                'full_address': str,
                'postal_code': str,
                'city': str,
                'province': str,
                'phone': str,
                'is_default': bool
            }
        
        Returns:
            Address: آدرس ایجاد شده
        
        Raises:
            ValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def update_address(self, 
                      user: User, 
                      address_id: int, 
                      address_data: dict) -> Address:
        """
        بروزرسانی آدرس
        
        Args:
            user: کاربر
            address_id: ID آدرس
            address_data: داده‌های جدید
        
        Returns:
            Address: آدرس بروزرسانی شده
        
        Raises:
            AddressNotFoundError: اگر آدرس وجود نداشته باشد
        """
        pass
    
    def delete_address(self, user: User, address_id: int) -> bool:
        """
        حذف آدرس
        
        Args:
            user: کاربر
            address_id: ID آدرس
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            AddressNotFoundError: اگر آدرس وجود نداشته باشد
        """
        pass
    
    def get_addresses(self, user: User) -> QuerySet:
        """
        دریافت لیست آدرس‌های کاربر
        
        Args:
            user: کاربر
        
        Returns:
            QuerySet: لیست آدرس‌ها
        """
        pass
    
    def set_default_address(self, user: User, address_id: int) -> bool:
        """
        تنظیم آدرس به عنوان پیش‌فرض
        
        Args:
            user: کاربر
            address_id: ID آدرس
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        
        Raises:
            AddressNotFoundError: اگر آدرس وجود نداشته باشد
        """
        pass
    
    def get_default_address(self, user: User) -> Address:
        """
        دریافت آدرس پیش‌فرض
        
        Args:
            user: کاربر
        
        Returns:
            Address: آدرس پیش‌فرض
        
        Raises:
            AddressNotFoundError: اگر آدرس پیش‌فرض وجود نداشته باشد
        """
        pass
```

**مثال استفاده:**
```python
from apps.userprofile.services.user_address_service import UserAddressService

service = UserAddressService()

# افزودن آدرس جدید
address = service.add_address(
    user=user,
    address_data={
        'title': 'خانه',
        'full_address': 'تهران، خیابان ولیعصر، پلاک 123',
        'postal_code': '1234567890',
        'city': 'تهران',
        'province': 'تهران',
        'phone': '09123456789',
        'is_default': True
    }
)

# دریافت لیست آدرس‌ها
addresses = service.get_addresses(user)

# تنظیم آدرس پیش‌فرض
service.set_default_address(user, address_id=123)

# حذف آدرس
service.delete_address(user, address_id=456)
```

**قوانین مهم:**
- ✅ هر کاربر می‌تواند چند آدرس داشته باشد
- ✅ فقط یک آدرس می‌تواند پیش‌فرض باشد
- ✅ هنگام تنظیم آدرس به عنوان پیش‌فرض، سایر آدرس‌ها به حالت غیرپیش‌فرض تغییر می‌کنند

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.address')
```

---

### user_detail_service.py

#### 📍 موقعیت: `backend/apps/userprofile/services/user_detail_service.py`

#### هدف:
مدیریت پروفایل کاربر.

#### کلاس اصلی: `UserDetailService`

**متدهای اصلی:**

```python
class UserDetailService:
    def get_profile(self, user: User) -> UserProfile:
        """
        دریافت پروفایل کاربر
        
        Args:
            user: کاربر
        
        Returns:
            UserProfile: پروفایل کاربر
        """
        pass
    
    def update_profile(self, 
                      user: User, 
                      profile_data: dict) -> UserProfile:
        """
        بروزرسانی پروفایل
        
        Args:
            user: کاربر
            profile_data: {
                'first_name': str,
                'last_name': str,
                'phone': str,
                'bio': str,
                'birth_date': str
            }
        
        Returns:
            UserProfile: پروفایل بروزرسانی شده
        """
        pass
    
    def upload_avatar(self, user: User, image_file) -> str:
        """
        آپلود تصویر پروفایل
        
        Args:
            user: کاربر
            image_file: فایل تصویر
        
        Returns:
            str: URL تصویر آپلود شده
        
        Raises:
            ValidationError: اگر فایل نامعتبر باشد
        """
        pass
    
    def delete_avatar(self, user: User) -> bool:
        """
        حذف تصویر پروفایل
        
        Args:
            user: کاربر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
```

**مثال استفاده:**
```python
from apps.userprofile.services.user_detail_service import UserDetailService

service = UserDetailService()

# دریافت پروفایل
profile = service.get_profile(user)
print(f"نام: {profile.user.get_full_name()}")
print(f"بیو: {profile.bio}")

# بروزرسانی پروفایل
updated_profile = service.update_profile(
    user=user,
    profile_data={
        'first_name': 'علی',
        'last_name': 'محمدی',
        'phone': '09123456789',
        'bio': 'توسعه‌دهنده نرم‌افزار'
    }
)

# آپلود آواتار
avatar_url = service.upload_avatar(user, image_file)
print(f"آواتار جدید: {avatar_url}")

# حذف آواتار
service.delete_avatar(user)
```

**قابلیت‌های آپلود آواتار:**
- ✅ فرمت‌های مجاز: JPG، PNG، GIF
- ✅ حداکثر حجم: 2MB
- ✅ تغییر سایز خودکار (Resize)
- ✅ فشرده‌سازی تصویر
- ✅ ذخیره در پوشه `media/avatars/`

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.profile')
```

---

### user_feedback_service.py

#### 📍 موقعیت: `backend/apps/userprofile/services/user_feedback_service.py`

#### هدف:
مدیریت نظرات و فیدبک‌های کاربران.

#### کلاس اصلی: `UserFeedbackService`

**متدهای اصلی:**

```python
class UserFeedbackService:
    def create_feedback(self, 
                       user: User, 
                       text: str, 
                       rating: int = None) -> Feedback:
        """
        ایجاد فیدبک جدید
        
        Args:
            user: کاربر
            text: متن فیدبک
            rating: امتیاز (1-5) - اختیاری
        
        Returns:
            Feedback: فیدبک ایجاد شده
        
        Raises:
            ValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def get_user_feedbacks(self, 
                          user: User, 
                          page: int = 1, 
                          page_size: int = 20) -> PaginatedResponse:
        """
        دریافت لیست فیدبک‌های کاربر
        
        Args:
            user: کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
        
        Returns:
            PaginatedResponse: لیست فیدبک‌ها
        """
        pass
    
    def get_feedback_by_id(self, user: User, feedback_id: int) -> Feedback:
        """
        دریافت یک فیدبک خاص
        
        Args:
            user: کاربر
            feedback_id: ID فیدبک
        
        Returns:
            Feedback: فیدبک
        
        Raises:
            FeedbackNotFoundError: اگر فیدبک وجود نداشته باشد
        """
        pass
```

**مثال استفاده:**
```python
from apps.userprofile.services.user_feedback_service import UserFeedbackService

service = UserFeedbackService()

# ایجاد فیدبک
feedback = service.create_feedback(
    user=user,
    text='محصول عالی بود، تحویل سریع',
    rating=5
)

# دریافت لیست فیدبک‌ها
feedbacks = service.get_user_feedbacks(user, page=1, page_size=20)

# دریافت یک فیدبک خاص
feedback = service.get_feedback_by_id(user, feedback_id=123)
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.notification')
```

---

### user_order_service.py

#### 📍 موقعیت: `backend/apps/userprofile/services/user_order_service.py`

#### هدف:
مدیریت سفارشات کاربر.

#### کلاس اصلی: `UserOrderService`

**متدهای اصلی:**

```python
class UserOrderService:
    def get_orders(self, 
                  user: User, 
                  page: int = 1, 
                  page_size: int = 20,
                  status: str = None) -> PaginatedResponse:
        """
        دریافت لیست سفارشات کاربر
        
        Args:
            user: کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
            status: فیلتر بر اساس وضعیت (اختیاری)
        
        Returns:
            PaginatedResponse: لیست سفارشات
        """
        pass
    
    def get_order_detail(self, 
                        user: User, 
                        order_id: int) -> Order:
        """
        دریافت جزئیات سفارش
        
        Args:
            user: کاربر
            order_id: ID سفارش
        
        Returns:
            Order: سفارش
        
        Raises:
            OrderNotFoundError: اگر سفارش وجود نداشته باشد
        """
        pass
    
    def get_order_items(self, 
                       user: User, 
                       order_id: int) -> QuerySet:
        """
        دریافت آیتم‌های سفارش
        
        Args:
            user: کاربر
            order_id: ID سفارش
        
        Returns:
            QuerySet: آیتم‌های سفارش
        """
        pass
    
    def can_cancel_order(self, user: User, order_id: int) -> bool:
        """
        بررسی امکان لغو سفارش
        
        Args:
            user: کاربر
            order_id: ID سفارش
        
        Returns:
            bool: آیا سفارش قابل لغو است
        """
        pass
```

**مثال استفاده:**
```python
from apps.userprofile.services.user_order_service import UserOrderService

service = UserOrderService()

# دریافت لیست سفارشات
orders = service.get_orders(
    user=user,
    page=1,
    page_size=20,
    status='pending'  # فیلتر اختیاری
)

# دریافت جزئیات سفارش
order = service.get_order_detail(user, order_id=123)
print(f"کد سفارش: {order.order_code}")
print(f"مبلغ: {order.final_amount} تومان")
print(f"وضعیت: {order.get_status_display()}")

# دریافت آیتم‌های سفارش
items = service.get_order_items(user, order_id=123)
for item in items:
    print(f"{item.product_name} - {item.quantity} عدد")

# بررسی امکان لغو
if service.can_cancel_order(user, order_id=123):
    print("این سفارش قابل لغو است")
```

**فیلترهای وضعیت:**
- `pending`: در انتظار پرداخت
- `paid`: پرداخت شده
- `processing`: در حال پردازش
- `shipped`: ارسال شده
- `delivered`: تحویل داده شده
- `cancelled`: لغو شده
- `refunded`: بازگشت وجه

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.orders')
```

---

### user_transaction_service.py

#### 📍 موقعیت: `backend/apps/userprofile/services/user_transaction_service.py`

#### هدف:
مدیریت تراکنش‌های مالی و کیف پول کاربر.

#### کلاس اصلی: `UserTransactionService`

**متدهای اصلی:**

```python
class UserTransactionService:
    def get_wallet_balance(self, user: User) -> Decimal:
        """
        دریافت موجودی کیف پول
        
        Args:
            user: کاربر
        
        Returns:
            Decimal: موجودی
        """
        pass
    
    def get_transactions(self, 
                        user: User, 
                        page: int = 1, 
                        page_size: int = 20,
                        transaction_type: str = None) -> PaginatedResponse:
        """
        دریافت لیست تراکنش‌ها
        
        Args:
            user: کاربر
            page: شماره صفحه
            page_size: تعداد آیتم
            transaction_type: نوع تراکنش (اختیاری)
        
        Returns:
            PaginatedResponse: لیست تراکنش‌ها
        """
        pass
    
    def add_transaction(self, 
                       user: User, 
                       amount: Decimal, 
                       type: str, 
                       description: str) -> Transaction:
        """
        افزودن تراکنش جدید
        
        Args:
            user: کاربر
            amount: مبلغ
            type: نوع تراکنش (deposit, withdraw, purchase, refund)
            description: توضیحات
        
        Returns:
            Transaction: تراکنش ایجاد شده
        
        Raises:
            ValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def get_transaction_by_id(self, 
                             user: User, 
                             transaction_id: int) -> Transaction:
        """
        دریافت یک تراکنش خاص
        
        Args:
            user: کاربر
            transaction_id: ID تراکنش
        
        Returns:
            Transaction: تراکنش
        
        Raises:
            TransactionNotFoundError: اگر تراکنش وجود نداشته باشد
        """
        pass
```

**مثال استفاده:**
```python
from apps.userprofile.services.user_transaction_service import UserTransactionService
from decimal import Decimal

service = UserTransactionService()

# دریافت موجودی
balance = service.get_wallet_balance(user)
print(f"موجودی: {balance} تومان")

# دریافت لیست تراکنش‌ها
transactions = service.get_transactions(
    user=user,
    page=1,
    page_size=20,
    transaction_type='deposit'  # فیلتر اختیاری
)

# افزودن تراکنش
transaction = service.add_transaction(
    user=user,
    amount=Decimal('100000'),
    type='deposit',
    description='واریز از طریق درگاه پرداخت'
)

# دریافت یک تراکنش خاص
transaction = service.get_transaction_by_id(user, transaction_id=123)
print(f"مبلغ: {transaction.amount}")
print(f"نوع: {transaction.get_type_display()}")
print(f"تاریخ: {transaction.created_at}")
```

**انواع تراکنش:**
- `deposit`: واریز به کیف پول
- `withdraw`: برداشت از کیف پول
- `purchase`: خرید (کاهش موجودی)
- `refund`: بازگشت وجه (افزایش موجودی)

**قوانین مهم:**
- ✅ تراکنش‌های withdraw فقط در صورت موجودی کافی انجام می‌شود
- ✅ تراکنش‌های purchase به صورت خودکار پس از سفارش ایجاد می‌شوند
- ✅ تراکنش‌های refund برای بازگشت وجه استفاده می‌شوند
- ✅ تمام تراکنش‌ها با تاریخ و توضیحات ثبت می‌شوند

**لاگ‌گذاری:**
```python
logger = logging.getLogger('userprofile.services.wallet')
```

---

## نکات مهم

### 1. **امنیت**
- ✅ کاربر فقط می‌تواند به آدرس‌های خودش دسترسی داشته باشد
- ✅ فقط آدرس پیش‌فرض برای ارسال سفارش استفاده می‌شود
- ✅ تراکنش‌های مالی فقط توسط ادمین قابل تغییر هستند

### 2. **پروفایل**
- ✅ تصویر پروفایل اختیاری است
- ✅ در صورت عدم وجود آواتار، تصویر پیش‌فرض نمایش داده می‌شود
- ✅ اطلاعات پروفایل به صورت partial update بروزرسانی می‌شوند

### 3. **آدرس‌ها**
- ✅ هر کاربر می‌تواند چند آدرس داشته باشد
- ✅ فقط یک آدرس می‌تواند پیش‌فرض باشد
- ✅ آدرس پیش‌فرض برای ارسال سفارش استفاده می‌شود
- ✅ در صورت عدم وجود آدرس پیش‌فرض، اولین آدرس استفاده می‌شود

### 4. **کیف پول**
- ✅ موجودی کیف پول به صورت خودکار بروزرسانی می‌شود
- ✅ تراکنش‌های مالی فقط افزایش یا کاهش موجودی می‌کنند
- ✅ تراکنش‌های منفی (برداشت) فقط در صورت موجودی کافی امکان‌پذیر است
- ✅ تمام تراکنش‌ها قابل ردیابی هستند

### 5. **سفارشات**
- ✅ کاربر فقط می‌تواند سفارشات خودش را مشاهده کند
- ✅ سفارشات به صورت پاگینیشن نمایش داده می‌شوند
- ✅ امکان فیلتر بر اساس وضعیت سفارش وجود دارد
- ✅ جزئیات کامل هر سفارش قابل مشاهده است

### 6. **فیدبک**
- ✅ کاربر می‌تواند برای محصولات فیدبک ارسال کند
- ✅ فیدبک‌ها قبل از نمایش عمومی نیاز به تأیید دارند
- ✅ هر کاربر می‌تواند برای یک محصول فقط یک فیدبک ارسال کند

### 7. **لاگ‌گذاری**
```python
logger = logging.getLogger('userprofile.services.address')
logger = logging.getLogger('userprofile.services.profile')
logger = logging.getLogger('userprofile.services.orders')
logger = logging.getLogger('userprofile.services.wallet')
logger = logging.getLogger('userprofile.services.notification')
```

### 8. **بهینه‌سازی**
- ✅ استفاده از select_related برای بهینه‌سازی کوئری‌ها
- ✅ کش کردن پروفایل کاربر با Redis
- ✅ به‌روزرسانی lazy اطلاعات پروفایل

---

## API Endpoints

### نمای کلی:

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

---

## فرآیند‌های مهم

### 1. بروزرسانی پروفایل:

```
1. User → PUT /api/v1/userprofile/profile/
   {
     'first_name': 'علی',
     'last_name': 'محمدی',
     'phone': '09123456789',
     'bio': 'توسعه‌دهنده'
   }

2. UserDetailService.update_profile()
   - اعتبارسنجی داده‌ها
   - بروزرسانی اطلاعات کاربر
   - بروزرسانی اطلاعات پروفایل

3. Response
   {
     'success': true,
     'profile': {...}
   }
```

### 2. افزودن آدرس:

```
1. User → POST /api/v1/userprofile/address/
   {
     'title': 'خانه',
     'full_address': 'تهران، خیابان ولیعصر',
     'postal_code': '1234567890',
     'city': 'تهران',
     'province': 'تهران',
     'phone': '09123456789',
     'is_default': true
   }

2. UserAddressService.add_address()
   - اعتبارسنجی داده‌ها
   - اگر is_default=True، سایر آدرس‌ها را غیرپیش‌فرض کن
   - ایجاد آدرس جدید

3. Response
   {
     'success': true,
     'address': {...}
   }
```

### 3. مشاهده تاریخچه سفارشات:

```
1. User → GET /api/v1/userprofile/orders/?page=1&page_size=20

2. UserOrderService.get_orders()
   - دریافت سفارشات کاربر
   - اعمال فیلترها
   - پاگینیشن

3. Response
   {
     'count': 50,
     'next': '...',
     'previous': '...',
     'results': [...]
   }
```

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core (مدل‌های کاربری)
- **[مستندات Order](./order.md)** - مستندات اپلیکیشن Order
- **[مستندات API](../api/README.md)** - مستندات لایه API

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24