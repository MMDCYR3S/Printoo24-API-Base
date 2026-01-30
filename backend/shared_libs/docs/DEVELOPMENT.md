# راهنمای توسعه و Contribution

## 📖 مقدمه

این مستند راهنمای کامل برای توسعه‌دهندگان است که قصد دارند در پروژه Printoo24 مشارکت کنند یا کد جدیدی به کتابخانه `shared_libs` اضافه کنند.

---

## 🚀 شروع کار

### پیش‌نیازها

- Python 3.8+
- Django 4.0+
- PostgreSQL (توصیه می‌شود)
- Git
- Docker & Docker Compose (برای محیط توسعه)

### راه‌اندازی محیط توسعه

#### 1. کلون کردن پروژه

```bash
git clone <repository-url>
cd Printoo24-API-Base
```

#### 2. نصب وابستگی‌ها

```bash
# ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows

# نصب وابستگی‌ها
pip install -r requirements.txt

# نصب کتابخانه مشترک در حالت editable
cd backend/shared_libs
pip install -e .
```

#### 3. تنظیمات پایگاه داده

```bash
# ایجاد فایل .env
cp .env.example .env

# اجرای migrations
cd ../admin_site  # یا customer_site
python manage.py migrate

# ایجاد superuser (اختیاری)
python manage.py createsuperuser
```

---

## 📁 ساختار کد

### سازماندهی دامنه‌ها

هر دامنه باید ساختار زیر را داشته باشد:

```
domain_name/
├── __init__.py
├── models.py              # مدل‌های دامنه
├── exceptions.py          # Exceptionهای اختصاصی
├── managers/              # Repository Pattern
│   ├── __init__.py
│   ├── base.py           # BaseQuerySet
│   └── *.py              # Repositoryهای تخصصی
└── services/              # Domain Services
    ├── __init__.py
    └── *.py              # سرویس‌های مختلف
```

### نام‌گذاری

#### کلاس‌ها

- **Models:** `PascalCase` (مثلاً `Product`, `OrderItem`)
- **Services:** `PascalCase` + `Service` (مثلاً `ProductService`, `OrderService`)
- **Managers:** `PascalCase` + `Manager` (مثلاً `ProductManager`, `OrderManager`)
- **QuerySets:** `PascalCase` + `QuerySet` (مثلاً `ProductQuerySet`, `OrderQuerySet`)
- **Exceptions:** `PascalCase` + `Exception` (مثلاً `ProductNotFoundException`)

#### متدها

- **Repository Methods:** `snake_case` با پیشوند توصیفی (مثلاً `get_product_by_slug`, `create_order`)
- **Service Methods:** `snake_case` (مثلاً `get_product_detail`, `create_order_direct`)

#### فایل‌ها

- **Models:** `models.py`
- **Services:** `service_name.py` (مثلاً `product.py`, `order.py`)
- **Managers:** `entity_name.py` (مثلاً `product.py`, `order.py`)

---

## 🔨 توسعه جدید

### افزودن مدل جدید

#### 1. تعریف مدل در `models.py`

```python
# core/domain/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class NewModel(models.Model):
    """توضیحات مدل"""
    
    name = models.CharField(_('نام'), max_length=255)
    is_active = models.BooleanField(_('فعال'), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    
    class Meta:
        verbose_name = _('مدل جدید')
        verbose_name_plural = _('مدل‌های جدید')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

#### 2. ایجاد Migration

```bash
python manage.py makemigrations core
python manage.py migrate
```

#### 3. اضافه کردن به `__init__.py`

```python
# core/models/__init__.py
from core.domain.models import NewModel
```

---

### افزودن Repository جدید

#### 1. ایجاد QuerySet در `managers/base.py` یا فایل جدید

```python
# core/domain/managers/entity.py
from django.db import models
from .base import BaseQuerySet

class NewModelQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به NewModel"""
    
    def get_active(self):
        """دریافت رکوردهای فعال"""
        return self.filter(is_active=True)
    
    def get_by_name(self, name: str):
        """دریافت با نام"""
        return self.filter(name=name).first()

class NewModelManager(models.Manager):
    """Repository برای دسترسی به NewModel"""
    
    def get_queryset(self):
        return NewModelQuerySet(self.model, using=self._db)
    
    def get_active_models(self):
        return self.get_queryset().get_active()
    
    def get_by_name(self, name: str):
        return self.get_queryset().get_by_name(name)
```

#### 2. اضافه کردن Manager به مدل

```python
# core/domain/models.py
class NewModel(models.Model):
    # ...
    objects = NewModelManager()
```

#### 3. Export در `__init__.py`

```python
# core/domain/managers/__init__.py
from .entity import NewModelManager
```

---

### افزودن Service جدید

#### 1. ایجاد Service

```python
# core/domain/services/new_service.py
from typing import Dict, Any
from django.db import transaction
from ..models import NewModel
from ..exceptions import NewModelNotFoundException

class NewService:
    """سرویس مدیریت منطق NewModel"""
    
    def get_by_id(self, model_id: int) -> NewModel:
        """دریافت با ID"""
        model = NewModel.objects.get_by_id(model_id)
        if not model:
            raise NewModelNotFoundException("یافت نشد")
        return model
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> NewModel:
        """ایجاد جدید"""
        return NewModel.objects.create(**data)
    
    @transaction.atomic
    def update(self, model_id: int, data: Dict[str, Any]) -> NewModel:
        """ویرایش"""
        model = self.get_by_id(model_id)
        for key, value in data.items():
            setattr(model, key, value)
        model.save()
        return model
```

#### 2. Export در `__init__.py`

```python
# core/domain/services/__init__.py
from .new_service import NewService
```

---

### افزودن Exception جدید

```python
# core/domain/exceptions.py

class NewModelNotFoundException(Exception):
    """استثنا برای زمانی که NewModel یافت نشد"""
    pass

class InvalidNewModelDataException(Exception):
    """استثنا برای داده‌های نامعتبر"""
    pass
```

---

## ✅ اصول کدنویسی

### 1. Repository Pattern

**همیشه از Repository استفاده کنید، نه کوئری مستقیم:**

```python
# ✅ صحیح
product = Product.objects.get_product_by_slug('slug')

# ❌ غلط
product = Product.objects.get(slug='slug')
```

### 2. Domain Services

**منطق تجاری در Services، نه در Views:**

```python
# ✅ صحیح
service = ProductService()
product = service.get_product_detail_by_slug('slug')

# ❌ غلط
product = Product.objects.get(slug='slug')
# محاسبه قیمت در View
price = calculate_price(product, quantity)  # ❌
```

### 3. Exception Handling

**استفاده از Exceptionهای اختصاصی:**

```python
# ✅ صحیح
from core.product.exceptions import ProductNotFoundException

try:
    product = service.get_product_by_slug('slug')
except ProductNotFoundException:
    return Response({'error': 'یافت نشد'}, status=404)

# ❌ غلط
try:
    product = Product.objects.get(slug='slug')
except Product.DoesNotExist:  # ❌ Exception عمومی
    pass
```

### 4. Transaction Management

**استفاده از @transaction.atomic برای عملیات چند مرحله‌ای:**

```python
# ✅ صحیح
@transaction.atomic
def create_order(self, user, items):
    order = Order.objects.create(...)
    for item in items:
        OrderItem.objects.create(order=order, ...)
    return order

# ❌ غلط
def create_order(self, user, items):
    order = Order.objects.create(...)  # اگر خطا بدهد، Order ایجاد شده می‌ماند
    for item in items:
        OrderItem.objects.create(order=order, ...)
    return order
```

### 5. Query Optimization

**استفاده از select_related و prefetch_related:**

```python
# ✅ صحیح
def _get_detail_queryset(self):
    return self.select_related(
        'pricing_config'
    ).prefetch_related(
        'categories',
        'product_image'
    )

# ❌ غلط
def get_product(self, id):
    return self.get(id)  # N+1 Query!
```

### 6. Documentation

**همیشه docstring اضافه کنید:**

```python
# ✅ صحیح
def get_product_by_slug(self, slug: str) -> Product:
    """
    دریافت محصول با اسلاگ.
    
    Args:
        slug: اسلاگ محصول
        
    Returns:
        Product object یا None
        
    Raises:
        ProductNotFoundException: اگر محصول یافت نشد
    """
    product = self.get_queryset().filter(slug=slug, is_active=True).first()
    if not product:
        raise ProductNotFoundException(f"محصول با اسلاگ '{slug}' یافت نشد")
    return product
```

---

## 🧪 تست‌نویسی

### ساختار تست‌ها

```python
# tests/test_domain/test_services/test_new_service.py
from django.test import TestCase
from core.domain.services import NewService
from core.domain.exceptions import NewModelNotFoundException

class NewServiceTestCase(TestCase):
    def setUp(self):
        self.service = NewService()
        # ایجاد داده‌های تست
    
    def test_get_by_id_success(self):
        """تست دریافت موفق"""
        model = self.service.get_by_id(1)
        self.assertIsNotNone(model)
    
    def test_get_by_id_not_found(self):
        """تست دریافت ناموفق"""
        with self.assertRaises(NewModelNotFoundException):
            self.service.get_by_id(999)
    
    def test_create_model(self):
        """تست ایجاد"""
        data = {'name': 'Test'}
        model = self.service.create(data)
        self.assertEqual(model.name, 'Test')
```

### اجرای تست‌ها

```bash
# اجرای تمام تست‌ها
python manage.py test

# اجرای تست‌های یک دامنه خاص
python manage.py test core.domain

# اجرای یک تست خاص
python manage.py test core.domain.tests.test_services.test_new_service.NewServiceTestCase.test_create_model
```

---

## 📝 Commit Messages

از استاندارد Conventional Commits استفاده کنید:

```
type(scope): subject

body (اختیاری)

footer (اختیاری)
```

**انواع (Types):**
- `feat`: ویژگی جدید
- `fix`: رفع باگ
- `docs`: تغییرات مستندات
- `style`: فرمت‌بندی (بدون تغییر منطق)
- `refactor`: بازنویسی کد
- `test`: افزودن/تغییر تست‌ها
- `chore`: تغییرات در build/tooling

**مثال‌ها:**

```
feat(product): add price calculator service

docs(architecture): update repository pattern documentation

fix(order): fix race condition in order creation

refactor(users): simplify customer service methods
```

---

## 🔍 Code Review Checklist

قبل از درخواست Pull Request، بررسی کنید:

### کد

- [ ] کد از Repository Pattern استفاده می‌کند
- [ ] منطق تجاری در Services است، نه در Views
- [ ] از Exceptionهای اختصاصی استفاده شده
- [ ] از `@transaction.atomic` برای عملیات چند مرحله‌ای استفاده شده
- [ ] کوئری‌ها بهینه شده‌اند (select_related/prefetch_related)
- [ ] Docstring برای تمام متدهای public وجود دارد

### تست

- [ ] تست‌های واحد (Unit Tests) نوشته شده‌اند
- [ ] تمام تست‌ها پاس می‌شوند
- [ ] Coverage مناسب است (حداقل 70%)

### مستندات

- [ ] README.md به‌روز شده (در صورت نیاز)
- [ ] Docstring‌ها واضح و کامل هستند
- [ ] تغییرات در CHANGELOG.md ثبت شده‌اند (در صورت نیاز)

---

## 🐛 دیباگ و Troubleshooting

### مشکلات رایج

#### 1. ModuleNotFoundError

**مشکل:** `ModuleNotFoundError: No module named 'core'`

**راه‌حل:**
```bash
# اطمینان از نصب در حالت editable
cd backend/shared_libs
pip install -e .
```

#### 2. Migration Conflicts

**مشکل:** خطا در اجرای migrations

**راه‌حل:**
```bash
# بررسی migrations
python manage.py showmigrations core

# ایجاد migration جدید
python manage.py makemigrations core

# اجرای migrations
python manage.py migrate
```

#### 3. N+1 Query Problem

**مشکل:** کوئری‌های زیاد در logs

**راه‌حل:**
```python
# استفاده از select_related و prefetch_related
products = Product.objects.select_related('category').prefetch_related('images')
```

#### 4. Transaction Errors

**مشکل:** خطاهای مربوط به transaction

**راه‌حل:**
```python
# استفاده از @transaction.atomic
from django.db import transaction

@transaction.atomic
def create_order(...):
    # عملیات چند مرحله‌ای
    pass
```

---

## 📚 منابع مفید

### مستندات داخلی

- [README.md](./README.md) - راهنمای شروع
- [ARCHITECTURE.md](./ARCHITECTURE.md) - معماری و الگوها
- [MODELS.md](./MODELS.md) - مستندات مدل‌ها
- [SERVICES.md](./SERVICES.md) - مستندات سرویس‌ها

### مستندات خارجی

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---

## 🤝 مشارکت

### فرآیند Contribution

1. **Fork کردن پروژه**
2. **ایجاد Branch جدید:**
   ```bash
   git checkout -b feat/new-feature
   ```
3. **توسعه و Commit:**
   ```bash
   git add .
   git commit -m "feat(domain): add new feature"
   ```
4. **Push کردن به Fork:**
   ```bash
   git push origin feat/new-feature
   ```
5. **ایجاد Pull Request**

### قوانین

- ✅ کد باید قابل خواندن و maintainable باشد
- ✅ تمام تست‌ها باید پاس شوند
- ✅ مستندات باید به‌روز باشد
- ✅ Code Style باید رعایت شود (PEP 8)
- ✅ Commit Messages باید واضح باشند

---

## 📞 تماس

برای سوالات یا کمک:

- **Developer:** Mohammad Amin Gholami
- **Email:** amingholami06@gmail.com

---

**آخرین به‌روزرسانی:** ۱۴۰۴

