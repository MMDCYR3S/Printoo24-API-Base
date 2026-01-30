# معماری کتابخانه مشترک Printoo24

## 📐 مقدمه

این مستند به بررسی معماری، الگوهای طراحی و ساختار لایه‌ای کتابخانه `shared_libs` می‌پردازد. هدف از این معماری، ایجاد یک پایه محکم و مقیاس‌پذیر برای پروژه Printoo24 با جداسازی کامل منطق تجاری از لایه نمایش است.

---

## 🏛️ معماری کلی

کتابخانه `shared_libs` بر اساس اصول **Domain-Driven Design (DDD)** طراحی شده است. در این معماری:

- **منطق تجاری** کاملاً از لایه نمایش (Views/API) جدا شده است
- هر دامنه (Domain) دارای ساختار مستقل با مدل‌ها، Repositoryها و سرویس‌های خود است
- قوانین هسته سیستم (مثل محاسبه قیمت یا ثبت سفارش) در این کتابخانه متمرکز شده‌اند
- همه سرویس‌ها (admin_site و customer_site) از یک منطق واحد استفاده می‌کنند

### قانون طلایی ⭐

> **هیچ کوئری مستقیم دیتابیس یا منطق محاسباتی نباید در View نوشته شود. همه چیز باید از طریق Service و Repository انجام شود.**

---

## 📦 ساختار لایه‌ای

هر دامنه در `core` از ساختار زیر پیروی می‌کند:

```
domain_name/
├── models.py              # مدل‌های دامنه
├── managers/              # Repository Pattern (دسترسی به داده)
│   ├── base.py           # BaseQuerySet مشترک
│   └── *.py              # Repositoryهای تخصصی
├── services/              # Domain Services (منطق تجاری)
│   └── *.py              # سرویس‌های مختلف
└── exceptions.py          # Exceptionهای اختصاصی دامنه
```

### ۱. لایه مدل‌ها (Data Layer)

**مسئولیت:** تعریف ساختار داده و روابط بین موجودیت‌ها

مدل‌ها در Django ORM تعریف می‌شوند و شامل:
- فیلدهای داده
- روابط (ForeignKey, ManyToMany, OneToOne)
- متدهای سفارشی
- Meta کلاس برای تنظیمات

**مثال:**
```python
# core/product/models.py
class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
```

---

### ۲. لایه Repository (Data Access Layer)

**الگو:** Repository Pattern

**مسئولیت:** 
- کپسوله‌سازی دسترسی به داده
- جلوگیری از N+1 Query با استفاده از `select_related` و `prefetch_related`
- ارائه متدهای خوانا و قابل استفاده مجدد برای دسترسی به داده

#### ساختار Repository

هر Repository شامل دو بخش است:

1. **QuerySet (کلاس اصلی کوئری‌ها)**
   - ارث‌بری از `BaseQuerySet` یا `models.QuerySet`
   - متدهای کوئری تخصصی
   - بهینه‌سازی کوئری‌ها

2. **Manager (نماینده Repository)**
   - ارث‌بری از `models.Manager`
   - متدهای دسترسی به QuerySet
   - رابط عمومی برای استفاده

**مثال:**
```python
# core/product/managers/product.py

class ProductQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به مدل Product"""
    
    def _get_detail_queryset(self):
        """کوئری‌ست بهینه‌شده با eager loading"""
        return self.select_related(
            'pricing_config'
        ).prefetch_related(
            'categories',
            'product_image',
            Prefetch('options', queryset=...)
        )
    
    def get_detail_by_slug(self, slug: str):
        """دریافت محصول با جزئیات کامل"""
        try:
            return self._get_detail_queryset().get(slug=slug, is_active=True)
        except self.model.DoesNotExist:
            return None

class ProductManager(models.Manager):
    """Repository برای دسترسی به محصولات"""
    
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    
    def get_product_by_slug(self, slug: str):
        return self.get_queryset().get_detail_by_slug(slug)
```

**ویژگی‌های کلیدی:**

- ✅ **جلوگیری از N+1 Query:** استفاده گسترده از `select_related` و `prefetch_related`
- ✅ **تراکنش‌های امن:** استفاده از `select_for_update` برای عملیات مالی
- ✅ **تمیزی کد:** متدهای پیچیده پشت رابط‌های ساده پنهان می‌شوند
- ✅ **قابل استفاده مجدد:** کوئری‌های بهینه در تمام سرویس‌ها قابل استفاده

**استفاده در کد:**
```python
# ✅ صحیح - استفاده از Repository
product = Product.objects.get_product_by_slug('product-slug')

# ❌ غلط - کوئری مستقیم در View
product = Product.objects.get(slug='product-slug')  # N+1 Query!
```

---

### ۳. لایه Domain Services (Business Logic Layer)

**مسئولیت:** اجرای قوانین تجاری و منطق بیزنس

سرویس‌های دامنه:
- هیچ وابستگی به `Request` یا `Response` وب ندارند
- منطق تجاری پیچیده را کپسوله می‌کنند
- از Repositoryها برای دسترسی به داده استفاده می‌کنند
- Exceptionهای اختصاصی پرتاب می‌کنند

**مثال - سرویس سفارش:**
```python
# core/order/services/order.py

class OrderService:
    """سرویس دامنه مدیریت سفارشات"""
    
    def get_order_details(self, user_id: int, order_id: int) -> Order:
        """دریافت جزئیات سفارش برای کاربر"""
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد")
        return order
    
    @transaction.atomic
    def create_order_direct(self, user_id: int, address_id: int, items_data: List[Dict]) -> Order:
        """ایجاد مستقیم سفارش (توسط ادمین)"""
        # 1. دریافت و اعتبارسنجی داده‌ها
        user = get_object_or_404(User, pk=user_id)
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        
        # 2. محاسبه قیمت
        calculated_total = Decimal(0)
        # ... منطق محاسبه
        
        # 3. ایجاد سفارش به صورت اتمی
        order = Order.objects.create(...)
        # ... ایجاد آیتم‌ها
        
        return order
```

**مثال - سرویس محاسبه قیمت:**
```python
# core/product/services/calculator.py

class ProductPriceCalculator:
    """موتور محاسبه قیمت محصول"""
    
    def __init__(self, product: Product, quantity: int, width: float = 0, height: float = 0, ...):
        self.product = product
        self.quantity = quantity
        # ... تنظیمات
    
    def calculate(self) -> Dict[str, Union[float, Dict]]:
        """محاسبه قیمت نهایی با جزئیات کامل"""
        # 1. محاسبه قیمت پایه
        base_unit_cost = self._calculate_base_unit_cost()
        
        # 2. محاسبه هزینه آپشن‌ها
        options_unit_cost = self._calculate_options_unit_cost(base_unit_cost)
        
        # 3. اعمال تیراژ و ضریب
        total_items_price = (base_unit_cost + options_unit_cost) * self.qty_multiplier
        
        # 4. هزینه‌های سربار
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        
        # 5. اعمال مودیفایر درصدی
        if self.product.price_modifier_percent:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier
        
        # 6. گرد کردن نهایی
        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)
        
        return {
            "final_price": float(final_price),
            "breakdown": {...}
        }
```

**ویژگی‌های سرویس‌های دامنه:**

- ✅ **مستقل از Framework:** بدون وابستگی به Django Views/Requests
- ✅ **قابل تست:** به راحتی قابل Unit Testing
- ✅ **قابل استفاده مجدد:** در admin_site و customer_site یکسان عمل می‌کنند
- ✅ **Atomic Operations:** استفاده از `@transaction.atomic` برای عملیات مهم

---

### ۴. لایه Infrastructure (زیرساخت)

**مسئولیت:** ارائه سرویس‌های زیرساختی مشترک

این لایه شامل سرویس‌هایی است که توسط سایر بخش‌ها استفاده می‌شوند:

#### Cache Service

```python
# core/infrastructure/cache.py

class CacheService:
    """سرویس کش برای سیستم"""
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        cache.set(key, value, timeout)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return cache.get(key, default)
    
    def delete(self, key: str) -> None:
        cache.delete(key)
```

#### Email Service

```python
# core/infrastructure/email.py

class EmailService:
    """سرویس ارسال ایمیل"""
    
    def send(self, subject: str, template_name: str, context: dict, 
             from_email: str, to_email: str) -> None:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message
        )
```

---

## 🔄 جریان داده (Data Flow)

### جریان معمول درخواست:

```
Request (View)
    ↓
Domain Service (منطق تجاری)
    ↓
Repository (دسترسی به داده)
    ↓
Database (ORM)
```

### مثال واقعی:

```python
# در View (customer_site/api/v1/cart/views.py)
def checkout(request):
    cart_service = CartDomainService()
    
    try:
        order = cart_service.checkout_cart(
            user=request.user,
            address_id=request.data['address_id']
        )
        return Response({'order_id': order.id})
    
    except InsufficientFundsException as e:
        return Response({'error': str(e)}, status=400)

# در Domain Service (shared_libs/core/order/services/order.py)
class OrderService:
    @transaction.atomic
    def checkout_cart(self, user, address_id):
        # استفاده از Repository
        cart = Cart.objects.get_active_cart(user)
        if not cart:
            raise CartNotFoundException()
        
        # منطق تجاری
        order = self._create_order_from_cart(cart, address_id)
        
        # استفاده از Repository
        Cart.objects.clear_cart(cart)
        
        return order
```

---

## 🎯 الگوهای طراحی استفاده شده

### ۱. Repository Pattern

**هدف:** جداسازی منطق دسترسی به داده از منطق تجاری

**پیاده‌سازی:** استفاده از Django Managers و QuerySets

**مزایا:**
- تست‌پذیری بهتر
- تغییرپذیری (می‌توان Repository را با Mock جایگزین کرد)
- جلوگیری از تکرار کوئری‌ها

### ۲. Domain Services Pattern

**هدف:** کپسوله‌سازی منطق تجاری پیچیده

**مثال:** `ProductPriceCalculator`, `OrderService`

**مزایا:**
- قوانین بیزنس در یک مکان متمرکز
- قابل استفاده مجدد در چندین View
- مستقل از لایه نمایش

### ۳. Exception Handling Pattern

**هدف:** مدیریت خطاهای معنادار

هر دامنه Exceptionهای اختصاصی خود را دارد:

```python
# core/users/exceptions.py
class EmailAlreadyExistsException(Exception):
    pass

class UserNotFoundException(Exception):
    pass

# استفاده در Service
def get_user_by_email(email: str):
    user = User.objects.filter(email=email).first()
    if not user:
        raise UserNotFoundException("کاربر یافت نشد")
    return user
```

**مزایا:**
- خطاهای معنادار برای کاربر
- جداسازی نگرانی‌ها (Service خطا می‌دهد، View تصمیم می‌گیرد)
- قابل تست و دیباگ

---

## 🚨 مدیریت تراکنش‌ها (Transactions)

برای عملیات مهم (مثل ایجاد سفارش یا تغییر موجودی)، از `@transaction.atomic` استفاده می‌شود:

```python
from django.db import transaction

class OrderService:
    @transaction.atomic
    def create_order(self, user, items):
        # اگر هر کدام از این عملیات fail شود، همه rollback می‌شوند
        order = Order.objects.create(...)
        for item in items:
            OrderItem.objects.create(order=order, ...)
        Wallet.objects.deduct(user, order.total_price)
```

برای عملیات مالی حساس، از `select_for_update` برای قفل کردن رکورد استفاده می‌شود:

```python
# جلوگیری از Race Condition
wallet = Wallet.objects.select_for_update().get(user=user)
wallet.balance -= amount
wallet.save()
```

---

## 🔔 Django Signals

سیگنال‌ها برای اجرای خودکار فرآیندها استفاده می‌شوند:

```python
# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ProductCategoryRelation)
def generate_code_on_relation_creation(sender, instance, created, **kwargs):
    """تولید خودکار کد محصول پس از اختصاص دسته‌بندی"""
    if created and not instance.product.code:
        category = instance.category
        root_category = category.get_root()
        year = timezone.now().year
        new_code = product_code_generator(
            root_category.slug, 
            instance.product.slug, 
            year
        )
        Product.objects.filter(pk=instance.product.pk).update(code=new_code)
```

**مزایا:**
- جداسازی نگرانی‌ها (Decoupling)
- توسعه‌پذیری (Extensibility)
- یکپارچگی داده (Data Integrity)

---

## 📊 دیاگرام معماری

```
┌─────────────────────────────────────────────────────┐
│              Views/API Layer                        │
│  (admin_site/api, customer_site/api)               │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│            Domain Services Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ OrderService │  │ProductService│  │UserService│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│          Repository Layer (Managers)                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │OrderManager  │  │ProductManager│  │UserManager│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│              Models Layer (ORM)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │    Order     │  │   Product    │  │   User    │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└───────────────────┬─────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│                Database (PostgreSQL)                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          Infrastructure Services                    │
│  ┌──────────────┐  ┌──────────────┐                │
│  │CacheService  │  │EmailService  │                │
│  └──────────────┘  └──────────────┘                │
└─────────────────────────────────────────────────────┘
```

---

## ✅ اصول طراحی

### 1. Separation of Concerns (جداسازی نگرانی‌ها)

هر لایه مسئولیت مشخصی دارد:
- **Models:** ساختار داده
- **Repositories:** دسترسی به داده
- **Services:** منطق تجاری
- **Views:** تبدیل درخواست/پاسخ

### 2. Don't Repeat Yourself (DRY)

- منطق مشترک در Services
- کوئری‌های مشترک در Repositories
- Utilityها در Infrastructure

### 3. Single Responsibility Principle (SRP)

هر کلاس یک مسئولیت دارد:
- `ProductPriceCalculator` فقط قیمت محاسبه می‌کند
- `OrderService` فقط سفارشات را مدیریت می‌کند

### 4. Dependency Inversion Principle (DIP)

Services به Repositoryهای انتزاعی وابسته‌اند، نه به پیاده‌سازی‌های خاص.

---

## 🎓 بهترین روش‌ها (Best Practices)

### ✅ انجام دهید:

1. **همیشه از Repository استفاده کنید:**
   ```python
   # ✅ صحیح
   product = Product.objects.get_product_by_slug('slug')
   
   # ❌ غلط
   product = Product.objects.get(slug='slug')
   ```

2. **منطق تجاری در Services:**
   ```python
   # ✅ صحیح
   order_service = OrderService()
   order = order_service.create_order(user, items)
   
   # ❌ غلط
   order = Order.objects.create(...)  # در View
   ```

3. **استفاده از Exceptionهای اختصاصی:**
   ```python
   # ✅ صحیح
   if not product:
       raise ProductNotFoundException()
   
   # ❌ غلط
   return None  # بدون اطلاع از نوع خطا
   ```

4. **استفاده از Atomic Transactions:**
   ```python
   @transaction.atomic
   def create_order(self, ...):
       # عملیات چند مرحله‌ای
   ```

### ❌ انجام ندهید:

1. ❌ کوئری مستقیم در View
2. ❌ منطق تجاری در View
3. ❌ N+1 Query
4. ❌ تراکنش‌های ناامن
5. ❌ تکرار کد (DRY Violation)

---

## 📚 منابع بیشتر

- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---

**آخرین به‌روزرسانی:** ۱۴۰۴

