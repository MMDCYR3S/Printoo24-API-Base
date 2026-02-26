import random
from slugify import slugify as unicode_slugify
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey

from .managers import (
    ProductManager, 
    ProductImageManager, 
    AttachmentManager,
    ProductCategoryManager,
    ProductRatingManager, 
    ProductCommentManager
)

# ======== Guide Type ======== #
class GuideType(models.TextChoices):
    """
    انواع پیام‌های راهنما برای نمایش به کاربر
    """
    INFO = 'info', _('اطلاعات')
    WARNING = 'warning', _('هشدار')
    TIP = 'tip', _('نکته)')
    
# ======== Has Guide Model ======== #
class HasGuide(models.Model):
    """
    میکسین یکپارچه برای مدیریت راهنماها و هشدارها.
    هر مدلی که نیاز به توضیحات اضافی برای کاربر دارد از این کلاس ارث‌بری می‌کند.
    """
    guide_text = models.TextField(
        _("متن راهنما/هشدار"), 
        blank=True, null=True, 
        help_text=_("متنی که با کلیک روی آیکون مربوطه نمایش داده می‌شود.")
    )
    guide_type = models.CharField(
        _("نوع پیام"),
        max_length=20,
        choices=GuideType.choices,
        default=GuideType.INFO,
        help_text=_("رنگ و آیکون نمایش داده شده را تعیین می‌کند.")
    )

    class Meta:
        abstract = True

    @property
    def has_guide(self):
        return bool(self.guide_text)

# ======= OPTION INPUT TYPE MODEL ======= #
class OptionInputType(models.TextChoices):
    """
    انواع ورودی برای رندر کردن در فرانت‌اند
    """
    TEXT = 'text', _('ورودی متنی (Text)')
    TEXTAREA = 'textarea', _('ورودی متن بلند (Textarea)')
    NUMBER = 'number', _('ورودی عددی (Number)')
    SELECT = 'select', _('لیست کشویی (Select)')
    RADIO = 'radio', _('رادیو باتن (Radio)')
    CHECKBOX = 'checkbox', _('چک‌باکس چندتایی (Checkbox)')
    MULTI_SELECT = 'multi_select', _('انتخاب چندگانه (Multi Select / Checkboxes)')

# ======== OPTION ABSTRACT MODEL ======== #
class BaseOptionDefinition(HasGuide, models.Model):
    """
    کلاس پایه برای تعریف 'صورت‌مسئله' ویژگی.
    دارای input_type است تا مشکل نوع ورودی در ویژگی‌های کاستوم حل شود.
    """
    name = models.CharField(
        _("نام سیستمی"), 
        max_length=150, 
        help_text=_("شناسه یکتا برای کدنویسی (مثال: paper_type)")
    )
    label = models.CharField(_("عنوان نمایشی"), max_length=150, null=True, blank=True)
    # ===== نوع آپشن ===== #
    input_type = models.CharField(
        _("نوع ورودی"),
        max_length=25,
        choices=OptionInputType.choices,
        default=OptionInputType.SELECT
    )

    class Meta:
        abstract = True

# ======== OPTION VALUE ABSTRACT MODEL ======== #
class BaseOptionValueDefinition(HasGuide, models.Model):
    """
    کلاس پایه برای تعریف 'گزینه‌ها/مقادیر'.
    """
    label = models.CharField(_("عنوان مقدار"), max_length=150, null=True, blank=True)
    value = models.CharField(_("کد سیستمی/مقدار"), max_length=150, null=True, blank=True)

    class Meta:
        abstract = True

# ======== Product Code Generator ======== #
def product_code_generator(category_slug, product_slug, year):
    """
    این تابع برای تولید کد یکتا برای محصولات است
    """
    
    random_num = random.randint(1000, 9999)
    code = f"{random_num}-{category_slug.upper()}-{product_slug.upper()[:4]}-{year}"
    return code

# ======== Product Category Model ======== #
class ProductCategory(MPTTModel):
    """
    مدل دسته بندی محصولات
    """

    user = models.ForeignKey("core.User", related_name='product_category', on_delete=models.PROTECT)
    name = models.CharField(_("نام"), max_length=150)
    slug = models.SlugField(_("اسلاگ"), unique=True, blank=True, null=True)
    parent = TreeForeignKey("self", related_name="children", on_delete=models.PROTECT, blank=True, null=True)
    # ===== فیلدهای جدید برای بنر و توضیحات ===== #
    description = models.TextField(_("توضیحات"), blank=True, null=True, help_text=_("توضیحات برای نمایش در بالای صفحه دسته بندی و سئو"))
    banner_wide = models.ImageField(
        _("بنر عریض"), 
        upload_to='categories/banners/', 
        blank=True, 
        null=True,
        help_text=_("تصویر عریض برای هدر صفحه (مثلاً 1920x400)")
    )
    banner_box = models.ImageField(
        _("بنر مربعی/باکس"), 
        upload_to='categories/boxes/', 
        blank=True, 
        null=True,
        help_text=_("تصویر برای نمایش در لیست دسته‌بندی‌ها (مثلاً 400x400)")
    )
    order = models.PositiveIntegerField(
        _("ترتیب نمایش"), 
        default=0, 
        help_text=_("عدد کوچکتر = نمایش در رتبه بالاتر (مثال: 1 بالاتر از 2 است)")
    )
    is_active = models.BooleanField(_("فعال"), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = ProductCategoryManager()
    
    class MPTTMeta:
        """
        این کلاس به MPTT می‌گوید که در حین درج و ساخت درخت، 
        گره‌های هم‌سطح را بر چه اساسی مرتب کند.
        """
        order_insertion_by = ['order', 'name']

    def save(self, *args, **kwargs):
        """ ذخیره اسلاگ به صورت خودکار """
        if not self.slug:
            self.slug = unicode_slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
    # ===== متدهای کمکی (Domain Logic) ===== #
    def get_banner_wide_url(self):
        """
        دریافت آدرس بنر عریض.
        اگر این دسته بنر نداشت، سعی می‌کند از والدش بگیرد (Inheritance).
        """
        if self.banner_wide:
            return self.banner_wide.url
        if self.parent:
            return self.parent.get_banner_wide_url()
        return None 

    def get_descendants_active(self):
        """گرفتن زیرمجموعه‌های فعال"""
        return self.get_descendants().filter(is_active=True)
    
# ======== Product Category Relation ======== #
class ProductCategoryRelation(models.Model):
    """
    جدول واسط صریح برای مدیریت رابطه محصول و دسته‌بندی.
    این جدول به ما اجازه می‌دهد فراداده‌هایی مثل 'is_primary' داشته باشیم.
    """
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE, 
        related_name='category_relations',
        verbose_name=_("محصول")
    )
    category = models.ForeignKey(
        'ProductCategory', 
        on_delete=models.PROTECT, 
        related_name='product_relations',
        verbose_name=_("دسته‌بندی")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("رابطه محصول-دسته")
        verbose_name_plural = _("روابط محصول-دسته")
        unique_together = ('product', 'category')

    def save(self, *args, **kwargs):
        """
        تضمین یکپارچگی داده‌ها (Data Integrity):
        اگر این رکورد به عنوان Primary ست شود، بقیه رکوردهای این محصول باید False شوند.
        """
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} -> {self.category.name}"
    
# ======== Product Model ======== #
class Product(HasGuide, models.Model):
    """
    مدل محصولات مربوط به وبسایت
    این مدل باید به صورت کاملا حرفه ای باشد 
    """

    user = models.ForeignKey(
        'core.User',
        verbose_name=_('کاربر'),
        related_name='products',
        on_delete=models.PROTECT,
    )
    name = models.CharField(_('نام'), max_length=150)
    categories = models.ManyToManyField(
        'ProductCategory',
        through='ProductCategoryRelation', 
        related_name='products',
        verbose_name=_('دسته‌بندی‌ها'),
        blank=True
    )
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True, null=True)
    has_price = models.BooleanField(_('دارای قیمت'), default=True)
    show_price = models.DecimalField(
        _("قیمت نمایشی"),
        max_digits=14,
        decimal_places=2,
        default=0.0
    )
    price = models.DecimalField(
        _('قیمت'),
        max_digits=12, 
        decimal_places=2, 
        default=0.0,
    )
    # ===== قیمت گذاری براساس مقدار ==== #
    price_per_unit = models.PositiveIntegerField(
        _("گام شمارش (تعداد مبنا)"),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_("قیمت بالا به ازای چه تعدادی است؟ (مثلا: ۱۰۰۰ تومان به ازای هر ۱۰ عدد).")
    )
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    code = models.CharField(
        _("کد محصول"),
        max_length=150,
        unique=True,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_('فعال'), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    has_quantity = models.BooleanField(_('دارای تیراژ'), default=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = ProductManager()
    
    def validate_has_price(self) -> bool:
        """
        بررسی اینکه آیا محصول دارای قیمت هست، اگر بله، نباید تیک
        has_price رو کاربر بزنه. از طرفی اگر نه، باید تیک رو بزنه.
        """
        if self.has_price and self.price == 0:
            raise ValidationError('محصول باید قیمت داشته باشد')
        elif not self.has_price and self.price > 0:
            raise ValidationError('نمی توانید تیک گزینه قیمت رو نزنید و سپس قیمت را وارد کنید.')
        elif not self.has_price and self.price == 0:
            return True
         
    def save(self, *args, **kwargs):
        """ ذخیره اسلاگ محصول به صورت خودکار """
        if not self.slug:
            self.slug = unicode_slugify(self.name)
        if self.slug in Product.objects.filter(slug=self.slug).exclude(pk=self.pk):
            raise ValidationError('محصول با این نام قبلا ساخته شده است.')
            
        if not self.code:
            year = timezone.now().year
            
            category_slug = 'PENDING'
            self.code = product_code_generator(category_slug, self.slug, year)
            
        super().save(*args, **kwargs)
    
    # def get_primary_category(self):
    #     """
    #     یک متد کمکی برای دریافت دسته‌بندی اصلی جهت استفاده در لاجیک‌ها.
    #     """
    #     rel = self.category_relations.filter(is_primary=True).select_related('category').first()
    #     if rel:
    #         return rel.category

    #     rel = self.category_relations.select_related('category').first()
    #     return rel.category if rel else None

    def __str__(self):
        return f"{self.name} - {self.code}"

# ======== ENUMS ======== #
class FieldType(models.TextChoices):
    TEXT = 'text', _('متن کوتاه')
    TEXTAREA = 'textarea', _('متن چندخطی')
    NUMBER = 'number', _('عدد')
    SINGLE_SELECT = 'single_select', _('تک انتخابی (Radio)')
    MULTI_SELECT = 'multi_select', _('چند انتخابی (Checkbox)')
    DROPDOWN = 'dropdown', _('کشویی (Select)')

class ConditionOperator(models.TextChoices):
    EQUALS = 'equals', _('برابر با')
    NOT_EQUALS = 'not_equals', _('به غیر از')
    IS_EMPTY = 'is_empty', _('خالی باشد')
    IS_NOT_EMPTY = 'is_not_empty', _('خالی نباشد')

class ConditionAction(models.TextChoices):
    SHOW = 'show', _('آشکار شود')
    HIDE = 'hide', _('پنهان شود')
    ENABLE = 'enable', _('فعال شود')
    DISABLE = 'disable', _('غیرفعال شود')

class MultiSelectOperator(models.TextChoices):
    ADD = 'add', _('جمع (+)')
    SUBTRACT = 'sub', _('تفریق (-)')
    MULTIPLY = 'mul', _('ضرب (*)')
    DIVIDE = 'div', _('تقسیم (/)')

# ======== 1. فرم‌ساز (مدل فیلدها) ======== #
class ProductField(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='fields', verbose_name=_("محصول"))
    title = models.CharField(_("عنوان فیلد"), max_length=150)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    multi_select_operator = models.CharField(
        _("عملگر داخلی چندانتخابی"),
        max_length=10,
        choices=MultiSelectOperator.choices,
        default=MultiSelectOperator.ADD,
        help_text=_("اگر فیلد چندانتخابی است، مقادیرِ تیک‌خورده با چه عملگری با هم محاسبه شوند؟")
    )
    field_type = models.CharField(_("نوع فیلد"), max_length=20, choices=FieldType.choices, default=FieldType.DROPDOWN)
    
    # اضافه شدن مقدار عددی به خود فیلد (طبق دستور شما)
    numeric_value = models.DecimalField(
        _("مقدار عددی پایه (برای فرمول)"), 
        max_digits=14, 
        decimal_places=2, 
        default=0.0,
        help_text=_("اگر خود فیلد به تنهایی دارای ارزش عددی/قیمتی در فرمول است (مستقل از زیرمجموعه‌ها)")
    )
    
    is_required = models.BooleanField(_("اجباری بودن"), default=False)
    is_active = models.BooleanField(_("فعال بودن"), default=True)
    is_quantity_field = models.BooleanField(_("آیا این فیلد همان تیراژ است؟"), default=False)
    
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.title} (ID: {self.id})"


# ======== 2. مقادیر زیرمجموعه ======== #
class ProductFieldChoice(models.Model):
    field = models.ForeignKey(ProductField, on_delete=models.CASCADE, related_name='choices')
    title = models.CharField(_("عنوان مقدار"), max_length=150)
    
    numeric_value = models.DecimalField(
        _("مقدار عددی (برای فرمول)"), 
        max_digits=14, 
        decimal_places=2, 
        default=0.0
    )

    is_default = models.BooleanField(
        _("گزینه پیش‌فرض"), 
        default=False,
        help_text=_("آیا این گزینه در فرانت‌اند به صورت پیش‌فرض انتخاب شده باشد؟")
    )
    
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        """
        تضمین یکپارچگی داده‌ها (Data Integrity):
        اگر این رکورد به عنوان پیش‌فرض ست شود، بقیه رکوردهای هم‌خانواده باید False شوند.
        """
        if self.is_default:
            ProductFieldChoice.objects.filter(field=self.field).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.field.title} -> {self.title} (Value: {self.numeric_value})"


# ======== 3. شرط‌ساز ======== #
class ProductFieldCondition(models.Model):
    target_field = models.ForeignKey(ProductField, on_delete=models.CASCADE, related_name='applied_conditions', verbose_name=_("فیلد هدف"))
    
    trigger_field = models.ForeignKey(ProductField, on_delete=models.CASCADE, related_name='triggering_conditions', verbose_name=_("فیلد شرط"))
    operator = models.CharField(_("عملگر"), max_length=20, choices=ConditionOperator.choices)
    
    trigger_choice = models.ForeignKey(ProductFieldChoice, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("مقدار شرط (برای لیست‌ها)"))
    trigger_value_text = models.CharField(_("مقدار شرط (برای متن/عدد)"), max_length=255, null=True, blank=True)
    
    action = models.CharField(_("عملیات"), max_length=20, choices=ConditionAction.choices)

    def clean(self):
        if self.target_field == self.trigger_field:
            raise ValidationError(_("یک فیلد نمی‌تواند به خودش وابسته باشد."))

    def __str__(self):
        return f"If {self.trigger_field.title} {self.operator} -> {self.action} {self.target_field.title}"


# ======== 4. فرمول‌ساز نهایی ======== #
class ProductFormula(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='formulas')
    title = models.CharField(_("عنوان فرمول"), max_length=150)
    
    condition_expression = models.CharField(
        _("شرط اجرای فرمول"), 
        max_length=255, 
        blank=True, 
        null=True,
        help_text=_("مثال: field_15 > 1000")
    )
    
    # تغییر Help Text بر اساس استفاده از ID
    calculation_expression = models.TextField(
        _("عبارت محاسباتی"),
        help_text=_("فرمول ریاضی با استفاده از ID فیلدها. مثال: (field_12 * field_15) + 500")
    )
    
    currency = models.CharField(
        _("واحد پولی"), 
        max_length=10, 
        default='IQD', 
        editable=False
    )

    def __str__(self):
        return f"{self.product.name} - {self.title}"
        
# ====== Product Image Model ====== #
class ProductImage(models.Model):
    """ مدل عکس محصول """
    user = models.ForeignKey("core.User", related_name='user_product_image', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product_image', on_delete=models.CASCADE)
    image = models.ImageField(_('تصویر'), upload_to='products/')
    order = models.IntegerField(_('ترتیب'), default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = ProductImageManager()

    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name = _('تصویر')
        verbose_name_plural = _('تصاویر')

# ======= Attachement Model ======= #
class Attachment(models.Model):
    """ مدل فایل های پیوست """
    user = models.ForeignKey("core.User", related_name='user_attachments', on_delete=models.PROTECT)
    name = models.CharField(_('نام'), max_length=150, null=True, blank=True)
    file = models.FileField(_('فایل'), upload_to='products/attachments/')
    product = models.ForeignKey(Product, verbose_name=_("محصولات"), on_delete=models.CASCADE, related_name="product_attachment")
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = AttachmentManager()
    
    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name = _('فایل پیوست')
        verbose_name_plural = _('فایل های پیوست')

# ===== Product Rating Model ===== #
class ProductRating(models.Model):
    """
    مدل امتیازدهی به محصول (Star Rating).
    این مدل فقط مسئول ذخیره عدد امتیاز است و متن نظر را شامل نمی‌شود.
    """
    user = models.ForeignKey(
        "core.User", 
        on_delete=models.PROTECT, 
        related_name="product_ratings",
        verbose_name=_("کاربر")
    )
    product = models.ForeignKey(
        "core.Product", 
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("محصول")
    )
    score = models.PositiveSmallIntegerField(
        _("امتیاز"),
        default=5,
        validators=[
            MinValueValidator(1, message=_("امتیاز نمی‌تواند کمتر از ۱ باشد.")),
            MaxValueValidator(5, message=_("امتیاز نمی‌تواند بیشتر از ۵ باشد."))
        ],
        help_text=_("امتیاز بین ۱ تا ۵")
    )
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ ویرایش"), auto_now=True)
    
    objects = ProductRatingManager()

    class Meta:
        verbose_name = _("امتیاز محصول")
        verbose_name_plural = _("امتیازات محصولات")
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['product', 'score']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}: {self.score}"

    def clean(self):
        """
        اعتبارسنجی سطح مدل (Rich Model Logic).
        """
        if not (1 <= self.score <= 5):
            raise ValidationError(_("امتیاز باید بین ۱ تا ۵ باشد."))

    @property
    def is_positive(self):
        """آیا امتیاز مثبت تلقی می‌شود؟ (مثلاً ۴ و ۵)"""
        return self.score >= 4

class ProductCommentChoices(models.TextChoices):
    """
    مشخصات و مقادیر قابلیت‌های نظرات (Comment Choices).
    """
    PENDING = 'pending', _('در انتظار بررسی')
    APPROVED = 'approved', _('تایید شده')
    REJECTED = 'rejected', _('رد شده')

# ===== Product Comment Model ===== #
class ProductComment(models.Model):
    """
    مدل نظرات و پرسش/پاسخ محصول.
    قابلیت پاسخ‌دهی تو در تو (Nested Replies) برای ادمین را دارد.
    """

    user = models.ForeignKey(
        "core.User", 
        on_delete=models.PROTECT, 
        related_name="product_comments",
        verbose_name=_("کاربر")
    )
    product = models.ForeignKey(
        "core.Product", 
         on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("محصول")
    )
    # ===== پاسخ‌دهی تو در تو ===== #
    parent = models.ForeignKey(
        'self', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='replies',
        verbose_name=_("پاسخ به")
    )
    
    # ===== محتوای نظر ===== #
    name = models.CharField(_("نام نمایش داده شده"), max_length=150)
    email = models.EmailField(_("ایمیل"))
    message = models.TextField(_("متن نظر"))
    
    # ===== مدیریت وضعیت ===== #
    status = models.CharField(
        _("وضعیت"), 
        max_length=20, 
        choices=ProductCommentChoices.choices, 
        default=ProductCommentChoices.PENDING
    )
    
    # ===== اطلاعات اضافی ===== #
    admin_note = models.TextField(_("یادداشت ادمین"), blank=True, null=True, help_text=_("دلیل رد یا تایید برای داخلی"))
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ ویرایش"), auto_now=True)
    
    objects = ProductCommentManager()

    class Meta:
        verbose_name = _("نظر محصول")
        verbose_name_plural = _("نظرات محصولات")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} on {self.product.name}"

    def save(self, *args, **kwargs):
        """
        پر کردن خودکار نام و ایمیل اگر خالی باشند (Rich Behavior).
        """
        if not self.name and self.user:
            # ===== پیدا کردن نام و نام خانوادگی ===== #
            try:
                self.name = f"{self.user.customer_profile.first_name} {self.user.customer_profile.last_name}"
            except Exception:
                self.name = self.user.username
        
        if not self.email and self.user:
            self.email = self.user.email
            
        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        """آیا این یک پاسخ است؟"""
        return self.parent is not None

    @property
    def is_public(self):
        """آیا نظر قابل نمایش است؟"""
        return self.status == self.STATUS_APPROVED

    def approve(self):
        """تایید نظر (Domain Action)"""
        self.status = self.STATUS_APPROVED
        self.save(update_fields=['status', 'updated_at'])

    def reject(self, reason=""):
        """رد نظر"""
        self.status = self.STATUS_REJECTED
        self.admin_note = reason
        self.save(update_fields=['status', 'admin_note', 'updated_at'])
