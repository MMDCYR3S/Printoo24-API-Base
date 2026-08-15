from django.utils import timezone

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .managers import (
    InvoiceManager,
    QuotationManager,
    ExpenseManager
)

# ===== Invoice Model ===== #
class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('در انتظار پرداخت')
        PAID_PARTIAL = 'PAID_PARTIAL', _('پرداخت ناقص')
        PAID_FULL = 'PAID_FULL', _('تسویه کامل')
        CANCELED = 'CANCELED', _('لغو شده')
        FINALIZE = 'FINALIZE', _('نهایی شده / بسته شده')

    # فیلدهای اختصاصی فاکتور
    order = models.OneToOneField(
        'core.Order', 
        related_name='invoice', 
        on_delete=models.SET_NULL, 
        verbose_name=_("سفارش مرتبط"),
        null=True, blank=True
    )
    invoice_number = models.CharField(_("شماره فاکتور"), max_length=50, unique=True, db_index=True)
    
    paid_amount = models.DecimalField(_("مبلغ دریافتی تایید شده"), max_digits=18, decimal_places=0, default=0)
    items_amount = models.DecimalField(_("جمع اقلام"), max_digits=18, decimal_places=0, null=True, blank=True)
    services_amount = models.DecimalField(_("جمع خدمات"), max_digits=18, decimal_places=0, default=0)
    tax_amount = models.DecimalField(_("مالیات"), max_digits=18, decimal_places=0, default=0)
    discount_amount = models.DecimalField(_("تخفیف"), max_digits=18, decimal_places=0, default=0)
    final_amount = models.DecimalField(_("مبلغ قابل پرداخت"), max_digits=18, decimal_places=0, default=0)
    description = models.TextField(_("توضیحات"), blank=True)
    status = models.CharField(
        _("وضعیت"), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    
    issued_at = models.DateTimeField(_("تاریخ صدور"), auto_now_add=True)
    due_date = models.CharField(_("سررسید"), null=True, blank=True, max_length=40)
    finalized_at = models.DateTimeField(_("تاریخ قطعی شدن"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    objects = InvoiceManager()
    
    class Meta:
        db_table = 'core_invoices'
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')
        ordering = ['-issued_at']

    def __str__(self):
        return f"Inv #{self.invoice_number}"

    @property
    def remaining_amount(self):
        return self.final_amount - self.paid_amount

    @property
    def is_paid(self):
        return self.status in [self.Status.PAID_FULL, self.Status.FINALIZE, self.Status.PAID_PARTIAL]

# ===== Quotation (Independent) ===== #
class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('پیش‌نویس')
        SENT = 'sent', _('ارسال شده')
        ACCEPTED = 'accepted', _('تایید شده')
        REJECTED = 'rejected', _('رد شده')
        EXPIRED = 'expired', _('منقضی شده')
        CONVERTED = 'converted', _('تبدیل شده به سفارش')

    # فیلدهای اختصاصی پیش‌فاکتور
    quotation_number = models.CharField(
        _("شماره پیش‌فاکتور"),
        max_length=50, unique=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("ایجاد کننده"),
        related_name='created_quotations'
    )
    # ===== سفارش مربوط به پیش فاکتور ===== #
    converted_order = models.OneToOneField(
        'core.Order',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("سفارش تبدیل شده"),
        related_name='origin_quotation'
    )
    customer_name = models.CharField(_("نام مشتری"), max_length=255, null=True)
    product_name = models.CharField(_("نام محصول"), max_length=255, null=True)
    product_image = models.ImageField(
        _("تصویر محصول"),
        upload_to='quotations/products/%Y/%m/%d/',
        null=True, blank=True
    )
    product_snapshot = models.JSONField(
        _("جزئیات پیکربندی (Snapshot)"),
        default=dict,
        null=True, blank=True,
        help_text=_("شامل ابعاد، متریال، آپشن‌ها و ویژگی‌های انتخابی در لحظه صدور")
    )
    quantity = models.PositiveIntegerField(_("تیراژ"), default=0)
    estimated_delivery_date = models.DateField(_("تاریخ تخمینی تحویل"), null=True, blank=True)
    total_price = models.DecimalField(_("مبلغ کل"), max_digits=18, decimal_places=0, default=0)
    
    status = models.CharField(
        _("وضعیت"), max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    valid_until = models.DateField(_("معتبر تا تاریخ"), null=True, blank=True)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_("تاریخ به روزرسانی"), auto_now=True, null=True)

    objects = QuotationManager()

    class Meta:
        db_table = 'core_quotations'
        verbose_name = _('پیش‌فاکتور')
        verbose_name_plural = _('پیش‌فاکتورها')
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote #{self.quotation_number}"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.valid_until and self.valid_until < timezone.now().date():
            return True
        return False

# ===== Expense Model ===== #
class Expense(models.Model):
    """
    مدل ثبت هزینه‌های سازمان.
    می‌تواند به یک سفارش مرتبط باشد یا مستقل (هزینه‌های عمومی).
    """

    EXPENSE_TYPE_CHOICES = [
        ('printing', _("هزینه چاپ")),
        ('material', _("هزینه متریال")),
        ('design', _("هزینه طراحی")),
        ('cutting', _("هزینه برش")),
        ('installation', _("هزینه نصب")),
        ('shipping', _("هزینه حمل")),
        ('packaging', _("هزینه بسته‌بندی")),
        ('labor', _("هزینه نیروی کار")),
        ('supplier', _("خرید از تأمین‌کننده")),
        ('urgent', _("هزینه فوری")),
        ('rework', _("هزینه اصلاح یا دوباره‌کاری")),
        ('other', _("سایر هزینه‌ها")),
    ]

    order = models.ForeignKey(
        'core.Order',
        related_name='expenses',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("سفارش مرتبط"),
        help_text=_("در صورت خالی بودن، هزینه عمومی محسوب می‌شود")
    )

    expense_code = models.CharField(
        _("کد هزینه"),
        max_length=50,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    expense_type = models.CharField(
        _("نوع هزینه"),
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
        default='other'
    )

    name = models.CharField(_("عنوان هزینه"), max_length=255)
    amount = models.DecimalField(_("مبلغ"), max_digits=18, decimal_places=0, default=0)

    quantity = models.PositiveIntegerField(_("تعداد"), default=0)
    unit_price = models.DecimalField(_("قیمت واحد"), max_digits=18, decimal_places=0, default=0)

    description = models.TextField(_("توضیحات"), blank=True, null=True)

    receipt = models.FileField(
        _("فایل رسید"),
        upload_to='expenses/receipts/%Y/%m/%d/',
        null=True,
        blank=True
    )

    expense_date = models.DateField(_("تاریخ هزینه"), auto_now_add=True, null=True, blank=True,)

    registered_by = models.ForeignKey(
        'core.User',
        verbose_name=_("ثبت کننده"),
        related_name='registered_expenses',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به‌روزرسانی"), auto_now=True)

    objects = ExpenseManager()

    class Meta:
        db_table = 'core_expenses'
        verbose_name = _('هزینه')
        verbose_name_plural = _('هزینه‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount:,} IQD"

    def save(self, *args, **kwargs):
        if not self.expense_code:
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            rand_num = random.randint(1000, 9999)
            self.expense_code = f"EXP-{date_str}-{rand_num}"
        super().save(*args, **kwargs)

class Payment(models.Model):
    """
    مدل پرداخت‌های مشتریان
    """

    class Method(models.TextChoices):
        ONLINE = 'online', _('پرداخت آنلاین')
        CASH = 'cash', _('نقدی')
        BANK_TRANSFER = 'bank_transfer', _('حواله بانکی')
        CARD_TO_CARD = 'card_to_card', _('کارت به کارت')
        OFFICE = 'office', _('پرداخت در دفتر')
        WHATSAPP = 'whatsapp', _('پرداخت از طریق واتساپ')
        MANUAL = 'manual', _('ثبت دستی')
        WALLET = 'wallet', _('کیف پول') 

    class Status(models.TextChoices):
        PENDING = 'pending', _('در انتظار تایید')
        APPROVED = 'approved', _('تایید شده')
        REJECTED = 'rejected', _('رد شده')

    order = models.ForeignKey(
        'core.Order',
        verbose_name=_("سفارش مرتبط"),
        related_name='payments',
        on_delete=models.PROTECT
    )

    user = models.ForeignKey(
        'core.User',
        verbose_name=_("پرداخت کننده"),
        related_name='payments',
        on_delete=models.PROTECT
    )

    invoice = models.ForeignKey(
        'core.Invoice',
        verbose_name=_("فاکتور مرتبط"),
        related_name='payments',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    payment_code = models.CharField(
        _("شماره پرداخت"),
        max_length=50,
        unique=True,
        db_index=True
    )

    amount = models.DecimalField(
        _("مبلغ پرداخت"),
        max_digits=18,
        decimal_places=0
    )

    method = models.CharField(
        _("روش پرداخت"),
        max_length=20,
        choices=Method.choices
    )

    status = models.CharField(
        _("وضعیت پرداخت"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reference_number = models.CharField(
        _("شماره مرجع"),
        max_length=100,
        blank=True,
        null=True,
        help_text="شماره تراکنش بانکی، شماره حواله، یا کد پیگیری"
    )

    receipt = models.FileField(
        _("رسید / تصویر پرداخت"),
        upload_to='payments/receipts/%Y/%m/%d/',
        null=True,
        blank=True
    )

    description = models.TextField(_("توضیحات"), blank=True, null=True)

    registered_by = models.ForeignKey(
        'core.User',
        verbose_name=_("ثبت کننده پرداخت"),
        related_name='registered_payments',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="ادمینی که پرداخت را ثبت کرده (برای پرداخت‌های دستی)"
    )

    approved_by = models.ForeignKey(
        'core.User',
        verbose_name=_("تایید کننده"),
        related_name='approved_payments',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    approved_at = models.DateTimeField(
        _("تاریخ تایید"),
        null=True,
        blank=True
    )

    payment_date = models.DateTimeField(
        _("تاریخ پرداخت"),
        default=timezone.now
    )

    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به‌روزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.payment_code} - {self.amount:,} IQD"

    def save(self, *args, **kwargs):
        if not self.payment_code:
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            rand_num = random.randint(1000, 9999)
            self.payment_code = f"PAY-{date_str}-{rand_num}"
        super().save(*args, **kwargs)

class FinancialLog(models.Model):
    """
    لاگ کامل تغییرات مالی برای جلوگیری از خطاهای حسابداری.
    تمام عملیات‌های مهم مالی در این جدول ثبت می‌شوند.
    """

    class ActionType(models.TextChoices):
        QUOTATION_CREATED = 'quotation_created', _('ایجاد پیش‌فاکتور')
        QUOTATION_APPROVED = 'quotation_approved', _('تأیید پیش‌فاکتور توسط مشتری')
        PRICE_UPDATED = 'price_updated', _('اصلاح قیمت')
        ORDER_CREATED = 'order_created', _('ثبت سفارش')
        PAYMENT_RECEIVED = 'payment_received', _('دریافت پرداخت')
        PAYMENT_APPROVED = 'payment_approved', _('تایید پرداخت')
        PAYMENT_REJECTED = 'payment_rejected', _('رد پرداخت')
        INVOICE_CREATED = 'invoice_created', _('صدور فاکتور')
        INVOICE_UPDATED = 'invoice_updated', _('اصلاح فاکتور')
        EXPENSE_ADDED = 'expense_added', _('افزودن هزینه')
        WALLET_DEPOSIT = 'wallet_deposit', _('واریز به کیف پول')
        WALLET_WITHDRAWAL = 'wallet_withdrawal', _('برداشت از کیف پول')
        REFUND_PROCESSED = 'refund_processed', _('برگشت وجه')
        ORDER_SETTLED = 'order_settled', _('تسویه سفارش')
        ORDER_CANCELLED = 'order_cancelled', _('لغو سفارش')

    # ===== ارتباطات ===== #
    order = models.ForeignKey(
        'core.Order',
        verbose_name=_("سفارش"),
        related_name='financial_logs',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        'core.User',
        verbose_name=_("کاربر مرتبط"),
        related_name='financial_logs',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    payment = models.ForeignKey(
        'core.Payment',
        verbose_name=_("پرداخت مرتبط"),
        related_name='financial_logs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    invoice = models.ForeignKey(
        'core.Invoice',
        verbose_name=_("فاکتور مرتبط"),
        related_name='financial_logs',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ===== اطلاعات لاگ ===== #
    action_type = models.CharField(
        _("نوع عملیات"),
        max_length=30,
        choices=ActionType.choices,
        db_index=True
    )

    # ===== تغییرات ===== #
    field_name = models.CharField(
        _("نام فیلد"),
        max_length=100,
        blank=True,
        null=True
    )

    old_value = models.JSONField(
        _("مقدار قبلی"),
        null=True,
        blank=True
    )

    new_value = models.JSONField(
        _("مقدار جدید"),
        null=True,
        blank=True
    )

    # ===== توضیحات ===== #
    description = models.TextField(
        _("توضیحات"),
        blank=True,
        null=True
    )

    reason = models.TextField(
        _("دلیل تغییر"),
        blank=True,
        null=True
    )

    # ===== اطلاعات فنی ===== #
    ip_address = models.GenericIPAddressField(
        _("آدرس IP"),
        null=True,
        blank=True
    )

    user_agent = models.CharField(
        _("مرورگر"),
        max_length=255,
        blank=True,
        null=True
    )

    # ===== سیستم ===== #
    created_by = models.ForeignKey(
        'core.User',
        verbose_name=_("ثبت‌کننده"),
        related_name='created_financial_logs',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        _("تاریخ ثبت"),
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'core_financial_logs'
        verbose_name = _("لاگ مالی")
        verbose_name_plural = _("لاگ‌های مالی")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_type_display()} - {self.created_at}"

    @classmethod
    def log(cls, action_type, created_by=None, **kwargs):
        """
        متد کمکی برای ثبت سریع لاگ.
        مثال:
            FinancialLog.log(
                action_type=FinancialLog.ActionType.PAYMENT_APPROVED,
                order=order,
                user=user,
                description="تأیید پرداخت",
                created_by=admin_user
            )
        """
        return cls.objects.create(
            action_type=action_type,
            created_by=created_by,
            **kwargs
        )

