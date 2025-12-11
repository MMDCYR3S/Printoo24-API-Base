from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

# ===== Invoice Status Model ===== #
class InvoiceStatus(models.Model):
    """
    وضعیت‌های فاکتور به صورت داینامیک.
    مثال: 'منتظر تایید حسابداری'، 'چک دریافت شد'، 'تسویه کامل'
    """
    name = models.CharField(_('عنوان وضعیت'), max_length=100)
    internal_code = models.SlugField(_('کد سیستمی'), unique=True, help_text="برای استفاده در لاجیک کد (مثلا: PAID_FULL)")
    # ===== تعیین نوع رفتار سیستم ===== #
    is_considered_paid = models.BooleanField(_('به معنی پرداخت شده است؟'), default=False)
    allows_editing = models.BooleanField(_('اجازه ویرایش فاکتور دارد؟'), default=True)
    
    color = models.CharField(_('رنگ نمایش'), max_length=20, default='secondary', help_text="primary, success, danger, ...")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('وضعیت فاکتور')
        verbose_name_plural = _('وضعیت‌های فاکتور')
        ordering = ['sort_order']

    def __str__(self):
        return self.name

# ===== Invoice Model ===== #
class Invoice(models.Model):
    """
    مدل فاکتور.
    این موجودیت مستقل است و "سند قطعی بدهی" مشتری محسوب می‌شود.
    """
    TYPE_CHOICES = [
        ('proforma', _('پیش‌فاکتور')),
        ('final', _('فاکتور رسمی')),
    ]


    order = models.OneToOneField(
        'core.Order', 
        related_name='invoice', 
        on_delete=models.PROTECT, 
        verbose_name=_("سفارش مرتبط")
    )
    
    invoice_type = models.CharField(_("نوع سند"), max_length=20, choices=TYPE_CHOICES, default='proforma')
    invoice_number = models.CharField(_("شماره فاکتور"), max_length=50, unique=True, db_index=True)
    
    # ===== مبالغ مختلف ===== #
    items_amount = models.DecimalField(_("جمع اقلام"), max_digits=18, decimal_places=0)
    services_amount = models.DecimalField(_("جمع خدمات و هزینه‌ها"), max_digits=18, decimal_places=0, default=0)
    
    tax_amount = models.DecimalField(_("مالیات"), max_digits=18, decimal_places=0, default=0)
    discount_amount = models.DecimalField(_("تخفیف"), max_digits=18, decimal_places=0, default=0)
    
    final_amount = models.DecimalField(_("مبلغ کل فاکتور"), max_digits=18, decimal_places=0)
    
    # ===== وضعیت حساب ===== #
    paid_amount = models.DecimalField(_("مبلغ دریافتی تایید شده"), max_digits=18, decimal_places=0, default=0)
    
    status = models.ForeignKey(
        InvoiceStatus, 
        on_delete=models.PROTECT, 
        verbose_name=_("وضعیت جاری"),
        related_name='invoices'
    )
    
    issued_at = models.DateTimeField(_("تاریخ صدور"), auto_now_add=True)
    due_date = models.DateTimeField(_("سررسید"), null=True, blank=True)
    finalized_at = models.DateTimeField(_("تاریخ قطعی شدن فاکتور"), null=True, blank=True)
    
    description = models.TextField(_("توضیحات فاکتور"), blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')
        ordering = ['-issued_at']

    def __str__(self):
        return f"Inv #{self.invoice_number}"

    def convert_to_final(self):
        """
        تبدیل پیش‌فاکتور به فاکتور نهایی.
        این متد زمانی صدا زده می‌شود که سفارش تولید شده، هزینه‌های حمل اضافه شده
        و حالا مشتری باید تسویه نهایی را انجام دهد.
        """
        if self.invoice_type == 'proforma':
            self.invoice_type = 'final'
            self.finalized_at = timezone.now()
            self.save()
            
    @property
    def is_pre_payment_done(self):
        """آیا پیش‌پرداخت (مثلا ۳۰٪) انجام شده؟"""
        return self.paid_amount > (self.final_amount * 0.1)
    
    @property
    def remaining_amount(self):
        """مانده بدهی"""
        return self.final_amount - self.paid_amount

# ===== Invoice State Log Model ===== #
class InvoiceStateLog(models.Model):
    """
    این مدل دقیقاً پاسخ سوال توست: 'چه کسی و کی وضعیت را عوض کرد؟'
    """
    invoice = models.ForeignKey(Invoice, related_name='logs', on_delete=models.CASCADE)
    
    from_status = models.ForeignKey(InvoiceStatus, related_name='log_from', on_delete=models.SET_NULL, null=True)
    to_status = models.ForeignKey(InvoiceStatus, related_name='log_to', on_delete=models.PROTECT)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        verbose_name=_("تغییر دهنده")
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
    
    dest_account = models.CharField(_("واریز به حساب"), max_length=100, blank=True, help_text="مثلا: بانک ملت - جاری")
    
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
