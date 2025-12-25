from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from .managers import *

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
        db_table = 'admin_order_cost_categories'
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
        db_table = 'admin_order_cost_sheets'
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
        db_table = 'admin_order_cost_reports'
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
        db_table = 'admin_order_cost_items'
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
        db_table = 'admin_order_cost_attachments'
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
        'core.Order', 
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
        db_table = 'admin_order_print_reports'
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
        db_table = 'admin_order_print_items'
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
        db_table = 'admin_order_print_attachments'
        verbose_name = _('پیوست چاپ')
        verbose_name_plural = _('پیوست‌های چاپ')

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
        db_table = 'admin_order_schedules'
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
