import random
from slugify import slugify

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    def save(self, *args, **kwargs):
        """ ذخیره اسلاگ به صورت خودکار """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
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
