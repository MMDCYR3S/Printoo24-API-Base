import os
from random import randint

from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.product.models import Product

from .managers import (
    OrderManager,
    OrderItemManager,
    OrderItemFileManager,
    OrderStatusManager,
    OrderStatusGroupManager,
)

# ===== Order Status Group ===== #
class OrderStatusGroup(models.Model):
    """
    گروه‌بندی وضعیت‌ها به صورت داینامیک.
    مثال:
    - عنوان: واحد طراحی / کد: design
    - عنوان: واحد چاپ / کد: production
    
    نکته: با ایجاد هر رکورد در اینجا، سیستم اتوماتیک یک AccessScope می‌سازد.
    """
    name = models.CharField(_('عنوان گروه'), max_length=100)
    code = models.SlugField(_('کد سیستمی'), max_length=50, unique=True, help_text="شناسه یکتا برای لاجیک سیستم (مثلا: design)")
    description = models.TextField(blank=True)
    
    is_system = models.BooleanField(
        _('سیستمی'), 
        default=False,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderStatusGroupManager()

    class Meta:
        verbose_name = _('گروه وضعیت')
        verbose_name_plural = _('گروه‌های وضعیت')

    def __str__(self):
        return f"{self.name} ({self.code})"

# ============================= #
# ===== Order Status Model ===== #
# ============================= #
class OrderStatus(models.Model):
    """ 
    مدل وضعیت‌های سفارش.
    نکته تحلیلی: فیلد internal_code برای لاجیک‌های کدنویسی حیاتی است 
    تا وابسته به تغییر متن فارسی توسط ادمین نباشیم.
    """
    
    # ===== انواع ماهیت وضعیت ===== #
    TYPE_CHOICES = [
        ('initial', _('آغازین (Start)')),
        ('progress', _('در جریان (Progress)')),
        ('approve', _('تاییدیه (Approve)')),
        ('reject', _('رد شده (Reject)')),
        ('cancel', _('لغو شده (Cancel)')),
    ]
    
    name = models.CharField(_('عنوان نمایشی'), max_length=150)
    internal_code = models.SlugField(_('کد سیستمی'), max_length=150, unique=True, null=True, blank=True)

    is_system = models.BooleanField(
        _('سیستمی'), 
        default=False, 
        editable=False
    )

    status_type = models.CharField(
        _('نوع وضعیت'), 
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='progress'
    )
    sort_order = models.PositiveIntegerField(
        _('ترتیب نمایش'), 
        default=0, 
        help_text=_("ترتیب قرارگیری در لیست (کم به زیاد).")
    )
    
    group = models.ForeignKey(OrderStatusGroup, related_name='order_status', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به‌روزرسانی'), auto_now=True)
    
    objects = OrderStatusManager()

    class Meta:
        verbose_name = _('وضعیت سفارش')
        verbose_name_plural = _('وضعیت‌های سفارش')

    def __str__(self):
        return f"{self.name} ({self.internal_code})"
    
    def clean(self):
        """ اعتبارسنجی‌های خاص """
        if self.status_type == 'initial':
            if self.group.order_status.filter(status_type='initial').count() == 1:
                # ===== بررسی اینکه آیا داریم خود آن یک وضعیت اولیه رو ویرایش میکنیم یا نه ===== #
                if not self.pk or (self.pk and self.group.order_status.filter(status_type='initial').first().pk != self.pk):
                    raise ValueError(_("این گروه قبلا یک وضعیت آغازین داشته است."))
            pass
        
    def save(self, *args, **kwargs):
        """
        تولید و فرمت‌دهی خودکار کد سیستمی.
        """
        if self.group and self.internal_code:
            # ===== ورودی های اولیه ===== #
            raw_input = self.internal_code.upper().strip()
            type_suffix = self.status_type.upper()
            group_suffix = self.group.code.upper()
            
            current_suffix = f"_{type_suffix}_{group_suffix}"
            
            if not raw_input.endswith(current_suffix):
                parts = raw_input.split('_')
                if len(parts) >= 3 and parts[-1] == group_suffix and parts[-2] == type_suffix:
                    pass
                else:
                    if raw_input.endswith(f"_{group_suffix}"):
                        raw_input = raw_input.rsplit(f"_{group_suffix}", 1)[0]
                        
                    for t_code, _label in self.TYPE_CHOICES:
                        t_upper = t_code.upper()
                        if raw_input.endswith(f"_{t_upper}"):
                            raw_input = raw_input.rsplit(f"_{t_upper}", 1)[0]
                            break
                    self.internal_code = f"{raw_input}_{type_suffix}_{group_suffix}"
                    
        super().save(*args, **kwargs)
                
# ======================= #
# ===== Order Model ===== #
# ======================= #
class Order(models.Model):
    """ مدل سفارش  - این مدل، نقطه ثقل سیستم هستش. """
    ORDER_TYPE = [
        ("1", _("سفارش معمولی")),
        ("2", _("سفارش اختصاصی"))
    ]
    
    user = models.ForeignKey(
        "core.User",
        verbose_name=_("مشتری"),
        on_delete=models.PROTECT,
        null=True, blank=True,
        help_text=_("در صورت نال بودن، سفارش به عنوان مهمان ثبت شده است.")
    )
    order_code = models.CharField(_("کد پیگیری"), max_length=50, unique=True, db_index=True, null=True, blank=True)
    # ===== اطلاعات مشتری ===== #
    recipient_name = models.CharField(_("نام گیرنده"), max_length=255, null=True, blank=True, help_text="نام و نام خانوادگی در لحظه ثبت سفارش")
    recipient_phone = models.CharField(_("شماره تماس گیرنده"), max_length=11, null=True, blank=True)
    company_name = models.CharField(_("نام شرکت"), max_length=150, blank=True, null=True)
    # ===== آدرس به صورت متنی ===== #
    full_address = models.TextField(
        _("آدرس کامل پستی"), null=True, blank=True,
        help_text=_("شامل: استان، شهر، کدپستی و آدرس دقیق")
    )
    # ===== نوع و وضعیت سفارش ===== #
    address = models.ForeignKey(
        "core.Address",
        verbose_name=_("آدرس"),
        on_delete=models.PROTECT,
        related_name="address_order",
        blank=True,
        null=True
    )
    type = models.CharField(_("نوع سفارش"), max_length=150, choices=ORDER_TYPE, default="2")
    current_status = models.ForeignKey(
        OrderStatus,
        verbose_name=_("وضعیت فعلی"),
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True
    )
    total_price = models.DecimalField(_("مبلغ کل سفارش"), max_digits=18, decimal_places=0,default=0)
    base_products_price = models.DecimalField(_("مبلغ پایه اقلام"), max_digits=15, decimal_places=0, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
        # verbose_name = _('سفارش')
        # verbose_name_plural = _('سفارشات')

    def __str__(self):
        return f"{self.order_code} | {self.user}"
    
    # ===== Properties ===== #
    @property
    def items_count(self):
        """ تعداد کل آیتم‌های داخل سفارش """
        return self.items.count()

    @property
    def is_locked(self):
        """ 
        آیا سفارش قفل شده است؟ 
        (مثلا اگر در مرحله چاپ باشد نباید بتوان آیتم اضافه کرد)
        """
        locked_statuses = ['PRODUCTION', 'PRINTING', 'SHIPPED', 'DELIVERED']
        return self.current_status.internal_code in locked_statuses
    
# =========================== #
# ===== Order Item Model ===== #
# =========================== #
class OrderItem(models.Model):
    """ 
    آیتم‌های سفارش.
    تحلیل: هر آیتم ویژگی‌های فنی (Features) خودش را دارد که در JSON ذخیره می‌شود.
    """
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار بررسی')),
        ('approved', _('تایید شده')),
        ('rejected', _('رد شده (نیازمند اصلاح)')),
        ('cancelled', _('لغو شده')),
    ]
        
    order = models.ForeignKey(Order, related_name='order_item_order', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product,
        related_name='order_item_product',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    name = models.CharField(_('نام'), max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_("قیمت"), max_digits=12, decimal_places=2)
    status = models.CharField(
        _("وضعیت فایل"), max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    items = models.JSONField(_("آیتم های اضافی"), blank=True, null=True)
    description = models.TextField(_("توضیحات کلی مشتری"), blank=True, null=True)
    admin_note = models.TextField(_("یادداشت تولید"), blank=True, help_text="مخصوص اپراتور چاپ")
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = OrderItemManager()
    
    class Meta:
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('اقلام سفارش')

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    # ===== Properties ===== #
    @property
    def total_price(self):
        """ محاسبه قیمت کل این خط (تعداد * قیمت واحد) """
        return self.quantity * self.unit_price

    @property
    def feature_summary(self):
        """ خروجی متنی خلاصه از ویژگی‌ها برای نمایش در لیست """
        if not self.features:
            return ""
        return ", ".join([f"{k}: {v}" for k, v in self.features.items()])

# =============================== #
# ===== Order Item File Model ===== #
# =============================== #
class OrderItemFile(models.Model):
    """ 
    مدل فایل‌های طراحی با قابلیت ورژن‌بندی.
    تحلیل: فایل‌ها پاک نمی‌شوند، بلکه ورژن جدید می‌خورند تا تاریخچه حفظ شود.
    """
    
    order_item = models.ForeignKey(
        OrderItem, 
        related_name='files', 
        on_delete=models.CASCADE,
        verbose_name=_("آیتم سفارش")
    )
    file = models.FileField(_('فایل نهایی'), upload_to='orders/designs/%Y/%m/%d/')
    version = models.PositiveIntegerField(_('نسخه فایل'), default=1)
    is_latest = models.BooleanField(_('آخرین نسخه است؟'), default=True)
    admin_feedback = models.TextField(_("دلیل رد شدن / توضیحات QC"), blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    objects = OrderItemFileManager()

    class Meta:
        verbose_name = _('فایل طراحی')
        verbose_name_plural = _('فایل‌های طراحی')
        ordering = ['-version']

    def __str__(self):
        return f"File v{self.version} - {self.get_status_display()}"

    # ===== Properties ===== #
    @property
    def filename(self):
        """ نام خالص فایل بدون مسیر """
        number = randint(0000, 9999)
        return os.path.basename(f"file_v{self.version}_r{self.requirement.spec.name}_{number}")

    @property
    def is_rejected(self):
        return self.status == 'rejected'
