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
    """
    سیگنال: هنگام ایجاد یک آیتم جدید در سبد خرید، یک پیش‌فاکتور خودکار صادر می‌شود.
    توجه: فقط در صورت ایجاد (created=True) اجرا می‌شود.
    """
    if not created:
        return

    try:
        cart_item = instance
        cart = cart_item.cart

        # ===== ۱. محاسبه قیمت کل آیتم ===== #
        unit_price = cart_item.price
        quantity = cart_item.quantity
        total_price = unit_price * quantity

        # ===== ۲. ساخت شماره پیش‌فاکتور ===== #
        quotation_number = generate_quotation_number()

        # ===== ۳. تعیین نام مشتری ===== #
        customer_name = get_customer_name(cart_item)

        # ===== ۴. اطلاعات محصول ===== #
        product = cart_item.product
        product_name = product.name if product else cart_item.name
        product_image = get_product_image(product) if product else None
        product_snapshot = cart_item.items if cart_item.items else {}

        # ===== ۵. ایجاد پیش‌فاکتور ===== #
        quotation = Quotation.objects.create(
            quotation_number=quotation_number,
            created_by=cart.user if cart.user else None,
            customer_name=customer_name,
            product_name=product_name,
            product_image=product_image,
            product_snapshot=product_snapshot,
            quantity=quantity,
            estimated_delivery_date=None,
            total_price=total_price,
            status=Quotation.Status.DRAFT,
            valid_until=timezone.now() + timezone.timedelta(days=7),
        )

        # ===== ۶. ثبت لاگ مالی (اختیاری اما توصیه‌شده) ===== #
        FinancialLog.log(
            action_type=FinancialLog.ActionType.QUOTATION_CREATED,
            user=cart.user if cart.user else None,
            description=f"ایجاد خودکار پیش‌فاکتور {quotation_number} برای آیتم سبد خرید (محصول: {product_name})",
            new_value={
                'cart_item_id': cart_item.id,
                'quotation_id': quotation.id,
                'amount': str(total_price),
            },
            created_by=cart.user if cart.user else None,
        )

        logger.info(f"پیش‌فاکتور {quotation_number} برای CartItem {cart_item.id} ایجاد شد.")

    except Exception as e:
        logger.error(f"خطا در ایجاد خودکار پیش‌فاکتور برای CartItem {instance.id}: {e}")
