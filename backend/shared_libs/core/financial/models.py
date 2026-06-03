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
        return self.status in [self.Status.PAID_FULL, self.Status.FINALIZE]

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
    
    order = models.ForeignKey(
        'core.Order',
        related_name='expenses',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("سفارش مرتبط"),
        help_text=_("در صورت خالی بودن، هزینه عمومی محسوب می‌شود")
    )
    name = models.CharField(_("عنوان هزینه"), max_length=255)
    amount = models.DecimalField(_("مبلغ"), max_digits=18, decimal_places=0, default=0)
    
    created_at = models.DateTimeField(_("تاریخ ثبت"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاریخ به‌روزرسانی"), auto_now=True)
    
    objects = ExpenseManager()
    
    class Meta:
        db_table = 'core_expenses'
        verbose_name = _('هزینه')
        verbose_name_plural = _('هزینه‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount:,} تومان"
