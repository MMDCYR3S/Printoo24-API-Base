from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .exceptions import InsufficientFundsException
from core.infrastructure.messages import msg_provider
from .managers import (WalletManager, WalletTransactionManager)

# ====== Wallet Model ====== #
class Wallet(models.Model):
    """ مدل کیف پول """
    user = models.OneToOneField("core.User", verbose_name=_("کاربر"), on_delete=models.CASCADE)
    balance = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    objects = WalletManager()
    
    def deposit(self, amount: Decimal):
        """
        منطق خالص دامین: فقط موجودی را زیاد می‌کند.
        هیچ ذخیره‌سازی (save) یا تراکنشی اینجا انجام نمی‌شود.
        """
        if amount <= 0:
            raise ValidationError(msg_provider.get("wallet.E3001"))
        self.balance += amount

    def withdraw(self, amount: Decimal):
        """
        منطق خالص دامین: چک کردن قوانین و کسر موجودی.
        """
        if amount <= 0:
            raise ValidationError(msg_provider.get("wallet.E3001"))
        if self.balance < amount:
            pass
        self.balance -= amount

    class Meta:
        db_table = 'customer_wallets'
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف های پول'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.username
    
# ====== Wallet Transaction Model ====== #
class  WalletTransaction(models.Model):
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
    transaction_type = models.CharField(_("نوع"), max_length=150, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(_("مقدار"), max_digits=12, decimal_places=2, default=0)
    amount_after = models.DecimalField(_("مقدار بعد از عملیات"), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)
    
    objects = WalletTransactionManager()
    
    class Meta:
        db_table = 'customer_wallet_transactions'
        verbose_name = 'تراکنش کیف پول'
        verbose_name_plural = 'تراکنش های کیف پول'
        ordering = ['-created_at']
