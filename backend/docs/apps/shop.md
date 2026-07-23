# مستندات اپلیکیشن Shop

## 📋 پیش‌نیاز
- مطالعه [مستندات اپلیکیشن‌ها](./apps/README.md)
- مطالعه [مستندات Core](../core/README.md)

## 📋 فهرست مطالب
1. [مقدمه](#مقدمه)
2. [ساختار فایل‌ها](#ساختار-فایل‌ها)
3. [مدل‌های استفاده شده](#مدل‌های-استفاده-شده)
4. [سرویس‌ها](#سرویس‌ها)
5. [فیلترها](#فیلترها)
6. [وظایف Celery](#وظایف-celery)
7. [نکات مهم](#نکات-مهم)

---

## مقدمه

اپلیکیشن shop مسئول مدیریت کامل محصولات، دسته‌بندی‌ها و عملیات مربوط به فروشگاه است. این اپلیکیشن با استفاده از مدل‌های Core کار می‌کند و سرویس‌های اختصاصی برای عملیات پیچیده قیمت‌گذاری و فیلتر کردن ارائه می‌دهد.

---

## ساختار فایل‌ها

```
shop/
├── __init__.py
├── admin.py                 # تنظیمات مدل‌ها در پنل مدیریت
├── apps.py                  # تنظیمات اپلیکیشن
├── models.py                # مدل‌های دیتابیس (در صورت وجود)
├── filters.py               # فیلترهای سفارشی
├── tasks.py                 # وظایف Celery
├── migrations/              # مهاجرت‌های دیتابیس
└── services/                # لایه سرویس‌ها
    ├── __init__.py
    ├── product_list_service.py      # لیست محصولات
    ├── product_detail_service.py    # جزئیات محصول
    ├── product_category_service.py  # دسته‌بندی‌ها
    └── product_comment_service.py   # کامنت‌ها
```

---

## مدل‌های استفاده شده

### 📍 موقعیت: `backend/core/product/models.py`

### توضیحات:
اپلیکیشن shop از مدل‌های تعریف شده در `core.product` استفاده می‌کند:

#### 1. **Product**
- نام، توضیحات، قیمت پایه
- موجودی، وضعیت فعال/غیرفعال
- دسته‌بندی
- تصاویر و فایل‌های پیوست

#### 2. **Category**
- دسته‌بندی‌های سلسله‌مراتبی
- نام، slug، تصویر
- والد و فرزند

#### 3. **ProductMedia**
- تصاویر و ویدیوهای محصول
- فایل‌های پیوست
- نوع فایل (تصویر، ویدیو، سند)

#### 4. **ProductField**
- فیلدهای داینامیک محصول
- نوع فیلد (select، multiselect، text، number، file)
- گزینه‌های هر فیلد

#### 5. **ProductOption**
- گزینه‌های قابل انتخاب برای هر فیلد
- قیمت اضافی
- موجودی

#### 6. **PriceFormula**
- فرمول‌های قیمت‌گذاری
- محاسبه قیمت بر اساس انتخاب‌ها

#### 7. **ProductComment**
- نظرات و امتیازات کاربران
- وضعیت تأیید

---

## سرویس‌ها

### 📍 موقعیت: `backend/apps/sop/services/`

### توضیحات:
لایه سرویس‌های اپلیکیشن shop که منطق تجاری مربوط به محصولات و فروشگاه را پیاده‌سازی می‌کنند.

---

### product_list_service.py

#### 📍 موقعیت: `backend/apps/shop/services/product_list_service.py`

#### هدف:
مدیریت لیست محصولات با قابلیت‌های فیلتر، جستجو و پاگینیشن.

#### کلاس اصلی: `ProductListService`

**متدهای اصلی:**

```python
class ProductListService:
    def get_products(self, 
                    filters: dict, 
                    page: int = 1, 
                    page_size: int = 20) -> PaginatedResponse:
        """
        دریافت لیست محصولات با فیلتر
        
        Args:
            filters: {
                'category_id': int,
                'min_price': Decimal,
                'max_price': Decimal,
                'search': str,
                'is_featured': bool,
                'ordering': str
            }
            page: شماره صفحه
            page_size: تعداد آیتم در هر صفحه
        
        Returns:
            PaginatedResponse: {
                'count': int,
                'next': str,
                'previous': str,
                'results': list
            }
        """
        pass
    
    def search_products(self, query: str) -> QuerySet:
        """
        جستجو در محصولات
        
        Args:
            query: عبارت جستجو
        
        Returns:
            QuerySet: محصولات پیدا شده
        """
        pass
    
    def get_featured_products(self, limit: int = 10) -> QuerySet:
        """
        دریافت محصولات ویژه
        
        Args:
            limit: تعداد محصولات
        
        Returns:
            QuerySet: محصولات ویژه
        """
        pass
```

**مثال استفاده:**
```python
from apps.shop.services.product_list_service import ProductListService

service = ProductListService()

# دریافت لیست محصولات با فیلتر
result = service.get_products(
    filters={
        'category_id': 5,
        'min_price': 100000,
        'max_price': 500000,
        'search': 'تیشرت'
    },
    page=1,
    page_size=20
)

print(f"تعداد کل محصولات: {result.count}")
for product in result.results:
    print(f"{product.name} - {product.base_price} تومان")

# جستجو
products = service.search_products('کفش')
```

**فیلترهای پشتیبانی شده:**
- `category_id`: فیلتر بر اساس دسته‌بندی
- `min_price`, `max_price`: محدوده قیمت
- `search`: جستجو در نام و توضیحات
- `is_featured`: فقط محصولات ویژه
- `ordering`: مرتب‌سازی (`-created_at`, `price`, `-price`)

**لاگ‌گذاری:**
```python
logger = logging.getLogger('shop.services.product_list')
```

---

### product_detail_service.py

#### 📍 موقعیت: `backend/apps/shop/services/product_detail_service.py`

#### هدف:
مدیریت جزئیات محصول و محاسبه قیمت نهایی.

#### کلاس اصلی: `ProductDetailService`

**متدهای اصلی:**

```python
class ProductDetailService:
    def get_product(self, product_id: int) -> Product:
        """
        دریافت جزئیات کامل محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            Product: محصول
        
        Raises:
            ProductNotFound: اگر محصول وجود نداشته باشد
        """
        pass
    
    def calculate_price(self, 
                       product: Product, 
                       selected_options: dict) -> Decimal:
        """
        محاسبه قیمت نهایی بر اساس انتخاب‌های کاربر
        
        Args:
            product: محصول
            selected_options: {
                'field_id': 'option_id',
                ...
            }
        
        Returns:
            Decimal: قیمت نهایی
        """
        pass
    
    def get_price_breakdown(self, 
                           product: Product, 
                           selected_options: dict) -> dict:
        """
        دریافت جزئیات قیمت
        
        Args:
            product: محصول
            selected_options: انتخاب‌های کاربر
        
        Returns:
            dict: {
                'base_price': Decimal,
                'options_price': Decimal,
                'total_price': Decimal,
                'breakdown': list
            }
        """
        pass
    
    def get_related_products(self, product: Product, limit: int = 5) -> QuerySet:
        """
        دریافت محصولات مرتبط
        
        Args:
            product: محصول
            limit: تعداد محصولات
        
        Returns:
            QuerySet: محصولات مرتبط
        """
        pass
```

**مثال استفاده:**
```python
from apps.shop.services.product_detail_service import ProductDetailService
from decimal import Decimal

service = ProductDetailService()

# دریافت جزئیات محصول
product = service.get_product(product_id=123)

# محاسبه قیمت با انتخاب‌های کاربر
selected_options = {
    'size': 'large',
    'color': 'red',
    'material': 'cotton'
}
final_price = service.calculate_price(product, selected_options)

# دریافت جزئیات قیمت
breakdown = service.get_price_breakdown(product, selected_options)
print(f"قیمت پایه: {breakdown['base_price']}")
print(f"قیمت گزینه‌ها: {breakdown['options_price']}")
print(f"قیمت نهایی: {breakdown['total_price']}")

# محصولات مرتبط
related = service.get_related_products(product, limit=5)
```

**فرآیند محاسبه قیمت:**
```
1. دریافت قیمت پایه محصول
2. دریافت انتخاب‌های کاربر
3. برای هر انتخاب:
   - پیدا کردن ProductOption مربوطه
   - اضافه کردن price_modifier به قیمت
4. اعمال PriceFormula (در صورت وجود)
5. برگرداندن قیمت نهایی
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('shop.services.product_detail')
logger = logging.getLogger('shop.services.price_calculator')
```

---

### product_category_service.py

#### 📍 موقعیت: `backend/apps/shop/services/product_category_service.py`

#### هدف:
مدیریت دسته‌بندی‌های محصولات.

#### کلاس اصلی: `ProductCategoryService`

**متدهای اصلی:**

```python
class ProductCategoryService:
    def get_categories(self) -> QuerySet:
        """
        دریافت لیست تمام دسته‌بندی‌های فعال
        
        Returns:
            QuerySet: دسته‌بندی‌ها
        """
        pass
    
    def get_category_tree(self) -> dict:
        """
        دریافت ساختار درختی دسته‌بندی‌ها
        
        Returns:
            dict: ساختار درختی
            {
                'id': 1,
                'name': 'لباس',
                'children': [
                    {
                        'id': 2,
                        'name': 'تیشرت',
                        'children': []
                    }
                ]
            }
        """
        pass
    
    def get_category_products(self, 
                             category_id: int, 
                             page: int = 1, 
                             page_size: int = 20) -> PaginatedResponse:
        """
        دریافت محصولات یک دسته‌بندی
        
        Args:
            category_id: ID دسته‌بندی
            page: شماره صفحه
            page_size: تعداد آیتم
        
        Returns:
            PaginatedResponse: لیست محصولات
        """
        pass
    
    def create_category(self, category_data: dict) -> Category:
        """
        ایجاد دسته‌بندی جدید
        
        Args:
            category_data: {
                'name': str,
                'parent_id': int,
                'description': str
            }
        
        Returns:
            Category: دسته‌بندی ایجاد شده
        """
        pass
```

**مثال استفاده:**
```python
from apps.shop.services.product_category_service import ProductCategoryService

service = ProductCategoryService()

# دریافت لیست دسته‌بندی‌ها
categories = service.get_categories()

# دریافت ساختار درختی
tree = service.get_category_tree()

# دریافت محصولات یک دسته‌بندی
products = service.get_category_products(category_id=5, page=1, page_size=20)

# ایجاد دسته‌بندی جدید
new_category = service.create_category({
    'name': 'کفش',
    'parent_id': 1,
    'description': 'انواع کفش ورزشی و رسمی'
})
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('shop.services.category')
```

---

### product_comment_service.py

#### 📍 موقعیت: `backend/apps/shop/services/product_comment_service.py`

#### هدف:
مدیریت نظرات و امتیازات محصولات.

#### کلاس اصلی: `ProductCommentService`

**متدهای اصلی:**

```python
class ProductCommentService:
    def create_comment(self, 
                      user: User, 
                      product_id: int, 
                      text: str, 
                      rating: int) -> ProductComment:
        """
        ایجاد نظر جدید
        
        Args:
            user: کاربر
            product_id: ID محصول
            text: متن نظر
            rating: امتیاز (1-5)
        
        Returns:
            ProductComment: نظر ایجاد شده
        
        Raises:
            ValidationError: اگر داده‌ها نامعتبر باشند
        """
        pass
    
    def get_product_comments(self, 
                            product_id: int, 
                            page: int = 1, 
                            page_size: int = 20) -> PaginatedResponse:
        """
        دریافت نظرات یک محصول
        
        Args:
            product_id: ID محصول
            page: شماره صفحه
            page_size: تعداد آیتم
        
        Returns:
            PaginatedResponse: لیست نظرات
        """
        pass
    
    def approve_comment(self, comment_id: int) -> bool:
        """
        تأیید نظر (برای نمایش عمومی)
        
        Args:
            comment_id: ID نظر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        pass
    
    def get_average_rating(self, product_id: int) -> float:
        """
        محاسبه میانگین امتیاز محصول
        
        Args:
            product_id: ID محصول
        
        Returns:
            float: میانگین امتیاز (0-5)
        """
        pass
```

**مثال استفاده:**
```python
from apps.shop.services.product_comment_service import ProductCommentService

service = ProductCommentService()

# ایجاد نظر
comment = service.create_comment(
    user=user,
    product_id=123,
    text='محصول عالی بود!',
    rating=5
)

# دریافت نظرات محصول
comments = service.get_product_comments(product_id=123, page=1, page_size=20)

# تأیید نظر (ادمین)
service.approve_comment(comment_id=456)

# محاسبه میانگین امتیاز
avg_rating = service.get_average_rating(product_id=123)
print(f"میانگین امتیاز: {avg_rating}")
```

**لاگ‌گذاری:**
```python
logger = logging.getLogger('shop.services.feedback')
```

---

## فیلترها

### 📍 موقعیت: `backend/apps/shop/filters.py`

### توضیحات:
فیلترهای سفارشی برای فیلتر کردن محصولات.

**فیلترهای اصلی:**

```python
import django_filters
from core.product.models import Product

class ProductFilter(django_filters.FilterSet):
    """
    فیلتر محصولات
    """
    category = django_filters.NumberFilter(
        field_name='category__id',
        label='دسته‌بندی'
    )
    
    min_price = django_filters.NumberFilter(
        field_name='base_price',
        lookup_expr='gte',
        label='حداقل قیمت'
    )
    
    max_price = django_filters.NumberFilter(
        field_name='base_price',
        lookup_expr='lte',
        label='حداکثر قیمت'
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='جستجو'
    )
    
    is_featured = django_filters.BooleanFilter(
        label='فقط محصولات ویژه'
    )
    
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('base_price', 'price'),
            ('name', 'name'),
        ),
        field_labels={
            'created_at': 'تاریخ ایجاد',
            'base_price': 'قیمت',
            'name': 'نام',
        }
    )
    
    def filter_search(self, queryset, name, value):
        """جستجو در نام و توضیحات محصول"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value)
        )
    
    class Meta:
        model = Product
        fields = [
            'category',
            'min_price',
            'max_price',
            'search',
            'is_featured'
        ]
```

**استفاده در View:**
```python
from apps.shop.filters import ProductFilter

class ProductListView(APIView):
    def get(self, request):
        queryset = Product.objects.filter(is_active=True)
        
        # اعمال فیلترها
        filter_backend = DjangoFilterBackend()
        filtered_queryset = filter_backend.filter_queryset(
            request, queryset, ProductListView
        )
        
        # پاگینیشن
        page = paginate_queryset(filtered_queryset, request)
        serializer = ProductSerializer(page, many=True)
        
        return get_paginated_response(serializer.data)
```

---

## وظایف Celery

### 📍 موقعیت: `backend/apps/shop/tasks.py`

### توضیحات:
وظایف ناهمزمان برای عملیات زمان‌بر فروشگاه.

**وظایف اصلی:**

```python
from celery import shared_task
from apps.shop.services.product_list_service import ProductListService

@shared_task
def update_product_ratings(product_id: int) -> bool:
    """
    به‌روزرسانی میانگین امتیاز محصول
    
    Args:
        product_id: ID محصول
    
    Returns:
        bool: موفقیت‌آمیز بودن عملیات
    """
    pass

@shared_task
def generate_product_report(start_date: str, end_date: str) -> dict:
    """
    تولید گزارش محصولات
    
    Args:
        start_date: تاریخ شروع
        end_date: تاریخ پایان
    
    Returns:
        dict: گزارش
    """
    pass
```

**مثال استفاده:**
```python
# فراخوانی وظیفه
from apps.shop.tasks import update_product_ratings

# ارسال به صورت ناهمزمان
update_product_ratings.delay(product_id=123)
```

---

## نکات مهم

### 1. **قیمت‌گذاری پیچیده**
- ✅ قیمت نهایی بر اساس ویژگی‌های انتخابی محاسبه می‌شود
- ✅ از ProductCalculator برای محاسبه استفاده می‌شود
- ✅ قیمت در زمان افزودن به سبد خرید ذخیره می‌شود

### 2. **فیلتر کردن**
- ✅ استفاده از django-filter برای فیلتر کردن
- ✅ جستجو در نام و توضیحات محصول
- ✅ فیلتر بر اساس قیمت، دسته‌بندی و ...

### 3. **پاگینیشن**
- ✅ پیش‌فرض: 20 آیتم در هر صفحه
- ✅ حداکثر: 100 آیتم در هر صفحه
- ✅ قابل تنظیم با پارامتر `page_size`

### 4. **محصولات ویژه**
- ✅ محصولات ویژه با `is_featured=True` علامت‌گذاری می‌شوند
- ✅ در صفحه اصلی نمایش داده می‌شوند

### 5. **امتیاز و نظرات**
- ✅ نظرات قبل از نمایش عمومی نیاز به تأیید دارند
- ✅ میانگین امتیاز به صورت خودکار محاسبه می‌شود

### 6. **لاگ‌گذاری**
```python
logger = logging.getLogger('shop.services.product_list')
logger = logging.getLogger('shop.services.product_detail')
logger = logging.getLogger('shop.services.price_calculator')
logger = logging.getLogger('shop.services.order_creation')
logger = logging.getLogger('shop.services.feedback')
```

### 7. **بهینه‌سازی**
- ✅ استفاده از select_related و prefetch_related برای بهینه‌سازی کوئری‌ها
- ✅ کش کردن لیست محصولات با Redis
- ✅ فشرده‌سازی تصاویر محصول

---

## 🔗 مستندات مرتبط

- **[مستندات اپلیکیشن‌ها](./README.md)** - مستندات اصلی اپلیکیشن‌ها
- **[مستندات Core](../core/README.md)** - مستندات ماژول Core (مدل‌های محصول)
- **[مستندات API](../api/README.md)** - مستندات لایه API

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-24  
**آخرین به‌روزرسانی:** 2026-01-24  
**نگهبان:** تیم توسعه Printoo24