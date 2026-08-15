from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import Order, FinancialStatus
from core.financial.models import Payment, FinancialLog
from apps.accounts.services import WalletService


class PaymentService:
    """
    سرویس مدیریت پرداخت‌ها
    """

    @transaction.atomic
    def pay_with_wallet(self, order_id: int, user, amount: Decimal = None) -> Payment:
        """
        پرداخت سفارش با استفاده از کیف پول مشتری
        """
        order = Order.objects.select_for_update().filter(id=order_id).first()
        if not order:
            raise ValidationError("سفارش یافت نشد.")

        if order.user != user:
            raise ValidationError("شما مالک این سفارش نیستید.")

        if order.financial_status in [
            FinancialStatus.SETTLED,
            FinancialStatus.CANCELLED,
            FinancialStatus.REFUNDED,
        ]:
            raise ValidationError("امکان پرداخت برای این سفارش وجود ندارد.")

        # ===== تعیین مبلغ پرداختی ===== #
        if amount is None:
            amount = order.remaining_amount
        if amount <= 0:
            raise ValidationError("مبلغ پرداختی باید بزرگ‌تر از صفر باشد.")
        if amount > order.remaining_amount:
            raise ValidationError("مبلغ پرداختی بیشتر از مانده حساب است.")

        # ===== ایجاد رکورد پرداخت ===== #
        payment = Payment.objects.create(
            order=order,
            user=user,
            amount=amount,
            method=Payment.Method.WALLET,
            status=Payment.Status.APPROVED,
            payment_date=timezone.now(),
            approved_by=user,
            approved_at=timezone.now(),
            description="پرداخت از کیف پول",
        )

        # ===== کسر مبلغ از کیف پول ===== #
        wallet_service = WalletService()
        wallet_service.debit(
            user=user,
            amount=amount,
            description=f"پرداخت سفارش {order.order_code}",
            created_by=user,
            order=order,
            payment=payment,
        )

        # ===== به‌روزرسانی سفارش ===== #
        order.paid_amount = (order.paid_amount or 0) + amount
        if order.deposit_required > 0:
            order.deposit_paid = min(
                (order.deposit_paid or 0) + amount,
                order.deposit_required
            )
        order.save()  # وضعیت مالی به‌صورت خودکار محاسبه می‌شود

        # ===== ثبت لاگ مالی ===== #
        FinancialLog.log(
            action_type=FinancialLog.ActionType.PAYMENT_APPROVED,
            order=order,
            user=user,
            payment=payment,
            description=f"پرداخت {amount:,} IQD از کیف پول برای سفارش {order.order_code}",
            created_by=user,
        )

        return payment

    @transaction.atomic
    def register_payment(
        self,
        order_id: int,
        user,
        amount: Decimal,
        method: str,
        reference_number: str = "",
        description: str = "",
        created_by=None,
    ) -> Payment:
        """
        ثبت پرداخت دستی یا آنلاین (نقدی، کارت‌به‌کارت، حواله و ...) برای یک سفارش.
        پرداخت با وضعیت PENDING ساخته می‌شود و پس از تأیید ادمین روی سفارش اعمال می‌شود.

        توجه: طبق مدل فعلی، اثر مالی (افزایش مبلغ پرداختی سفارش و در صورت لزوم
        برداشت از کیف پول) پس از تأیید اعمال می‌شود.
        """
        order = Order.objects.select_for_update().filter(id=order_id).first()
        if not order:
            raise ValidationError("سفارش یافت نشد.")

        if amount <= 0:
            raise ValidationError("مبلغ پرداختی باید بزرگ‌تر از صفر باشد.")
        if amount > (order.remaining_amount or 0):
            raise ValidationError("مبلغ پرداختی بیشتر از مانده حساب است.")

        payment_payer = order.user or user

        payment = Payment.objects.create(
            order=order,
            user=payment_payer,
            amount=amount,
            method=method,
            status=Payment.Status.PENDING,
            reference_number=reference_number or "",
            description=description or "",
            registered_by=created_by,
        )
        FinancialLog.objects.create(
            order=order,
            user=payment_payer,
            payment=payment,
            action_type=FinancialLog.ActionType.PAYMENT_RECEIVED,
            description=f"ثبت پرداخت {payment.payment_code} به مبلغ {amount:,} IQD (در انتظار تأیید)",
            created_by=created_by,
        )
        return payment

    @transaction.atomic
    def approve_payment(self, payment_id: int, actor) -> Payment:
        """تأیید پرداخت در انتظار و اعمال اثر مالی آن روی سفارش."""
        payment = Payment.objects.select_for_update().filter(id=payment_id).first()
        if not payment:
            raise ValidationError("پرداخت یافت نشد.")
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("فقط پرداخت‌های در انتظار تأیید قابل تأیید هستند.")

        payment.status = Payment.Status.APPROVED
        payment.approved_by = actor
        payment.approved_at = timezone.now()
        payment.save()

        self.apply_approved_effect(payment, actor)
        return payment

    @transaction.atomic
    def reject_payment(self, payment_id: int, actor, reason: str = "") -> Payment:
        """رد یک پرداخت در انتظار."""
        payment = Payment.objects.filter(id=payment_id).first()
        if not payment:
            raise ValidationError("پرداخت یافت نشد.")
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("فقط پرداخت‌های در انتظار تأیید قابل رد هستند.")

        payment.status = Payment.Status.REJECTED
        payment.save()

        FinancialLog.objects.create(
            order=payment.order,
            user=payment.user,
            payment=payment,
            action_type=FinancialLog.ActionType.PAYMENT_REJECTED,
            description=f"رد پرداخت {payment.payment_code}",
            reason=reason,
            created_by=actor,
        )
        return payment

    @transaction.atomic
    def apply_approved_effect(self, payment: Payment, actor=None):
        """
        اعمال اثر مالی پرداختِ تأییدشده روی کیف پول (در صورت روش کیف پول) و سفارش.

        این متد توسط سیگنالِ ثبت/تغییر وضعیت پرداخت نیز صدا زده می‌شود و نباید
        پرداخت را دوباره ذخیره کند تا از بازگشت بی‌پایان سیگنال جلوگیری شود.
        """
        order = payment.order
        actor = actor or payment.approved_by

        if payment.method == Payment.Method.WALLET:
            wallet_service = WalletService()
            wallet_service.debit(
                user=payment.user,
                amount=payment.amount,
                description=f"پرداخت سفارش {order.order_code}",
                created_by=actor,
                order=order,
                payment=payment,
            )

        order.paid_amount = (order.paid_amount or 0) + payment.amount
        if order.deposit_required and order.deposit_required > 0:
            order.deposit_paid = min(
                (order.deposit_paid or 0) + payment.amount,
                order.deposit_required,
            )
        # وضعیت مالی به‌صورت خودکار در متد save محاسبه می‌شود
        order.save()

        FinancialLog.objects.create(
            order=order,
            user=payment.user,
            payment=payment,
            action_type=FinancialLog.ActionType.PAYMENT_APPROVED,
            description=f"تأیید پرداخت {payment.payment_code} به مبلغ {payment.amount:,} IQD",
            created_by=actor,
        )
        return payment