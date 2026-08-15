import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Order
from core.financial.models import FinancialLog

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def create_financial_log_for_order(sender, instance, created, **kwargs):
    """
    سیگنال ثبت لاگ مالی هنگام ایجاد سفارش.
    فقط در صورت ایجاد (created=True) یک لاگ از نوع ORDER_CREATED ثبت می‌کند.
    """
    if not created:
        return

    try:
        FinancialLog.log(
            action_type=FinancialLog.ActionType.ORDER_CREATED,
            order=instance,
            user=instance.user if instance.user else None,
            description=f"ثبت سفارش {instance.order_code}",
            new_value={
                "order_code": instance.order_code,
                "final_price": str(instance.final_price),
                "financial_status": instance.financial_status,
                "order_type": instance.type,
            },
            created_by=instance.user if instance.user else None,
        )
        logger.info(f"لاگ مالی ثبت سفارش {instance.order_code} ایجاد شد.")
    except Exception as e:
        logger.error(f"خطا در ثبت لاگ مالی برای سفارش {instance.order_code}: {e}")
