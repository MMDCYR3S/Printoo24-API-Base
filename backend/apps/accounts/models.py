import random
from datetime import datetime
from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.infrastructure.messages import msg_provider
from .managers import (WalletManager, WalletTransactionManager)

# ====== Wallet Model ====== #
class Wallet(models.Model):
    """
    مدل کیف پول مشتری با اطلاعات آماری و اعتباری کامل
    """

    user = models.OneToOneField(
        "core.User",
        verbose_name=_("کاربر"),
        related_name="wallet",
        on_delete=models.CASCADE
    )

    # ===== موجودی ===== #
    balance = models.DecimalField(
        _("موجودی فعلی"),
        max_digits=18,
        decimal_places=0,
        default=0,
        help_text="موجودی قابل استفاده مشتری (واحد: دینار)"
    )

    # ===== مجموع‌های مالی ===== #
    total_deposits = models.DecimalField(
        _("مجموع واریزها"),
        max_digits=18,
        decimal_places=0,
        default=0
    )

    total_withdrawals = models.DecimalField(
        _("مجموع برداشت‌ها"),
        max_digits=18,
        decimal_places=0,
        default=0
    )

    total_orders = models.DecimalField(
        _("مجموع مبلغ سفارشات"),
        max_digits=18,
        decimal_places=0,
        default=0,
        help_text="مجموع مبلغ سفارشات ثبت شده"
    )

    # ===== اعتبار ===== #
    credit_limit = models.DecimalField(
        _("سقف اعتبار"),
        max_digits=18,
        decimal_places=0,
        default=0,
        help_text="حداکثر اعتبار قابل استفاده"
    )

    is_credit_enabled = models.BooleanField(
        _("اعتبار فعال است؟"),
        default=False
    )

    # ===== آمار ===== #
    total_orders_count = models.PositiveIntegerField(
        _("تعداد کل سفارشات"),
        default=0
    )

    open_orders_count = models.PositiveIntegerField(
        _("تعداد سفارشات باز"),
        default=0
    )

    last_payment_date = models.DateTimeField(
        _("آخرین تاریخ پرداخت"),
        null=True,
        blank=True
    )

    last_invoice_date = models.DateTimeField(
        _("آخرین تاریخ فاکتور"),
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ به روزرسانی'), auto_now=True)

    objects = WalletManager()

    class Meta:
        db_table = 'customer_wallets'
        verbose_name = _('کیف پول')
        verbose_name_plural = _('کیف پول‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} - {self.balance:,} IQD"

    # ===== متدهای دامین ===== #
    def deposit(self, amount: Decimal):
        """
        افزایش موجودی کیف پول.
        ذخیره‌سازی در این متد انجام نمی‌شود؛ فقط موجودی در حافظه تغییر می‌کند.
        """
        if amount <= 0:
            raise ValidationError(_("مبلغ واریز باید بزرگ‌تر از صفر باشد."))
        self.balance += amount

    def withdraw(self, amount: Decimal):
        """
        کاهش موجودی کیف پول با بررسی کافی بودن موجودی.
        """
        if amount <= 0:
            raise ValidationError(_("مبلغ برداشت باید بزرگ‌تر از صفر باشد."))

        if self.balance < amount:
            raise ValidationError(_("موجودی کافی نیست."))

        self.balance -= amount

    # ===== پراپرتی‌های وضعیت ===== #
    @property
    def is_positive(self):
        return self.balance > 0

    @property
    def is_negative(self):
        return self.balance < 0

    @property
    def status(self):
        if self.balance > 0:
            return _("بستانکار")
        elif self.balance < 0:
            return _("بدهکار")
        return _("تسویه شده")
    
# ====== Wallet Transaction Model ====== #
class WalletTransaction(models.Model):
    """
    تراکنش‌های کیف پول مشتری با قابلیت ردیابی کامل
    """

    class Type(models.TextChoices):
        DEPOSIT = 'deposit', _('واریز')
        WITHDRAWAL = 'withdrawal', _('برداشت')
        PAYMENT = 'payment', _('پرداخت سفارش')
        REFUND = 'refund', _('برگشت وجه')
        ADJUSTMENT = 'adjustment', _('تسویه حساب')

    # ===== ارتباطات ===== #
    wallet = models.ForeignKey(
        Wallet,
        verbose_name=_("کیف پول"),
        related_name='transactions',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        "core.User",
        verbose_name=_("کاربر"),
        related_name="wallet_transactions",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    order = models.ForeignKey(
        'core.Order',
        verbose_name=_("سفارش مرتبط"),
        related_name='wallet_transactions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    payment = models.ForeignKey(
        'core.Payment',
        verbose_name=_("پرداخت مرتبط"),
        related_name='wallet_transactions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    invoice = models.ForeignKey(
        'core.Invoice',
        verbose_name=_("فاکتور مرتبط"),
        related_name='wallet_transactions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ===== اطلاعات تراکنش ===== #
    transaction_code = models.CharField(
        _("کد تراکنش"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    transaction_type = models.CharField(
        _("نوع تراکنش"),
        max_length=20,
        choices=Type.choices
    )

    amount = models.DecimalField(
        _("مبلغ"),
        max_digits=18,
        decimal_places=0
    )

    balance_before = models.DecimalField(
        _("موجودی قبل از تراکنش"),
        max_digits=18,
        decimal_places=0,
        default=0
    )

    balance_after = models.DecimalField(
        _("موجودی بعد از تراکنش"),
        max_digits=18,
        decimal_places=0,
        default=0
    )

    description = models.TextField(
        _("توضیحات"),
        blank=True,
        null=True
    )

    # ===== ثبت‌کننده ===== #
    created_by = models.ForeignKey(
        "core.User",
        verbose_name=_("ثبت‌کننده"),
        related_name='created_wallet_transactions',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="کاربری که تراکنش را ثبت کرده است"
    )

    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    objects = WalletTransactionManager()

    class Meta:
        db_table = 'customer_wallet_transactions'
        verbose_name = _('تراکنش کیف پول')
        verbose_name_plural = _('تراکنش‌های کیف پول')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_code} - {self.amount:,} IQD ({self.get_transaction_type_display()})"

    def save(self, *args, **kwargs):
        # تولید خودکار کد یکتا در صورت نبود
        if not self.transaction_code:
            date_str = datetime.now().strftime('%Y%m%d')
            rand_num = random.randint(1000, 9999)
            self.transaction_code = f"WT-{date_str}-{rand_num}"

        super().save(*args, **kwargs)