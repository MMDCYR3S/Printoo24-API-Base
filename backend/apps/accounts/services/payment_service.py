from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import User, Order, Payment
from ..models import Wallet, WalletTransaction
from .wallet_service import WalletService

class PaymentService:
    """
    سرویس مدیریت پرداخت‌ها
    """

    @transaction.atomic
    def approve_payment(self, payment: Payment, approved_by: User):
        """
        تأیید پرداخت و اعمال آن روی سفارش و کیف پول (در صورت لزوم)
        """
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("فقط پرداخت‌های در انتظار تأیید قابل تأیید هستند.")

        payment.status = Payment.Status.APPROVED
        payment.approved_by = approved_by
        payment.approved_at = timezone.now()
        payment.save()

        order = payment.order

        # ===== ۱. اگر روش پرداخت کیف پول باشد، از کیف پول کسر می‌کنیم =====
        if payment.method == Payment.Method.WALLET:
            wallet_service = WalletService()
            wallet = wallet_service.debit(
                user=payment.user,
                amount=payment.amount,
                description=f"پرداخت سفارش {order.order_code}",
                created_by=approved_by,
                order=order,
                payment=payment,
            )
            # لینک کیف پول به تراکنش (اختیاری)
            payment.wallet = wallet  # اگر فیلد wallet در Payment ندارید این خط را حذف کنید
            payment.save()

        # ===== ۲. به‌روزرسانی مبالغ سفارش =====
        order.paid_amount = (order.paid_amount or 0) + payment.amount
        order.remaining_amount = max(order.final_price - order.paid_amount, 0)

        # به‌روزرسانی وضعیت مالی
        if order.final_price <= 0:
            order.financial_status = Order.FinancialStatus.NO_PAYMENT
        elif order.paid_amount >= order.final_price:
            order.financial_status = Order.FinancialStatus.SETTLED
            order.settlement_date = timezone.now()
        else:
            order.financial_status = Order.FinancialStatus.HAS_BALANCE
        order.save()

        # ===== ۳. ثبت لاگ مالی =====
        FinancialLog.objects.create(
            order=order,
            user=payment.user,
            action_type=FinancialLog.ActionType.PAYMENT_APPROVED,
            description=f"تأیید پرداخت {payment.payment_code} به مبلغ {payment.amount:,} IQD",
            created_by=approved_by,
        )
        return payment

    @transaction.atomic
    def reject_payment(self, payment: Payment, rejected_by: User, reason: str = ""):
        """
        رد پرداخت
        """
        if payment.status != Payment.Status.PENDING:
            raise ValidationError("فقط پرداخت‌های در انتظار تأیید قابل رد هستند.")

        payment.status = Payment.Status.REJECTED
        payment.save()

        # ثبت لاگ
        FinancialLog.objects.create(
            order=payment.order,
            user=payment.user,
            action_type=FinancialLog.ActionType.PAYMENT_REJECTED,
            description=f"رد پرداخت {payment.payment_code}",
            reason=reason,
            created_by=rejected_by,
        )
        return payment