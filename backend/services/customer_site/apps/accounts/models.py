from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import (WalletManager, WalletTransactionManager)

# ====== Wallet Model ====== #
class Wallet(models.Model):
    """ مدل کیف پول """
    user = models.OneToOneField("core.User", verbose_name=_("کاربر"), on_delete=models.CASCADE)
    decimal = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    objects = WalletManager()    

    class Meta:
        db_table = 'customer_wallet'
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف های پول'
    
    def __str__(self):
        return self.user.username
    
# ====== Wallet Transaction Model ====== #
class WalletTransaction(models.Model):
    """
    مدل تراکنش های کیف پول
    """
    TRANSACTION_TYPE = [
        ("1", _("افزایش")),
        ("2", _("کاهش")),
        ("3", _("تایید")),
        ("4", _("رد")),
        ("5", _("برگشت")),
        ("6", _("پرداخت")),
        ("7", _("دریافت")),
        ("8", _("تایید پرداخت")),
        ("9", _("رد پرداخت")),
    ]
    
    user = models.ForeignKey("core.User", related_name="wallet_transactions", on_delete=models.CASCADE)
    type = models.CharField(_("نوع"), max_length=150, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    amount_after = models.DecimalField(_("مقدار بعد از عملیات"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = WalletTransactionManager()
    
    class Meta:
        db_table = 'customer_wallet_transaction'
        verbose_name = 'تراکنش کیف پول'
        verbose_name_plural = 'تراکنش های کیف پول'
