import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from core.models import Order, WalletTransaction
from core.domain.notification.services import NotificationDomainService

logger = logging.getLogger('celery.notification')
User = get_user_model()

@shared_task
def send_order_status_notification(order_id, old_status_id, new_status_id):
    """
    تسک ارسال اعلان تغییر وضعیت سفارش.
    """
    try:
        order = Order.objects.select_related('user', 'order_status').get(id=order_id)
        user = order.user
        # ===== نام تغییر وضعیت برای نام اعلان ===== #
        new_status_name = order.order_status.name
        title = "تغییر وضعیت سفارش"
        message = f"وضعیت سفارش شما با شناسه {order.id} به «{new_status_name}» تغییر یافت."
        
        # ===== ساخت سرویس اعلان ===== #
        service = NotificationDomainService()
        service.send_notification(
            recipient=user,
            title=title,
            message=message,
            target_object=order # لینک به سفارش
        )
        logger.info(f"Order status notification sent for Order {order_id}")
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found in task")
    except Exception as e:
        logger.exception(f"Error in send_order_status_notification: {e}")

@shared_task
def send_wallet_notification(transaction_id):
    """
    تسک ارسال اعلان تراکنش مالی.
    """
    try:
        transaction = WalletTransaction.objects.select_related('user').get(id=transaction_id)
        user = transaction.user
        
        amount = f"{transaction.amount:,.0f}"
        
        # ===== تعیین نوع تراکنش ===== #
        trans_type = transaction.type
        
        if trans_type in ['1', '7', '5']:
            title = "افزایش موجودی"
            if trans_type == '5':
                message = f"مبلغ {amount} تومان بابت برگشت وجه به کیف پول شما واریز شد."
            else:
                message = f"حساب شما به مبلغ {amount} تومان شارژ شد."
                
        elif trans_type in ['2', '6']: # برداشت / پرداخت
            title = "کسر موجودی"
            if trans_type == '6':
                message = f"مبلغ {amount} تومان بابت پرداخت سفارش کسر شد."
            else:
                message = f"مبلغ {amount} تومان از حساب شما برداشت شد."
        else:
            return

        service = NotificationDomainService()
        service.send_notification(
            recipient=user,
            title=title,
            message=message,
            target_object=transaction
        )
        logger.info(f"Wallet notification sent for Transaction {transaction_id}")

    except WalletTransaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")