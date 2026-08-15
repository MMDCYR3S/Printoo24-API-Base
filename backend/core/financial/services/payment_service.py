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