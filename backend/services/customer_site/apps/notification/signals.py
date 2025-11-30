from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from core.models import Order, WalletTransaction
from .tasks import send_order_status_notification, send_wallet_notification

# ========= Store Old Order Status ========= #
@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    """
    بررسی وضعیت سفارش هایی که از قبل ثبت شدند
    ایجاد یک متغیر داخل کلاس برای شناسایی سفارش های
    قدیمی، جهت بررسی تغییر وضعیت و اطلاع رسانی.
    """
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            instance._old_status_id = old_order.order_status_id
        except Order.DoesNotExist:
            instance._old_status_id = None
    else:
        instance._old_status_id = None

@receiver(post_save, sender=Order)
def trigger_order_notification(sender, instance, created, **kwargs):
    """
    بررسی وجود داشتن سفارش و سپس، ارسال اعلان.
    اگر جدید بود، به عنوان سفارش جدید، پیام ارسال می شود.
    اگر قدیمی بود، به عنوان پیام قدیمی در نظر گرفته شده و
    تغییر وضعیت را ملاک قرار میدهد.
    """
    # ===== بررسی وجود داشتن سفارش ===== #
    if not created and hasattr(instance, '_old_status_id'):
        if instance._old_status_id != instance.order_status_id:
            # ===== ارسال اعلان ===== #
            send_order_status_notification.delay(
                order_id=instance.id,
                old_status_id=instance._old_status_id,
                new_status_id=instance.order_status_id
            )

# ===== Trigger Wallet Notification ===== #
@receiver(post_save, sender=WalletTransaction)
def trigger_wallet_notification(sender, instance, created, **kwargs):
    """
    هر وقت تراکنشی ساخته شد، پیام بده.
    تراکنش‌ها معمولا آپدیت نمی‌شوند (Immutable)، پس فقط created را چک می‌کنیم.
    """
    if created:
        send_wallet_notification.delay(transaction_id=instance.id)
