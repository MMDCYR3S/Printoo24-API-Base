import logging
import uuid
from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import timezone

from .models import CartItem, Cart
from core.financial.models import Quotation, FinancialLog
from core.models import User  # در صورت نیاز

logger = logging.getLogger(__name__)


def generate_quotation_number():
    """
    تولید شماره یکتا برای پیش‌فاکتور.
    قالب: QTE-YYYYMMDD-XXXXXXXX
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = uuid.uuid4().hex[:8].upper()
    return f"QTE-{date_str}-{random_suffix}"


def get_customer_name(cart_item):
    """
    دریافت نام مشتری از سبد خرید.
    اگر کاربر لاگین کرده باشد، نام یا شماره تماس او را برمی‌گرداند.
    در غیر این صورت، 'مهمان' برگردانده می‌شود.
    """
    if cart_item.cart.user:
        user = cart_item.cart.user
        # تلاش برای دریافت پروفایل مشتری
        try:
            profile = user.customer_profile
            if profile.first_name or profile.last_name:
                return f"{profile.first_name} {profile.last_name}".strip()
        except:
            pass
        return user.phone_number
    return "مهمان"


def get_product_image(product):
    """
    دریافت تصویر اصلی محصول (در صورت وجود).
    """
    try:
        first_image = product.product_image.first()
        if first_image:
            return first_image.image
    except AttributeError:
        pass
    return None


@receiver(post_save, sender=CartItem)
def create_quotation_for_cart_item(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        cart_item = instance
        cart = cart_item.cart

        total_price = cart_item.price
        quantity = cart_item.quantity or 1

        quotation = Quotation.objects.create(
            quotation_number=generate_quotation_number(),
            created_by=cart.user if cart.user else None,
            cart_item=cart_item,  # اتصال به آیتم سبد خرید
            customer_name=None,    # بعداً هنگام ثبت سفارش تکمیل می‌شود
            product_name=cart_item.product.name if cart_item.product else cart_item.name,
            product_image=cart_item.product.product_image.order_by('order').first().image
                            if cart_item.product and cart_item.product.product_image.exists() else None,
            product_snapshot=cart_item.items if cart_item.items else {},
            quantity=quantity,
            estimated_delivery_date=None,
            total_price=total_price,
            status=Quotation.Status.DRAFT,
            valid_until=timezone.now() + timezone.timedelta(days=7),
        )

        FinancialLog.log(
            action_type=FinancialLog.ActionType.QUOTATION_CREATED,
            user=cart.user if cart.user else None,
            description=f"ایجاد خودکار پیش‌فاکتور {quotation.quotation_number} برای آیتم سبد خرید",
            created_by=cart.user if cart.user else None,
        )
        logger.info(f"پیش‌فاکتور {quotation.quotation_number} برای CartItem {cart_item.id} ایجاد شد.")

    except Exception as e:
        logger.error(f"خطا در ایجاد خودکار پیش‌فاکتور برای CartItem {instance.id}: {e}")