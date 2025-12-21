import random
from slugify import slugify
from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey

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
    is_active = models.BooleanField(_("فعال"), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def save(self, *args, **kwargs):
        """ ذخیره اسلاگ به صورت خودکار """
        if not self.slug:
            self.slug = slugify(self.name)
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
    
# ======== Product Model ======== #
class Product(models.Model):
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
    category = models.ForeignKey(
        'ProductCategory',
        verbose_name=_('دسته بندی'),
        on_delete=models.PROTECT,
        related_name='products',
    )
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True, null=True)
    has_price = models.BooleanField(_('دارای قیمت'), default=True)
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
            self.slug = slugify(self.name)
            
        if not self.code:
            year = timezone.now().year
            category_slug = self.category.slug if self.category else 'UNKNOWN'
            self.code = product_code_generator(category_slug, self.slug, year)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.code}"

# ======== Product Pricing & Config Logic ======== #
class ProductPricingConfig(models.Model):
    """
    تنظیمات پیشرفته محاسبه قیمت و قوانین سفارش.
    این مدل جلوی چاق شدن مدل Product را می‌گیرد.
    """
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE,
        related_name='pricing_config',
        verbose_name=_("محصول مرتبط")
    )
    
    # ===== تنظیمات تیراژ و ابعاد ===== #
    allow_custom_quantity = models.BooleanField(_("امکان تیراژ دلخواه"), default=False)
    min_quantity = models.PositiveIntegerField(_("حداقل تیراژ"), default=100)
    max_quantity = models.PositiveIntegerField(_("حداکثر تیراژ"), default=10000)
    
    accepts_custom_dimensions = models.BooleanField(_("پذیرش ابعاد دلخواه"), default=False)
    min_width = models.FloatField(_("حداقل عرض (cm)"), default=0)
    max_width = models.FloatField(_("حداکثر عرض (cm)"), default=0)
    
    # ===== تنظیمات مالی ===== #
    base_setup_price = models.DecimalField(
        _("هزینه ثابت اولیه (Setup)"), 
        max_digits=12, decimal_places=0, default=0,
        help_text=_("هزینه زینک، قالب یا تنظیم دستگاه که ربطی به تیراژ ندارد.")
    )
    
    # ===== تنظیمات خدمات طراحی ===== #
    design_service_available = models.BooleanField(_("ارائه خدمات طراحی"), default=True)
    design_fee = models.DecimalField(
        _("هزینه طراحی پایه"),
        max_digits=12, decimal_places=0, default=0,
        help_text=_("اگر کاربر فایل نداشت، این مبلغ اضافه می‌شود.")
    )
    
    class Meta:
        verbose_name = _("تنظیمات قیمت و سفارش")
        verbose_name_plural = _("تنظیمات قیمت و سفارش")

    def __str__(self):
        return f"Config for {self.product.name}"

# ======== Size ======== #
class Size(models.Model):
    """ مدل سایز با طول و عرض """
    user = models.ForeignKey("core.User", related_name='size_user', on_delete=models.PROTECT)
    name = models.CharField(_("نام"), max_length=150)
    width = models.FloatField(_("عرض"), default=0)
    height = models.FloatField(_("طول"), default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.name}({self.width} - {self.height})"
    
    class Meta:
        verbose_name = _("سایز")
        verbose_name_plural = _("سایزها")

# ====== Product Size Model ====== #
class ProductSize(models.Model):
    """ مدل واسط بین سایز و محصول"""
    user = models.ForeignKey("core.User", related_name='product_size', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product_size', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='size_product', on_delete=models.PROTECT)
    # ==== قیمت هر سایز ==== #
    price_impact = models.DecimalField(
        _("تأثیر بر قیمت"), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text=_("مبلغی که به قیمت پایه اضافه یا از آن کسر می‌شود (به تومان).")
    )
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.size.name}"

    class Meta:
        verbose_name = _('محصول سایز')
        verbose_name_plural = _('محصولات سایز')

# ====== Quantity Model ====== #
class Quantity(models.Model):
    """ مدل تیراژ """
    user = models.ForeignKey("core.User", related_name='quantity_user', on_delete=models.PROTECT)
    value = models.PositiveIntegerField(_('تیراژ'), unique=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return str(self.value)
    
    class Meta:
        verbose_name = _('تیراژ')
        verbose_name_plural = _('تیراژ ها')

# ====== Product Quantity Model ====== #
class ProductQuantity(models.Model):
    """ کلاس واسط بین مدل محصول و تیراژ """
    user = models.ForeignKey('core.User', related_name='product_quantity_user', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product_quantity', on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, related_name='quantity_product', on_delete=models.PROTECT)
    price = models.IntegerField(_('قیمت'), default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.price}: {self.quantity}"
    
    class Meta:
        verbose_name = _('تعداد')
        verbose_name_plural = _('تعداد ها')
        
# ====== Product Image Model ====== #
class ProductImage(models.Model):
    """ مدل عکس محصول """
    user = models.ForeignKey("core.User", related_name='user_product_image', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='product_image', on_delete=models.CASCADE)
    image = models.ImageField(_('تصویر'), upload_to='products/')
    order = models.IntegerField(_('ترتیب'), default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name = _('تصویر')
        verbose_name_plural = _('تصاویر')

# ======= Attachement Model ======= #
class Attachment(models.Model):
    """ مدل فایل های پیوست """
    user = models.ForeignKey("core.User", related_name='user_attachments', on_delete=models.PROTECT)
    name = models.CharField(_('نام'), max_length=150)
    file = models.FileField(_('فایل'), upload_to='products/attachments/')
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return str(self.pk)
    
    class Meta:
        verbose_name = _('فایل محصول')
        verbose_name_plural = _('فایل های محصولات')


# ======= Product Attachment Model ======= #
class ProductAttachment(models.Model):
    """ مدل واسط بین محصول و فایل """
    user = models.ForeignKey("core.User", related_name='product_attachment_user', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_attachment_product', on_delete=models.PROTECT)
    attachment = models.ForeignKey(Attachment, related_name='product_attachment_file', on_delete=models.PROTECT)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.attachment.name}"

# ======= Option Input Type Model ======= #
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
    BOOLEAN = 'boolean', _('سوییچ / تیک (Boolean)')

# ====== Option Pricing Strategy Model ====== #
class OptionPricingStrategy(models.TextChoices):
    """
    استراتژی محاسبه قیمت.
    مشخص می‌کند عدد قیمت (Rate) در چه چیزی ضرب شود.
    """
    FIXED = 'fixed', _('مبلغ ثابت (Fixed Amount)')
    PERCENTAGE = 'percentage', _('درصدی از قیمت پایه (Percentage)')
    
    # ===== فرمول‌های وابسته به ابعاد ===== #
    PER_SQM = 'per_sqm', _('براساس متر مربع (Area * Rate)')
    PER_METER_PERIMETER = 'per_perimeter', _('براساس متر محیط (Perimeter * Rate)')
    
    # ===== فرمول‌های وابسته به ورودی ===== #
    PER_UNIT_INPUT = 'per_unit', _('براساس عدد ورودی کاربر (Input * Rate)')
    
# ====== Option Model ====== #
class Option(models.Model):
    """
    تعریف نوع ویژگی در سطح کل سیستم.
    (Master Data)
    """
    name = models.CharField(
        _("نام سیستمی"), 
        max_length=150, 
        unique=True, 
        help_text=_("شناسه یکتا برای کدنویسی (مثال: paper_type)")
    )
    label = models.CharField(_("عنوان نمایشی"), max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.get_input_type_display()})"
    
    class Meta:
        verbose_name = _("بانک ویژگی")
        verbose_name_plural = _("بانک ویژگی‌ها")

# ====== Option Value Model ====== #
class OptionValue(models.Model):
    """ 
    بانک مقادیر پیش‌فرض (Template Library).
    برای جلوگیری از تایپ تکراری توسط ادمین.
    """
    option = models.ForeignKey(Option, related_name='global_values', on_delete=models.PROTECT)
    label = models.CharField(_("عنوان مقدار"), max_length=150, null=True, blank=True)
    value = models.CharField(_("کد سیستمی"), max_length=150, null=True, blank=True)
    input_type = models.CharField(
        _("نوع ویژگی"),
        max_length=25,
        choices=OptionInputType.choices,
        default=OptionInputType.TEXT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.option.label}: {self.label}"
    
    class Meta:
        verbose_name = _("الگوی مقدار ویژگی")
        verbose_name_plural = _("الگوهای مقادیر ویژگی")
        
# ====== Product Option Model ====== #
class ProductOption(models.Model):
    """
    اتصال ویژگی به محصول.
    اینجا تعیین می‌کنیم ویژگی چه رفتاری در این محصول خاص دارد.
    """
    product = models.ForeignKey(Product, related_name='options', on_delete=models.CASCADE, null=True)
    option = models.ForeignKey(Option, related_name='product_configs', on_delete=models.PROTECT)
    
    # ===== تنظیمات نمایش (UI) ===== #
    is_required = models.BooleanField(_("اجباری؟"), default=False)
    order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)

    class Meta:
        verbose_name = _("پیکربندی ویژگی محصول")
        verbose_name_plural = _("پیکربندی ویژگی‌های محصولات")
        unique_together = ('product', 'option')
        ordering = ['order']

    def clean(self):
        """ Validation Logic """
        if not self.has_pricing and self.base_price != 0:
            raise ValidationError(_("وقتی ویژگی فاقد قیمت است، هزینه سربار باید ۰ باشد."))

    def __str__(self):
        status = "($)" if self.has_pricing else "(Free)"
        return f"{self.product.name} | {self.option.label} {status}"

# ====== PRODUCT OPTION VALUE ====== #
class ProductOptionValue(models.Model):
    """
    مقادیر قابل انتخاب (Choices).
    شامل نرخ‌ها (Rates) و قوانین تیراژ.
    """
    product_option = models.ForeignKey(
        ProductOption, 
        related_name='choices', 
        on_delete=models.PROTECT
    )
    
    # ===== ارجاع به بانک (Snapshot Pattern) ===== #
    global_source = models.ForeignKey(
        OptionValue, 
        null=True, blank=True, 
        on_delete=models.PROTECT,
        verbose_name=_("کپی از الگوی گلوبال")
    )

    # ===== مقادیر واقعی (Local Override) ===== #
    label = models.CharField(_("عنوان نمایشی"), max_length=150, blank=True)
    value = models.CharField(_("مقدار سیستمی"), max_length=150, blank=True)
    
    # ===== کنترل مالی دقیق (Granular Control) ===== #
    has_pricing = models.BooleanField(
        _("شامل هزینه می‌شود؟"),
        default=True,
        help_text=_("سطح ۲ کنترل: اگر خاموش باشد، قیمت این گزینه صفر لحاظ می‌شود.")
    )

    price_impact = models.DecimalField(
        _("مبلغ / نرخ واحد"), 
        max_digits=14, decimal_places=0, default=Decimal('0'),
        help_text=_("اگر استراتژی ثابت است: کل مبلغ. اگر متری/تعدادی است: نرخ واحد.")
    )
    
    is_default = models.BooleanField(_("پیش‌فرض"), default=False)
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    class Meta:
        verbose_name = _("گزینه انتخابی نهایی")
        verbose_name_plural = _("گزینه‌های انتخابی نهایی")
        ordering = ['order']

    def clean(self):
        """ 
        Strict Data Integrity Rules 
        """
        # ===== اگر قیمت ندارد، قوانین تیراژ باید غیرفعال باشد. ===== #
        if not self.product_option.has_pricing and self.has_pricing:
            raise ValidationError({
                'has_pricing': _("ویژگی اصلی (گروه) غیرمالی است. نمی‌توانید برای این گزینه محاسبه قیمت را فعال کنید.")
            })

        # ===== اگر قیمت ندارد، مبلغ باید صرفاً ۰ باشد. ===== #
        if not self.has_pricing and self.price_impact != 0:
             raise ValidationError({
                'price_impact': _("وقتی گزینه فاقد قیمت است، مبلغ باید ۰ باشد.")
            })
            
        # ===== اگر لیبل دستی وارد نشده باشد، از الگو انتخاب کنید. ===== 
        if not self.label and not self.global_source:
             raise ValidationError(_("عنوان گزینه الزامی است (یا دستی وارد کنید یا از الگو انتخاب کنید)."))

    def save(self, *args, **kwargs):
        # کپی خودکار از تمپلت اگر لیبل دستی وارد نشده باشد
        if self.global_source and not self.label:
            self.label = self.global_source.label
            self.value = self.global_source.value
            
        # ===== اگر قیمت ندارد، قیمت باید صرفاً ۰ باشد. ===== #
        if not self.product_option.has_pricing:
            self.has_pricing = False
        
        if not self.has_pricing:
            self.price_impact = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        price_str = f"+{self.price_impact:,}" if self.has_pricing else "Free"
        step_str = f"/{self.quantity_step}" if self.quantity_step > 1 else ""
        return f"{self.label} ({price_str}{step_str})"

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

    class Meta:
        verbose_name = _("امتیاز محصول")
        verbose_name_plural = _("امتیازات محصولات")
        # قانون بیزنس: هر کاربر به هر محصول فقط یک بار امتیاز می‌دهد
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['product', 'score']), # برای کوئری‌های فیلتر و میانگین‌گیری سریع
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
