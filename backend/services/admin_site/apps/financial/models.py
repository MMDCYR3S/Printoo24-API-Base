from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from core.models import Invoice
from .managers import TransactionManager

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
    
    objects = TransactionManager()

    class Meta:
        db_table = 'admin_financial_transactions'
        verbose_name = _('تراکنش / فیش')
        verbose_name_plural = _('تراکنش‌ها و فیش‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_method_display()} - {self.amount}"
