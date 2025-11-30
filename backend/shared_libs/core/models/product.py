import random
from slugify import slugify

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from mptt.models import MPTTModel, TreeForeignKey

# ======== Product Code Generator ======== #
def product_code_generator(category_slug, year):
    """
    این تابع برای تولید کد یکتا برای محصولات است
    """
    
    random_num = random.randint(1000, 9999)
    code = f"{random_num}{category_slug.upper()}{year}"
    return code

# ======== Product Category Model ======== #
class ProductCategory(MPTTModel):
    """
    مدل دسته بندی محصولات
    """

    user = models.ForeignKey("core.User", related_name='product_category', on_delete=models.CASCADE)
    name = models.CharField(_("نام"), max_length=150)
    slug = models.SlugField(_("اسلاگ"), unique=True, blank=True, null=True)
    parent = TreeForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)
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
        on_delete=models.CASCADE,
    )
    name = models.CharField(_('نام'), max_length=150)
    category = models.ForeignKey(
        'ProductCategory',
        verbose_name=_('دسته بندی'),
        on_delete=models.PROTECT,
        related_name='products',
    )
    slug = models.SlugField(_('اسلاگ'), unique=True, blank=True, null=True)
    price = models.PositiveIntegerField(_('قیمت'), default=0)
    accepts_custom_dimensions = models.BooleanField(_('پذیرش اندازه های سطح'), default=False)
    # ====== قیمت گذاری براساس واحد سطح ====== #
    price_per_square_unit = models.DecimalField(
        _("قیمت بر واحد سطح (مثلا سانتی‌متر مربع)"), 
        max_digits=10, 
        decimal_places=2, 
        null=True, blank=True,
        help_text=_("اگر این محصول ابعاد دلخواه دارد، قیمت هر واحد سطح را وارد کنید. در غیر این صورت خالی بگذارید.")
    )
    # ===== فیلد برای تغییر قیمت محصول ===== #
    price_modifier_percent = models.DecimalField(
        _("درصد تعدیل قیمت"), 
        max_digits=5, 
        decimal_places=2, 
        default=0.0, 
        help_text=_("یک عدد برای تغییر کلی قیمت. مثال: 15.0 برای افزایش 15 درصدی یا -10.0 برای کاهش 10 درصدی.")
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
    
    def save(self, *args, **kwargs):
        """ ذخیره اسلاگ محصول به صورت خودکار """
        if not self.slug:
            self.slug = slugify(self.name)
            
        if not self.code:
            year = timezone.now().year
            category_slug = self.category.slug if self.category else 'UNKNOWN'
            self.code = product_code_generator(category_slug, year)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.code}"

# ======== Size ======== #
class Size(models.Model):
    """ مدل سایز با طول و عرض """
    user = models.ForeignKey("core.User", related_name='size_user', on_delete=models.CASCADE)
    name = models.CharField(_("نام"), max_length=150)
    width = models.FloatField(_("عرض"), default=0.0)
    height = models.FloatField(_("طول"), default=0.0)
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
    user = models.ForeignKey("core.User", related_name='product_size', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_size', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='size_product', on_delete=models.CASCADE)
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

# ====== Material Model ====== # 
class Material(models.Model):
    user = models.ForeignKey("core.User", related_name='materials', on_delete=models.CASCADE)
    name = models.CharField(_('نام'), max_length=150)
    description = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('جنس')
        verbose_name_plural = _('جنس ها')
        
# ====== Product Material Model ====== #
class ProductMaterial(models.Model):
    """ کلاس واسط بین مدل جنس و محصول """
    user = models.ForeignKey("core.User", related_name='product_material', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_material', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, related_name='material_product', on_delete=models.CASCADE)
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
        return self.product.name
    
    class Meta:
        verbose_name = _('واسط محصول و جنس')
        verbose_name_plural = _('واسط های محصول و جنس')

# ====== Quantity Model ====== #
class Quantity(models.Model):
    """ مدل تیراژ """
    user = models.ForeignKey("core.User", related_name='quantity_user', on_delete=models.CASCADE)
    value = models.PositiveIntegerField(_('تیراژ'))
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
    user = models.ForeignKey('core.User', related_name='product_quantity_user', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_quantity', on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, related_name='quantity_product', on_delete=models.CASCADE)
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
    user = models.ForeignKey("core.User", related_name='user_product_image', on_delete=models.CASCADE)
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
    user = models.ForeignKey("core.User", related_name='user_attachments', on_delete=models.CASCADE)
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
    product = models.ForeignKey(Product, related_name='product_attachment_product', on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, related_name='product_attachment_file', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.attachment.name}"

# ====== Option Model ====== #
class Option(models.Model):
    """ مدل ویژگی های منحصر به فرد محصول """
    user = models.ForeignKey("core.User", related_name='option_user', on_delete=models.CASCADE)
    name = models.CharField(_('نام'), max_length=150)
    code = models.CharField(_('کد'), max_length=150)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def save(self, *args, **kwargs):
        """ ذخیره کد به صورت خودکار """
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _('ویژگی')
        verbose_name_plural = _('ویژگی ها')

# ====== Option Value ====== #
class OptionValue(models.Model):
    """
    مقدار ویژگی ها 
    این قسمت به این صورت کار میکنه که یک ویژگی تعریف شده انتخاب میشه
    بعد از انتخاب، حالا میتونیم که چندین مقدار مختلف رو به یک ویژگی
    ربط بدیم و اعمال کنیم. این اولین قدم برای ویژگی های منحصر به فرد
    محصولات هست.
    """
    user = models.ForeignKey("core.User", related_name='option_value_user', on_delete=models.CASCADE)
    option = models.ForeignKey(Option, related_name='option_value_option', on_delete=models.CASCADE)
    value = models.CharField(_('مقدار'), max_length=150)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def __str__(self):
        return self.option.name + ': ' + self.value
    
    class Meta:
        verbose_name = _('مقدار ویژگی')
        verbose_name_plural = _('مقدار ویژگی ها')
        
# ====== Product Option Model ====== #
class ProductOption(models.Model):
    """
    مدل واسط بین محصول و ویژگی ها 
    در این مدل، ما یک ویژگی رو برای محصول انتخاب میکنیم و سپس، مقادیری که
    به اون ویژگی مربوط هست، انتخاب میکنیم(میتونه چندین مقدار باشه). این کار
    باعث دقیق تر شدن گزارشات و همچنین مشخص بودن هر ویژگی منحصر به فرد برای
    محصول می باشد.
    """
    user = models.ForeignKey("core.User", related_name='product_option_user', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_option_product', on_delete=models.CASCADE)
    option = models.ForeignKey(Option, related_name='product_option_option', on_delete=models.CASCADE)
    option_value = models.ForeignKey(OptionValue, related_name='product_option_option_value', on_delete=models.CASCADE)
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
        return f"{self.product.name} - {self.option.name} - {self.option_value.value}"
    
    class Meta:
        verbose_name = _('ویژگی محصول')
        verbose_name_plural = _('ویژگی های محصولات')

# ======= File Upload Spec Model ======= #
class FileUploadSpec(models.Model):
    """
    تعریف یک نوع یا اسلات آپلود فایل.
    مانند 'طرح رو'، 'طرح پشت'، 'فایل خط برش'.
    این مدل از تکرار داده جلوگیری می‌کند.
    """
    name = models.CharField(
        _("نام مشخصات"),
        max_length=100,
        unique=True,
        help_text=_("مثال: طرح رو، طرح پشت، فایل UV")
    )
    description = models.TextField(_("توضیحات"), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("مشخصات آپلود فایل")
        verbose_name_plural = _("انواع مشخصات آپلود فایل")

# ======== Product File Upload Requirement Model ======== #
class ProductFileUploadRequirement(models.Model):
    """
    این مدل تعیین می‌کند که یک محصول خاص به چه نوع فایل‌هایی نیاز دارد.
    این همان مدل واسطی است که شما به درستی به آن اشاره کردید.
    """
    product = models.ForeignKey(
        Product,
        verbose_name=_("محصول"),
        on_delete=models.CASCADE,
        related_name="file_upload_requirements"
    )
    spec = models.ForeignKey(
        FileUploadSpec,
        verbose_name=_("مشخصات"),
        on_delete=models.PROTECT,
        related_name="product_requirements"
    )
    is_required = models.BooleanField(_("الزامی بودن"), default=True)
    sort_order = models.PositiveIntegerField(_("ترتیب نمایش"), default=0)

    def __str__(self):
        return f"{self.product.name} -> {self.spec.name}"

    class Meta:
        verbose_name = _("نیازمندی آپلود فایل محصول")
        verbose_name_plural = _("نیازمندی‌های آپلود فایل محصولات")
        ordering = ['sort_order']
        unique_together = ('product', 'spec')

# ===== Product Rating Model ===== #
class ProductRating(models.Model):
    """
    مدل امتیازدهی به محصول (Star Rating).
    این مدل فقط مسئول ذخیره عدد امتیاز است و متن نظر را شامل نمی‌شود.
    """
    user = models.ForeignKey(
        "core.User", 
        on_delete=models.CASCADE, 
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
        on_delete=models.CASCADE, 
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
        on_delete=models.CASCADE, 
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
