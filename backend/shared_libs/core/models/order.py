import os
from random import randint

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .product import Product, ProductFileUploadRequirement

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
    TARGET_CHOICES = [
        ('order', _('مختص سفارش (Order Only)')),
        ('item', _('مختص اقلام (Item Only)')),
        ('both', _('مشترک (Both)')),
    ]
    
    name = models.CharField(_('عنوان نمایشی'), max_length=150)
    internal_code = models.SlugField(_('کد سیستمی'), max_length=150, unique=True, null=True, blank=True)

    target_model = models.CharField(
        _('محدوده کاربرد'), 
        max_length=10, 
        choices=TARGET_CHOICES, 
        default='order',
        help_text=_("مشخص می‌کند این وضعیت در کدام بخش نمایش داده شود.")
    )
    status_type = models.CharField(
        _('نوع وضعیت'), 
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='progress'
    )
    is_workflow_gate = models.BooleanField(
        _('دسترسی چندگانه به وضعیت'), 
        default=False, 
        help_text=_("آیا این وضعیت می‌تواند مقصد انتقال‌های خاص (مثل QC) باشد؟")
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
        limit_choices_to=models.Q(target_model__in=['order', 'both']),
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
    order = models.ForeignKey(Order, related_name='order_item_order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_item_product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    status = models.ForeignKey(
        OrderStatus,
        related_name='order_items',
        on_delete=models.PROTECT,
        verbose_name=_("وضعیت آیتم"),
        limit_choices_to=models.Q(target_model__in=['item', 'both']),
        null=True, blank=True
    )
    price = models.DecimalField(_("قیمت"), max_digits=12, decimal_places=2)
    items = models.JSONField(_("آیتم های اضافی"), blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_order_items',
        verbose_name=_("کارشناس مسئول (طراح)")
    )
    admin_note = models.TextField(_("یادداشت تولید"), blank=True, help_text="مخصوص اپراتور چاپ")
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
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
    
    STATUS_CHOICES = [
        ('uploading', _('در حال آپلود/پردازش')),
        ('pending', _('در انتظار بررسی')),
        ('approved', _('تایید شده')),
        ('rejected', _('رد شده (نیازمند اصلاح)')),
    ]
    
    order_item = models.ForeignKey(
        OrderItem, 
        related_name='files', 
        on_delete=models.CASCADE,
        verbose_name=_("آیتم سفارش")
    )
    requirement = models.ForeignKey(
        ProductFileUploadRequirement, 
        on_delete=models.PROTECT,
        verbose_name=_("نوع فایل")
    )
    file = models.FileField(_('فایل نهایی'), upload_to='orders/designs/%Y/%m/%d/')
    version = models.PositiveIntegerField(_('نسخه فایل'), default=1)
    is_latest = models.BooleanField(_('آخرین نسخه است؟'), default=True)
    
    status = models.CharField(_("وضعیت فایل"), max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_feedback = models.TextField(_("دلیل رد شدن / توضیحات QC"), blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

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

# ========================= #
# ===== Order State Log ===== #
# ========================= #
class OrderStateLog(models.Model):
    """
    این مدل تمام تغییرات وضعیت سفارش را ثبت می‌کند.
    هیچ رکوردی در این جدول آپدیت یا پاک نمی‌شود (Append Only).
    """
    order = models.ForeignKey(
        Order, 
        related_name='state_logs', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مرتبط")
    )
    
    from_status = models.ForeignKey(
        OrderStatus, 
        related_name='log_from_status', 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("از وضعیت")
    )
    
    # ===== وضعیت جدید ===== #
    to_status = models.ForeignKey(
        OrderStatus, 
        related_name='log_to_status', 
        on_delete=models.PROTECT,
        verbose_name=_("به وضعیت")
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("تغییر دهنده")
    )
    
    timestamp = models.DateTimeField(_("زمان تغییر"), auto_now_add=True)
    duration_in_previous_status = models.DurationField(_("مدت توقف در مرحله قبل"), null=True, blank=True)
    
    description = models.TextField(_("توضیحات / دلیل تغییر"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = _('تاریخچه تغییر وضعیت')
        verbose_name_plural = _('تاریخچه تغییرات وضعیت')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.order_code} | {self.from_status} -> {self.to_status}"

# ========================================================= #
# ========== مدلاسیون مربوط به هزینه های سفارش ========== #
# ========================================================= #
# ===== Order Cost Type Model ===== #
class OrderCostType(models.Model):
    """
    تعریف انواع هزینه‌های قابل اضافه شدن به سفارش.
    مثال: هزینه تیپاکس، هزینه خدمات طراحی، هزینه برش خاص، هزینه فوریت.
    """
    CATEGORY_CHOICES = [
        ('production', _('تولید و چاپ')),
        ('logistics', _('انبار و ارسال')),
        ('design', _('طراحی')),
        ('general', _('عمومی/سربار')),
    ]

    title = models.CharField(_('عنوان هزینه'), max_length=150)
    code = models.SlugField(_('کد سیستمی'), unique=True, help_text="برای استفاده در محاسبات (مثلا: SHIPPING_FEE)")
    category = models.CharField(_('دسته بندی'), max_length=20, choices=CATEGORY_CHOICES)
    is_deduction = models.BooleanField(_('کسورات؟'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('نوع هزینه')
        verbose_name_plural = _('انواع هزینه')

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class OrderCostCatalog(models.Model):
    """
    لیست استاندارد هزینه‌ها.
    اینجا "کاغذ"، "زینک"، "تیپاکس" فقط یک بار تعریف می‌شوند.
    """
    cost_type = models.ForeignKey(OrderCostType, on_delete=models.PROTECT, verbose_name=_("دسته حسابداری"))
    title = models.CharField(_("شرح استاندارد"), max_length=200)
    code = models.CharField(_("کد کالا/خدمت"), max_length=150, unique=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.code})"

# ===== Order Cost Report Model ===== #
class OrderCostReport(models.Model):
    """
    این مدل همان "گزارش" است که کارفرما خواسته.
    شامل اطلاعات کلی و فایل‌های پیوست.
    """
    order = models.ForeignKey(
        'Order', 
        related_name='cost_reports', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مرتبط")
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name=_("ثبت کننده")
    )
    
    title = models.CharField(_("عنوان گزارش"), max_length=200)
    description = models.TextField(_("توضیحات کلی"), blank=True, null=True)
    attachment = models.FileField(
        _("فایل پیوست/سند"), 
        upload_to='orders/reports/%Y/%m/', 
        null=True, blank=True
    )
    
    is_approved_by_finance = models.BooleanField(_("تایید مالی"), default=False)
    finance_note = models.TextField(_("یادداشت مالی"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('گزارش مالی')
        verbose_name_plural = _('گزارشات مالی')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.order.order_code}"
    
    @property
    def total_amount(self):
        """ جمع کل هزینه‌های این گزارش """
        return sum(item.amount for item in self.items.all())

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
        OrderCostCatalog, 
        on_delete=models.PROTECT,
        verbose_name=_("شرح هزینه"),
        null=True, blank=True
    )
    custom_title = models.CharField(_("عنوان (متفرقه)"), max_length=150, blank=True, null=True)
    amount = models.DecimalField(_("مبلغ"), max_digits=18, decimal_places=0)
    description = models.CharField(_("توضیحات تکمیلی"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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
    
# ===== Order Invoice Model ===== #
class OrderInvoice(models.Model):
    """
    فاکتور نهایی سفارش.
    این جدول نقطه اتصال تمام هزینه‌ها + سود + مالیات است.
    """
    INVOICE_STATUS = [
        ('pending', _('صادر شده - پرداخت نشده')),
        ('partially_paid', _('پرداخت ناقص (پیش‌پرداخت)')),
        ('paid', _('تسویه شده')),
        ('cancelled', _('باطل شده')),
    ]

    order = models.OneToOneField(
        'Order', 
        related_name='invoice_order', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مرتبط")
    )
    
    invoice_number = models.CharField(_("شماره فاکتور"), max_length=50, unique=True)
    items_total = models.DecimalField(_("جمع بهای کالاها"), max_digits=18, decimal_places=0, default=0)
    services_total = models.DecimalField(_("جمع خدمات و هزینه‌ها"), max_digits=18, decimal_places=0, default=0)
    # ===== محاسبات مالی ===== #
    tax_amount = models.DecimalField(_("مالیات (۹٪)"), max_digits=18, decimal_places=0, default=0)
    profit_amount = models.DecimalField(_("سود / کارمزد"), max_digits=18, decimal_places=0, default=0)
    discount_amount = models.DecimalField(_("تخفیف کل"), max_digits=18, decimal_places=0, default=0)
    # ===== قیمت نهایی ===== #
    final_payable_amount = models.DecimalField(_("مبلغ قابل پرداخت"), max_digits=18, decimal_places=0)
    paid_amount = models.DecimalField(_("مبلغ پرداخت شده"), max_digits=18, decimal_places=0, default=0)
    # ===== وضعیت سفارش ===== #
    status = models.CharField(_("وضعیت فاکتور"), max_length=20, choices=INVOICE_STATUS, default='pending')
    # ===== تاریخ صدور ===== #
    issued_at = models.DateTimeField(_("تاریخ صدور"), auto_now_add=True)
    due_date = models.DateTimeField(_("مهلت پرداخت"), null=True, blank=True)
    # ===== تاریخ بروزرسانی ===== #
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('فاکتور فروش')
        verbose_name_plural = _('فاکتورهای فروش')

    def __str__(self):
        return f"Invoice #{self.invoice_number} | {self.get_status_display()}"

# ===== Order Transaction Model ===== #
class OrderTransaction(models.Model):
    """
    تراکنش‌های مالی مرتبط با فاکتور.
    شامل پیش‌پرداخت، تسویه نهایی یا استرداد وجه.
    """
    TX_TYPE = [
        ('deposit', _('پیش پرداخت')),
        ('settlement', _('تسویه حساب')),
        ('refund', _('استرداد وجه')),
    ]
    
    TX_STATUS = [
        ('pending', _('در حال پردازش')),
        ('success', _('موفق')),
        ('failed', _('ناموفق')),
    ]

    invoice = models.ForeignKey(
        OrderInvoice, 
        related_name='transactions', 
        on_delete=models.CASCADE,
        verbose_name=_("فاکتور"),
    )
    
    amount = models.DecimalField(_("مبلغ تراکنش"), max_digits=18, decimal_places=0)
    transaction_type = models.CharField(_("نوع تراکنش"), max_length=20, choices=TX_TYPE)
    
    gateway_name = models.CharField(_("درگاه پرداخت"), max_length=50, blank=True)
    ref_id = models.CharField(_("کد مرجع بانکی"), max_length=100, unique=True, null=True, blank=True)
    tracking_code = models.CharField(_("کد رهگیری"), max_length=100, null=True, blank=True)
    
    status = models.CharField(_("وضعیت"), max_length=20, choices=TX_STATUS, default='pending')
    
    payment_date = models.DateTimeField(_("تاریخ پرداخت"), auto_now_add=True)
    description = models.TextField(_("توضیحات"), blank=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(_("تاریخ به روزرسانی"), auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = _('تراکنش مالی سفارش')
        verbose_name_plural = _('تراکنش‌های مالی سفارش')
        ordering = ['-payment_date']

# ================================================== #
# ========== بخش مربوط به انبار و تحویل ========== #
# ================================================== #
# ===== Delivery Method Model (تنظیمات روش‌های ارسال) ===== #
class DeliveryMethod(models.Model):
    """
    روش‌های ارسال موجود در سیستم.
    مثال: پیک موتوری، پست پیشتاز، تیپاکس، باربری ترمینال.
    """
    title = models.CharField(_('عنوان روش'), max_length=100)
    description = models.TextField(_('توضیحات'), blank=True)
    # ===== قیمت ارسال شناور است یا خیر؟ ===== #
    is_price_dynamic = models.BooleanField(_('قیمت شناور؟'), default=False)
    base_price = models.DecimalField(_("هزینه پایه"), max_digits=15, decimal_places=0, default=0)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('روش ارسال')
        verbose_name_plural = _('روش‌های ارسال')

    def __str__(self):
        return self.title

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
    
    order = models.ForeignKey(
        'Order', 
        related_name='shipments', 
        on_delete=models.CASCADE,
        verbose_name=_("سفارش مربوطه")
    )
    
    delivery_method = models.ForeignKey(
        DeliveryMethod, 
        on_delete=models.PROTECT,
        verbose_name=_("روش ارسال")
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
    label_uuid = models.UUIDField(_("شناسه لیبل"), editable=False, unique=True, null=True, blank=True)
    
    # ===== اطلاعات مربوط به بسته ===== #
    box_number = models.PositiveIntegerField(_("شماره بسته"), default=1)
    weight_grams = models.PositiveIntegerField(_("وزن (گرم)"), default=0)
    width_cm = models.PositiveIntegerField(_("عرض (cm)"), default=0)
    length_cm = models.PositiveIntegerField(_("طول (cm)"), default=0)
    height_cm = models.PositiveIntegerField(_("ارتفاع (cm)"), default=0)
    
    # ===== محتویات داخل بسته ===== #
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

    class Meta:
        verbose_name = _('بسته/کارتن')
        verbose_name_plural = _('بسته‌ها و لیبل‌ها')
        # ===== یکتا بودن با شماره بسته ===== #
        unique_together = ['shipment', 'box_number']

    def __str__(self):
        return f"Box {self.box_number} (Weight: {self.weight_grams}g)"
    
    @property
    def label_code(self):
        """کد کوتاه خوانا برای چاپ روی لیبل"""
        return str(self.label_uuid).split('-')[0].upper()
    