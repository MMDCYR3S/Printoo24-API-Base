from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from slugify import slugify

from .managers import *

# ===== ORDER FINANCIAL CONFIGURATION ===== #

class OrderFinancialCategory(models.Model):
    """
    دسته‌بندی‌های مالی (سرفصل‌های حساب).
    توجه: ماهیت (هزینه/درآمد) از اینجا حذف شد و به خود گزارش منتقل شد.
    اینجا فقط نوع عملیات و عنوان را نگه می‌داریم.
    """
    OPERATION_TYPE = [
        ('design', _('واحد طراحی')),
        ('print', _('واحد چاپ/تولید')),
        ('material', _('تامین مواد اولیه')),
        ('logistics', _('لجستیک و ارسال')),
        ('outsourcing', _('برون‌سپاری')),
        ('overhead', _('سربار/عمومی')),
        ('sales', _('فروش و خدمات')),
    ]
    
    title = models.CharField(_("عنوان سرفصل"), max_length=100)
    slug = models.SlugField(_("کد سیستمی"), unique=True)
    
    operation_type = models.CharField(
        _("گروه عملیاتی"), 
        max_length=20, 
        choices=OPERATION_TYPE, 
        default='overhead',
        help_text="برای تفکیک گزارش‌ها در نمودارها (مثلا چقدر خرج چاپ شده)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    objects = OrderFinancialCategoryManager()
    
    class Meta:
        db_table = 'admin_order_financial_categories'
        verbose_name = _("سرفصل مالی سفارش")
        verbose_name_plural = _("سرفصل‌های مالی سفارش")

    def __str__(self):
        return f"{self.title} ({self.get_operation_type_display()})"
    
# ===== Order Financial Type ===== #
class OrderFinancialType(models.Model):
    """ 
    تگ‌های ریز برای گزارش‌گیری (اختیاری).
    """
    title = models.CharField(max_length=100, verbose_name=_("عنوان"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("اسلاگ"), blank=True, null=True)
    
    class Meta:
        db_table = "admin_order_financial_types"
        verbose_name = _("تگ مالی")
        verbose_name_plural = _("تگ‌های مالی")
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

# ===== ORDER P&L SHEET (MAIN DOCUMENT) ===== #

class OrderFinancialSheet(models.Model):
    """
    سند سود و زیان (P&L) اختصاصی هر سفارش.
    """
    order = models.OneToOneField(
        'core.Order', 
        on_delete=models.CASCADE, 
        related_name='financial_sheet',
        verbose_name=_("سفارش مرتبط")
    )
    
    is_locked = models.BooleanField(
        _("قفل حسابرسی"), 
        default=False, 
        help_text="پس از بستن حساب‌های سفارش، امکان تغییر وجود ندارد."
    )
    
    # ===== خروجی‌ها (Costs) ===== #
    total_material_cost = models.DecimalField(_("هزینه مواد"), max_digits=18, decimal_places=0, default=0)
    total_production_cost = models.DecimalField(_("هزینه تولید/چاپ"), max_digits=18, decimal_places=0, default=0)
    total_service_cost = models.DecimalField(_("هزینه خدمات/طراحی"), max_digits=18, decimal_places=0, default=0)
    total_delivery_cost = models.DecimalField(_("هزینه ارسال"), max_digits=18, decimal_places=0, default=0)
    total_other_cost = models.DecimalField(_("سایر هزینه‌ها"), max_digits=18, decimal_places=0, default=0)
    
    final_total_cost = models.DecimalField(_("جمع کل بهای تمام شده"), max_digits=18, decimal_places=0, default=0)
    
    # ===== ورودی‌ها (Revenues) ===== #
    total_revenue = models.DecimalField(_("جمع کل درآمد (فروش + اضافات)"), max_digits=18, decimal_places=0, default=0)
    
    # ===== نتیجه نهایی (Result) ===== #
    net_profit = models.DecimalField(_("سود/زیان خالص"), max_digits=18, decimal_places=0, default=0)
    profit_margin_percent = models.FloatField(_("حاشیه سود (%)"), default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderFinancialSheetManager()

    class Meta:
        db_table = 'admin_order_financial_sheets'
        verbose_name = _("سند سود و زیان سفارش")
        verbose_name_plural = _("اسناد سود و زیان")

    def __str__(self):
        return f"Financial Sheet: {self.order.order_code}"

    def recalculate_totals(self):
        """
        محاسبه مجدد بر اساس ماهیت گزارش (Report Nature).
        """
        # ===== دریافت آیتم‌ها از گزارش‌های تایید شده ===== #
        # نکته: باید report را هم select کنیم چون ماهیت الان توی ریپورت هست
        items = OrderFinancialItem.objects.filter(
            report__sheet=self,
            report__is_approved=True
        ).select_related('category', 'report')

        # ===== ریست کردن متغیرها ===== #
        costs = {
            'material': 0, 'print': 0, 'design': 0, 
            'logistics': 0, 'other': 0
        }
        total_rev = 0
        total_cost = 0

        # ===== پردازش آیتم‌ها ===== #
        for item in items:
            amount = item.amount or 0
            
            # ماهیت را از هدر گزارش می‌خوانیم
            nature = item.report.nature 
            
            if nature == 'revenue':
                total_rev += amount
            else:
                # اگر هزینه بود، تفکیک می‌کنیم که چه نوع هزینه‌ای است
                total_cost += amount
                
                cat = item.category
                if cat:
                    op_type = cat.operation_type
                    if op_type == 'material':
                        costs['material'] += amount
                    elif op_type in ['print', 'outsourcing']:
                        costs['print'] += amount
                    elif op_type == 'design':
                        costs['design'] += amount
                    elif op_type == 'logistics':
                        costs['logistics'] += amount
                    else:
                        costs['other'] += amount
                else:
                    # بدون دسته‌بندی -> سایر
                    costs['other'] += amount

        # ===== آپدیت فیلدهای مدل ===== #
        self.total_material_cost = costs['material']
        self.total_production_cost = costs['print']
        self.total_service_cost = costs['design']
        self.total_delivery_cost = costs['logistics']
        self.total_other_cost = costs['other']
        
        self.final_total_cost = total_cost
        self.total_revenue = total_rev
        
        # ===== محاسبه سود ===== #
        self.net_profit = total_rev - total_cost
        
        if total_rev > 0:
            self.profit_margin_percent = (float(self.net_profit) / float(total_rev)) * 100
        else:
            self.profit_margin_percent = 0.0

        self.save()

# ===== ORDER FINANCIAL REPORTS ===== #
class OrderFinancialReport(models.Model):
    """
    سندی که کاربر ثبت می‌کند.
    ماهیت (هزینه یا درآمد) در اینجا تعیین می‌شود.
    """
    NATURE_CHOICES = [
        ('cost', _('هزینه (Cost) - خروجی')),
        ('revenue', _('درآمد (Revenue) - ورودی')),
    ]

    sheet = models.ForeignKey(
        OrderFinancialSheet, 
        on_delete=models.CASCADE, 
        related_name='reports',
        verbose_name=_("سند مادر")
    )
    
    submitter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name=_("ثبت کننده")
    )
    
    title = models.CharField(_("عنوان گزارش"), max_length=200)
    
    # +++++ فیلد جدید: ماهیت گزارش +++++
    nature = models.CharField(
        _("ماهیت گزارش"), 
        max_length=10, 
        choices=NATURE_CHOICES, 
        default='cost',
        help_text="تعیین می‌کند اقلام این گزارش به درآمد اضافه شوند یا به هزینه."
    )

    financial_tag = models.ForeignKey(
        OrderFinancialType, 
        verbose_name=_("تگ مالی"),
        on_delete=models.SET_NULL,
        blank=True, null=True
    )

    is_approved = models.BooleanField(_("تایید شده"), default=False)
    description = models.TextField(_("توضیحات تکمیلی"), blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderFinancialReportManager()

    class Meta:
        db_table = 'admin_order_financial_reports'
        verbose_name = _('گزارش مالی')
        verbose_name_plural = _('گزارشات مالی')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_nature_display()}) - {self.created_at}"

# ===== Order Financial Item ===== #
class OrderFinancialItem(models.Model):
    """
    اقلام ریز گزارش.
    """
    report = models.ForeignKey(
        OrderFinancialReport,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_("گزارش مرتبط")
    )
    
    category = models.ForeignKey(
        OrderFinancialCategory, 
        on_delete=models.PROTECT,
        verbose_name=_("سرفصل حساب"),
        help_text="گروه عملیاتی (چاپ، طراحی و...) را مشخص می‌کند.",
        blank=True, null=True
    )
    
    custom_title = models.CharField(_("عنوان ریز قلم"), max_length=150, blank=True, null=True)
    amount = models.DecimalField(_("مبلغ"), max_digits=18, decimal_places=0)
    description = models.CharField(_("توضیحات"), max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    objects = OrderFinancialItemManager()

    class Meta:
        db_table = 'admin_order_financial_items'
        verbose_name = _('قلم مالی')
        verbose_name_plural = _('اقلام مالی')

    @property
    def final_title(self):
        return self.custom_title if self.custom_title else self.category.title

    def __str__(self):
        return f"{self.final_title}: {self.amount}"

# ===== Order Financial Attachment ===== #
class OrderFinancialAttachment(models.Model):
    report = models.ForeignKey(
        OrderFinancialReport, 
        related_name='attachments', 
        on_delete=models.CASCADE,
        verbose_name=_("گزارش مرتبط")
    )
    file = models.FileField(_("فایل ضمیمه"), upload_to='financial/attachments/%Y/%m/')
    title = models.CharField(_("عنوان فایل"), max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = OrderFinancialAttachmentManager()

    class Meta:
        db_table = 'admin_order_financial_attachments'
        verbose_name = _('پیوست مالی')
        verbose_name_plural = _('پیوست‌های مالی')

# ===== ORDER SCHEDULE (No Changes) ===== #
class OrderSchedule(models.Model):
    # (همان کدهای قبلی بدون تغییر)
    order = models.OneToOneField(
        'core.Order', 
        on_delete=models.CASCADE, 
        related_name='schedule',
        verbose_name=_("سفارش مرتبط")
    )
    start_date = models.DateTimeField(_("تاریخ شروع فرآیند"), default=timezone.now)
    due_date = models.DateTimeField(_("تاریخ تحویل نهایی (Deadline)"))
    completed_at = models.DateTimeField(_("تاریخ تکمیل واقعی"), null=True, blank=True)

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
        if self.due_date and self.start_date and self.due_date < self.start_date:
            raise ValidationError(_("تاریخ تحویل نمی‌تواند قبل از تاریخ شروع باشد."))

    @property
    def duration_days(self):
        return (self.due_date - self.start_date).days

    @property
    def is_overdue(self):
        if self.completed_at:
            return False
        return timezone.now() > self.due_date

    @property
    def delay_days(self):
        target_date = self.completed_at if self.completed_at else timezone.now()
        if target_date > self.due_date:
            return (target_date - self.due_date).days
        return 0

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
