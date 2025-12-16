from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

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
        on_delete=models.PROTECT, 
        verbose_name=_("سفارش مرتبط")
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
    due_date = models.DateTimeField(_("سررسید"), null=True, blank=True)
    finalized_at = models.DateTimeField(_("تاریخ قطعی شدن"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
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
        return self.status in [self.Status.PAID_FULL, self.Status.FINALIZE]

# ===== Invoice State Log Model ===== #
class InvoiceStateLog(models.Model):
    """
    این مدل دقیقاً پاسخ سوال توست: 'چه کسی و کی وضعیت را عوض کرد؟'
    """
    invoice = models.ForeignKey(Invoice, related_name='logs', on_delete=models.SET_NULL, null=True)
    
    from_status = models.CharField(_("از وضعیت"), max_length=50, null=True, blank=True)
    to_status = models.CharField(_("به وضعیت"), max_length=50)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        verbose_name=_("تغییر دهنده"),
        null=True, blank=True,
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(_("توضیحات (علت تغییر)"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('لاگ وضعیت فاکتور')

# ===== Transaction Model ===== #
class Transaction(models.Model):
    """
    مدل تراکنش (سند دریافت).
    چون درگاه نداریم، اینجا محل آپلود فیش یا ثبت کارت‌به‌کارت است.
    """
    METHOD_CHOICES = [
        ('card_to_card', _('کارت به کارت')),
        ('bank_transfer', _('حواله بانکی (پایا/ساتنا)')),
        ('cash', _('وجه نقد (حضوری)')),
        ('cheque', _('چک')),
        ('pos', _('دستگاه کارتخوان (حضوری)')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار تایید مالی')),
        ('confirmed', _('تایید شده')),
        ('rejected', _('رد شده / مغایرت')),
    ]

    invoice = models.ForeignKey(
        Invoice, 
        related_name='transactions', 
        on_delete=models.CASCADE,
        verbose_name=_("فاکتور")
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_("ثبت کننده")
    )
    
    amount = models.DecimalField(_("مبلغ واریزی"), max_digits=18, decimal_places=0)
    method = models.CharField(_("روش پرداخت"), max_length=20, choices=METHOD_CHOICES)
    
    # ===== سبند دستی ===== #
    receipt_image = models.ImageField(_("تصویر فیش/رسید"), upload_to='financial/receipts/%Y/%m/', blank=True, null=True)
    tracking_code = models.CharField(_("کد پیگیری/ارجاع"), max_length=100, help_text="شماره پیگیری فیش یا حواله")
    payment_date = models.DateTimeField(_("زمان واریز"), help_text="زمانی که پول واریز شده (طبق فیش)")
    
    dest_account = models.CharField(_("واریز به حساب"), max_length=100, blank=True, null=True, help_text="مثلا: بانک ملت - جاری")
    
    # ===== بخش تایید مالی ===== #
    status = models.CharField(_("وضعیت سند"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="confirmed_transactions",
        verbose_name=_("تایید کننده")
    )
    rejection_reason = models.TextField(_("دلیل رد شدن"), blank=True, help_text="اگر فیش جعلی است یا مبلغ نمی‌خواند")
    
    created_at = models.DateTimeField(_("زمان ثبت در سیستم"), auto_now_add=True)

    class Meta:
        verbose_name = _('تراکنش / فیش')
        verbose_name_plural = _('تراکنش‌ها و فیش‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_method_display()} - {self.amount}"

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

    class Meta:
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
