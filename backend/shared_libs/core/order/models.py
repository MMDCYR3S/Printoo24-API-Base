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
    OrderPrintReportManager, 
    OrderPrintItemManager, 
    OrderPrintAttachmentManager,
    OrderScheduleManager,
    OrderStatusManager,
    OrderStatusGroupManager,
    ShipmentManager, 
    PackageManager,
    OrderCostSheetManager, 
    OrderCostReportManager, 
    OrderCostItemManager,
    OrderCostAttachmentManager,
    OrderCostCategoryManager
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
        on_delete=models.PROTECT
    )
    order_code = models.CharField(_("کد پیگیری"), max_length=50, unique=True, db_index=True, null=True, blank=True)
    type = models.CharField(_("نوع سفارش"), max_length=150, choices=ORDER_TYPE, default="2")
    current_status = models.ForeignKey(
        OrderStatus,
        verbose_name=_("وضعیت فعلی"),
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True
    )
    address = models.ForeignKey(
        "core.Address",
        verbose_name=_("آدرس"),
        on_delete=models.PROTECT,
        related_name="address_order",
        blank=True,
        null=True
    )
    total_price = models.DecimalField(_("مبلغ کل سفارش"), max_digits=18, decimal_places=0,default=0)
    base_products_price = models.DecimalField(_("مبلغ پایه اقلام"), max_digits=15, decimal_places=0, default=0)
    description = models.TextField(_("توضیحات کلی مشتری"), blank=True, null=True)
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
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_("قیمت"), max_digits=12, decimal_places=2)
    status = models.CharField(
        _("وضعیت فایل"), max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    items = models.JSONField(_("آیتم های اضافی"), blank=True, null=True)
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

# ========================================================= #
# ========== مدلاسیون مربوط به هزینه های سفارش ========== #
# ========================================================= #
class OrderCostCategory(models.Model):
    """
    دسته‌بندی هزینه‌ها برای گزارش‌گیری دقیق.
    مثال: "مواد اولیه"، "خدمات چاپ"، "برون‌سپاری"، "حمل و نقل"، "سربار"
    """
    COST_TYPE = [
        ('design', _('طراحی')),
        ('print', _('چاپ')),
        ('material', _('مواد اولیه')),
        ('transport', _('حمل و نقل')),
        ('packing', _('بسته‌بندی')),
        ('storage', _('برون‌سپاری')),
        ('other', _('سایر')),
    ]
    
    title = models.CharField(_("عنوان دسته"), max_length=100)
    slug = models.SlugField(_("کد سیستمی"), unique=True)
    cost_type = models.CharField(_("نوع هزینه"), max_length=20, choices=COST_TYPE, default='other')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    objects = OrderCostCategoryManager()
    
    class Meta:
        verbose_name = _("دسته هزینه")
        verbose_name_plural = _("دسته‌های هزینه")

    def __str__(self):
        return self.title

# ========== Order Cost Sheet ========== #
class OrderCostSheet(models.Model):
    """
    سند کل بهای تمام شده سفارش (Internal Invoice).
    این مدل هیچ دیتای توصیفی ندارد، فقط اعداد نهایی را برای گزارش‌گیری مالی نگه می‌دارد.
    این رکورد باید همزمان با ایجاد سفارش (یا در اولین مرحله مالی) ساخته شود.
    """
    order = models.OneToOneField(
        'core.Order', 
        on_delete=models.CASCADE, 
        related_name='cost_sheet',
        verbose_name=_("سفارش مرتبط")
    )
    
    # ===== وضعیت کلی سند ===== #
    is_locked = models.BooleanField(
        _("قفل شده؟"), 
        default=False, 
        help_text="اگر تیک بخورد، هیچ گزارشی دیگر قابل اضافه شدن نیست (پایان سال مالی یا تسویه نهایی)."
    )
    
    # ===== تجمیع هزینه‌ها (Auto Calculated) ===== #
    total_material_cost = models.DecimalField(_("جمع هزینه مواد"), max_digits=18, decimal_places=0, default=0)
    total_service_cost = models.DecimalField(_("جمع هزینه خدمات/چاپ"), max_digits=18, decimal_places=0, default=0)
    total_shipping_cost = models.DecimalField(_("جمع هزینه ارسال"), max_digits=18, decimal_places=0, default=0)
    total_overhead_cost = models.DecimalField(_("جمع سربار/سایر"), max_digits=18, decimal_places=0, default=0)
    
    # ===== اعداد نهایی سود و زیان ===== #
    final_total_cost = models.DecimalField(_("بهای تمام شده کل"), max_digits=18, decimal_places=0, default=0)
    
    revenue_amount = models.DecimalField(_("مبلغ فروش (فاکتور)"), max_digits=18, decimal_places=0, default=0)
    net_profit = models.DecimalField(_("سود/زیان خالص"), max_digits=18, decimal_places=0, default=0)
    profit_margin_percent = models.FloatField(_("حاشیه سود (%)"), default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderCostSheetManager()

    class Meta:
        verbose_name = _("سند بهای تمام شده")
        verbose_name_plural = _("اسناد بهای تمام شده")

    def __str__(self):
        return f"Sheet for {self.order.order_code}"

    def recalculate_totals(self):
        self.save()

# ===== Order Cost Report ===== #
class OrderCostReport(models.Model):
    """
    گزارش هزینه ارسالی از سمت دپارتمان‌ها.
    این موجودیت توسط اپراتورها پر می‌شود و به تایید مدیر مالی می‌رسد.
    """
    
    DEPARTMENT_CHOICES = [
        ('design', _('واحد طراحی')),
        ('production', _('واحد تولید/چاپ')),
        ('warehouse', _('انبار')),
        ('logistics', _('لجستیک و ارسال')),
        ('outsourcing', _('برون‌سپاری')),
        ('management', _('مدیریت (سربار)')),
    ]

    sheet = models.ForeignKey(
        OrderCostSheet, 
        on_delete=models.CASCADE, 
        related_name='reports',
        verbose_name=_("سند مادر")
    )
    
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name=_("ارسال کننده گزارش")
    )
    
    title = models.CharField(_("عنوان گزارش"), max_length=200, help_text="مثلا: هزینه کاغذ مصرفی بخش افست")
    department = models.CharField(_("دپارتمان"), max_length=20, choices=DEPARTMENT_CHOICES)

    is_approved = models.BooleanField(_("تایید شده"), default=False)
    
    description = models.TextField(_("توضیحات تکمیلی"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderCostReportManager()

    class Meta:
        verbose_name = _('گزارش هزینه داخلی')
        verbose_name_plural = _('گزارشات هزینه داخلی')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

# ===== Order Cost Item Model ===== #
class OrderCostItem(models.Model):
    """
    اقلام ریز هزینه که زیرمجموعه یک گزارش هستند.
    مثال: "هزینه اول: کاغذ - 12000"
    """
    report = models.ForeignKey(
        OrderCostReport,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_("گزارش مرتبط"),
        blank=True,
        null=True
    )
    catalog_item = models.ForeignKey(
        OrderCostCategory, 
        on_delete=models.PROTECT,
        verbose_name=_("شرح هزینه"),
        null=True, blank=True
    )
    custom_title = models.CharField(_("عنوان (متفرقه)"), max_length=150, blank=True, null=True)
    amount = models.DecimalField(_("مبلغ"), max_digits=18, decimal_places=0)
    description = models.CharField(_("توضیحات تکمیلی"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    objects = OrderCostItemManager()

    class Meta:
        verbose_name = _('قلم هزینه')
        verbose_name_plural = _('اقلام هزینه')

    @property
    def final_title(self):
        """ برای نمایش در فاکتور یا گزارش """
        if self.catalog_item:
            return self.catalog_item.title
        return self.custom_title

    def __str__(self):
        return f"{self.custom_title}: {self.amount}"
    
class OrderCostAttachment(models.Model):
    """
    جدول پیوست‌های گزارش هزینه.
    جایگزین فیلد تکی 'attachment' در مدل OrderCostSheet می‌شود (یا در کنار آن).
    """
    report = models.ForeignKey(
        OrderCostReport, 
        related_name='attachments', 
        on_delete=models.CASCADE,
        verbose_name=_("گزارش هزینه")
    )
    file = models.FileField(_("فایل ضمیمه"), upload_to='financial/costs/attachments/%Y/%m/')
    title = models.CharField(_("عنوان فایل"), max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderCostAttachmentManager()

    class Meta:
        verbose_name = _('پیوست هزینه')
        verbose_name_plural = _('پیوست‌های هزینه')

# ==========================================
# ========== Print Material Models =========
# ==========================================

class OrderPrintReport(models.Model):
    """
    هدر گزارش مصرف متریال چاپ.
    مثلا: "مصرف کاغذ و زینک برای سفارش شماره ۱۰۰"
    """
    order = models.ForeignKey(
        'Order', 
        related_name='print_reports', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مرتبط")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name=_("ثبت کننده (اپراتور)")
    )
    title = models.CharField(_("عنوان گزارش"), max_length=200)
    description = models.TextField(_("توضیحات فنی"), blank=True, null=True)
    # ===== زمان مصرف ===== #
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderPrintReportManager()

    class Meta:
        verbose_name = _('گزارش مصرف چاپ')
        verbose_name_plural = _('گزارشات مصرف چاپ')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.order.order_code}"


class OrderPrintItem(models.Model):
    """
    اقلام مصرفی چاپ (به صورت استاتیک).
    """

    report = models.ForeignKey(
        OrderPrintReport, 
        related_name='items', 
        on_delete=models.CASCADE,
        verbose_name=_("گزارش مرتبط")
    )
    
    # ===== نوع مواد اولیه ===== #
    material_type = models.ForeignKey(
        OrderCostCategory, 
        related_name='print_items', 
        on_delete=models.PROTECT,
        verbose_name=_("نوع مواد اولیه")
    )
    custom_title = models.CharField(_("عنوان"), max_length=255, blank=True, null=True)
    price = models.DecimalField(_("قیمت"), max_digits=12, decimal_places=2)
    description = models.CharField(_("توضیحات"), max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    objects = OrderPrintItemManager()

    class Meta:
        verbose_name = _('قلم متریال')
        verbose_name_plural = _('اقلام متریال')

    def __str__(self):
        return f"{self.get_material_type_display()}"


class OrderPrintAttachment(models.Model):
    """
    فایل‌های پیوست مربوط به متریال چاپ.
    مثال: عکس فرم چاپی، عکس پالت کاغذ مصرفی.
    """
    report = models.ForeignKey(
        OrderPrintReport, 
        related_name='attachments', 
        on_delete=models.CASCADE,
        verbose_name=_("گزارش چاپ")
    )
    file = models.FileField(_("فایل/عکس"), upload_to='orders/print_logs/%Y/%m/')
    title = models.CharField(_("عنوان"), max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderPrintAttachmentManager()

    class Meta:
        verbose_name = _('پیوست چاپ')
        verbose_name_plural = _('پیوست‌های چاپ')

# ===== Order Shipment ===== #
class OrderShipment(models.Model):
    """
    مدل مرسوله.
    این مدل مشخص می‌کند "چه زمانی" و "چگونه" بار ارسال می‌شود.
    یک سفارش ممکن است در ۲ مرسوله جداگانه ارسال شود (Split Shipment).
    """
    SHIPMENT_STATUS = [
        ('processing', _('در حال پردازش انبار')),
        ('ready_to_ship', _('آماده ارسال')),
        ('dispatched', _('تحویل به متصدی')),
        ('delivered', _('تحویل مشتری شد')),
        ('returned', _('مرجوع شد')),
    ]
    
    METHOD_CHOICES = [
        ('terminal', _('باربری ترمینال')),
        ('pickup', _('تحویل حضوری(درب کارگاه)')),
        ('other', _('سایر')),
    ]
    
    order = models.ForeignKey(
        'Order', 
        related_name='shipments', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مربوطه")
    )
    
    delivery_method = models.CharField(
        _("روش ارسال"), 
        max_length=50, 
        choices=METHOD_CHOICES,
        default='other'
    )

    # ===== اطلاعات ارسال ===== #
    destination_address = models.ForeignKey(
        "core.Address", 
        on_delete=models.PROTECT,
        verbose_name=_("آدرس مقصد")
    )
    
    # ===== اطلاعات تحویل ===== #
    tracking_code = models.CharField(_("کد رهگیری پستی"), max_length=100, blank=True, null=True)
    driver_info = models.TextField(_("اطلاعات راننده/پیک"), blank=True, help_text="نام و شماره تماس پیک")
    
    shipping_cost_real = models.DecimalField(_("هزینه واقعی ارسال"), max_digits=15, decimal_places=0, default=0, help_text="هزینه‌ای که ما به پست پرداختیم")
    
    status = models.CharField(_("وضعیت مرسوله"), max_length=20, choices=SHIPMENT_STATUS, default='processing')
    
    # ===== زمان های تحویل ===== #
    expected_delivery_date = models.DateTimeField(_("زمان احتمالی تحویل"), null=True, blank=True)
    dispatched_at = models.DateTimeField(_("زمان خروج از انبار"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("زمان تحویل به مشتری"), null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ShipmentManager()

    class Meta:
        verbose_name = _('مرسوله پستی')
        verbose_name_plural = _('مرسولات پستی')
        
    def __str__(self):
        return f"Shipment #{self.id} | {self.get_status_display()}"

# =====  Order Package Model  ===== #
class OrderPackage(models.Model):
    """
    مدل بسته‌بندی فیزیکی (کارتن/پاکت).
    این مدل دقیقاً همان "لیبل" است.
    اگر یک مرسوله شامل ۳ کارتن باشد، ۳ رکورد در این جدول داریم.
    """
    shipment = models.ForeignKey(
        OrderShipment, 
        related_name='packages', 
        on_delete=models.CASCADE,
        verbose_name=_("مرسوله")
    )
    
    # ===== اطلاعات مربوط به لیبل ===== #
    label_uuid = models.CharField(_("شناسه لیبل"), max_length=50, editable=False, unique=True, null=True, blank=True)
    # ===== محتویات داخل بسته ===== #
    customer_name = models.CharField(_("نام مشتری"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("شماره تماس"), max_length=11, null=True, blank=True)
    address = models.TextField(_("آدرس"), null=True, blank=True)
    order_image = models.ImageField(_("تصویر سفارش"), null=True, blank=True)
    content_summary = models.TextField(_("خلاصه محتویات"), blank=True, help_text="مثلا: ۱۰۰۰ عدد کارت ویزیت لمینت")
    # ===== مسئول بسته بندی ===== #
    packed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        null=True, 
        verbose_name=_("انباردار")
    )
    # ===== تاریخ بسته بندی ===== #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = PackageManager()

    class Meta:
        verbose_name = _('بسته/کارتن')
        verbose_name_plural = _('بسته‌ها و لیبل‌ها')

    def __str__(self):
        return f"{self.customer_name} - {self.label_code}"
    
    @property
    def label_code(self):
        """کد کوتاه خوانا برای چاپ روی لیبل"""
        return str(self.label_uuid).split('-')[0].upper()

# ========== ORDER SCHEDULE ========== #
class OrderSchedule(models.Model):
    """
    مدل زمان‌بندی سفارش.
    به صورت One-to-One به سفارش متصل است.
    """
    order = models.OneToOneField(
        'core.Order', 
        on_delete=models.CASCADE, 
        related_name='schedule',
        verbose_name=_("سفارش مرتبط")
    )
    
    # ===== بازه‌های زمانی ===== #
    start_date = models.DateTimeField(_("تاریخ شروع فرآیند"), default=timezone.now)
    due_date = models.DateTimeField(_("تاریخ تحویل نهایی (Deadline)"))
    # ===== وضعیت اجرا ===== #
    completed_at = models.DateTimeField(_("تاریخ تکمیل واقعی"), null=True, blank=True)
    # ===== تنظیمات مدیریتی ===== #
    # schedule_notes = models.TextField(_("یادداشت برنامه‌ریزی"), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    objects = OrderScheduleManager()

    class Meta:
        verbose_name = _('زمان‌بندی سفارش')
        verbose_name_plural = _('زمان‌بندی‌های سفارش')
        indexes = [
            models.Index(fields=['start_date', 'due_date']),
            models.Index(fields=['completed_at']),
        ]

    def __str__(self):
        return f"Schedule: {self.order.order_code}"

    def clean(self):
        """ اعتبارسنجی سطح دیتابیس """
        if self.due_date and self.start_date and self.due_date < self.start_date:
            raise ValidationError(_("تاریخ تحویل نمی‌تواند قبل از تاریخ شروع باشد."))

    @property
    def duration_days(self):
        """ مدت زمان برنامه‌ریزی شده (روز) """
        return (self.due_date - self.start_date).days

    @property
    def is_overdue(self):
        """ آیا از موعد تحویل گذشته و هنوز تمام نشده؟ """
        if self.completed_at:
            return False
        return timezone.now() > self.due_date

    @property
    def delay_days(self):
        """ میزان تاخیر (اگر تکمیل شده: تفاوت تکمیل با ددلاین / اگر نشده: تفاوت الان با ددلاین) """
        target_date = self.completed_at if self.completed_at else timezone.now()
        if target_date > self.due_date:
            return (target_date - self.due_date).days
        return 0
