import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from core.models import Order, User
from apps.notification.models import CustomerNotification
from apps.accounts.models import WalletTransaction
from .tasks import send_order_status_notification, send_wallet_notification
from core.infrastructure.messages import msg_provider

logger = logging.getLogger(__name__)

# ========== ORDER STATUS CHANGE OLD ========== #
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
            instance._old_status_id = old_order.current_status_id
        except Order.DoesNotExist:
            instance._old_status_id = None
    else:
        instance._old_status_id = None

# ========== TRINGGER ORDER NOTIFICATION ========== #
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
        if instance._old_status_id != instance.current_status_id:
            # ===== ارسال اعلان ===== #
            send_order_status_notification.delay(
                order_id=instance.id,
                old_status_id=instance._old_status_id,
                new_status_id=instance.current_status_id
            )

# ========== TRIGGER WALLET NOTIFICATION ========== #
@receiver(post_save, sender=WalletTransaction)
def trigger_wallet_notification(sender, instance, created, **kwargs):
    """
    هر وقت تراکنشی ساخته شد، پیام بده.
    تراکنش‌ها معمولا آپدیت نمی‌شوند (Immutable)، پس فقط created را چک می‌کنیم.
    """
    if created:
        send_wallet_notification.delay(transaction_id=instance.id)

# ========== CREATE NOTIFICATION FOR ADMIN ========== #
@receiver(post_save, sender=Order, dispatch_uid="notify_admin_on_new_order")
def notify_admins_for_new_order(sender, instance, created, **kwargs):
    """
    سیگنال هوشمند ارسال اعلان به ادمین‌ها در زمان ثبت سفارش.
    پشتیبانی از: سفارش کاربر، سفارش مهمان و نادیده‌گرفتن سفارشات ثبتی توسط ادمین.
    """
    if not created:
        return
    
    # ===== تشخیص منبع ثبت ===== #
    if getattr(instance, '_created_by_admin', False):
        logger.info(f"Order {instance.id} created by ADMIN. Skipping notification.")
        return

    # ===== پیدا کردن ادمین‌ها ===== #
    admins = User.objects.filter(is_superuser=True, is_active=True)
    if not admins.exists():
        return

    # ===== تولید محتوای پیام بر اساس نوع کاربر (لاگین شده یا مهمان) ===== #
    order_code = instance.order_code or "---"
    title = msg_provider.get("notification.I6009")['text']
    
    if instance.user:
        sender_user = instance.user.customer_profile.fullname() or instance.user.username
        message = msg_provider.get("notification.I6010", order_code=order_code, sender_name=sender_user)['text']
    else:
        sender_user = instance.recipient_name or "مهمان"
        message = msg_provider.get("notification.I6011", order_code=order_code, sender_name=sender_user)['text']

    # ===== ۴. ذخیره گروهی (Bulk Create) اعلان‌ها ===== #
    content_type = ContentType.objects.get_for_model(instance)
    
    actual_sender = instance.user if instance.user else None

    notifications = [
        CustomerNotification(
            recipient=admin,
            sender=actual_sender,
            name="ثبت سفارش جدید",
            message=message,
            content_type=content_type,
            object_id=instance.id
        )
        for admin in admins
    ]
    
    try:
        CustomerNotification.objects.bulk_create(notifications)
        logger.info(f"Sent {len(notifications)} notifications to admins for Order {instance.id}")
    except Exception as e:
        logger.error(f"Failed to create admin notifications for Order {instance.id}: {str(e)}")
