import uuid
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from .models import(
    ProductCategoryRelation, Product,
    product_code_generator, OrderStateLog,
    OrderStatusGroup, Role, Order, UserRole,
    User, Payment, Invoice, FinancialLog
)

logger = logging.getLogger(__name__)

# =========== GENERATE CORE ON RELATION CREATION =========== #
@receiver(post_save, sender=ProductCategoryRelation)
def generate_code_on_relation_creation(sender, instance, created, **kwargs):
    """
    این سیگنال دقیقاً زمانی اجرا می‌شود که یک دسته‌بندی به محصول اختصاص داده شود.
    """
    
    product = instance.product
    category = instance.category
    
    if not product.code: 
        
        # ===== دریافت دسته بندی اصلی ===== #
        root_category = category.get_root()
        category_slug = root_category.slug
        
        # ===== تولید کد ===== #
        year = timezone.now().year
        new_code = product_code_generator(category_slug, product.slug, year)
        
        # ===== ذخیره کد ===== #
        Product.objects.filter(pk=product.pk).update(code=new_code)

# ========== CREATE STATUS GROUP ========== #
@receiver(post_save, sender=Role)
def create_status_group_for_role(sender, created, instance, **kwargs):
    """
    ایجاد یک گروه‌بندی برای هر نقشی که در سیستم اضافه می‌شود.
    """

    if not instance.slug:
        pass
    
    status_group, group_created = OrderStatusGroup.objects.get_or_create(
        code=instance.slug,
        defaults={'name': instance.name}
    )
    instance.allowed_groups.add(status_group)
    
    if not group_created and status_group.name != instance.name:
        status_group.name = instance.name
        status_group.save()

    if status_group:
        instance.allowed_groups.add(status_group)

# ===== TRACK STATUS CHANGE (PRE-SAVE) ===== #
@receiver(pre_save, sender=Order)
def capture_old_status(sender, instance, **kwargs):
    """
    چرایی: قبل از ذخیره، وضعیت فعلی دیتابیس را می‌گیریم تا بدانیم وضعیت قبلی چه بوده.
    """
    if instance.pk:
        try:
            old_obj = Order.objects.get(pk=instance.pk)
            instance._old_status = old_obj.current_status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

# ===== LOG STATUS CHANGE (POST-SAVE) ===== #
@receiver(post_save, sender=Order)
def log_order_state_change(sender, instance, created, **kwargs):
    """
    چرایی: بعد از ذخیره، اگر وضعیت تغییر کرده بود، یک رکورد در تاریخچه ثبت می‌کنیم.
    """
    old_status = getattr(instance, '_old_status', None)
    new_status = instance.current_status

    if created or (old_status and old_status != new_status):
        
        # ===== دریافت عامل تغییر (The Logic Fix) ===== #
        actor = getattr(instance, '_status_changer', None)
        
        description = getattr(instance, '_change_reason', None)
        
        if not description:
            if created:
                description = "ثبت اولیه سفارش"
            else:
                from_text = old_status.name if old_status else "نامشخص"
                to_text = new_status.name if new_status else "نامشخص"
                description = f"تغییر وضعیت سیستمی از {from_text} به {to_text}"

        if actor: 
             OrderStateLog.objects.create(
                order=instance,
                from_status=old_status,
                to_status=new_status,
                actor=actor,
                description=description
            )
        else:
            pass

# ===== سیگنال تخصیص نقش پیش‌فرض (مشتری) به کاربر جدید ===== #
@receiver(post_save, sender=User, dispatch_uid="assign_customer_role_on_new_user")
def assign_default_role_to_new_user(sender, instance, created, **kwargs):
    """
    این سیگنال به محض ایجاد یک کاربر جدید در سیستم فراخوانی می‌شود.
    اگر کاربر ادمین یا کارمند نباشد، نقش 'مشتری' به صورت خودکار به او اختصاص می‌یابد.
    """
    
    # ===== بررسی اینکه آیا کاربر جدید است و ادمین/کارمند نیست ===== #
    if created and not instance.is_superuser and not instance.is_staff:
        
        # ===== استفاده از تراکنش برای حفظ یکپارچگی دیتابیس ===== #
        with transaction.atomic():
            try:
                # ===== 1. دریافت نقش مشتری (اگر نبود، با این مشخصات ساخته می‌شود) ===== #
                customer_role, role_created = Role.objects.get_or_create(
                    slug='customer',
                    defaults={
                        'name': 'مشتری',
                        'type': 'normal',
                        'is_customer': True
                    }
                )
                
                if role_created:
                    logger.info("نقش 'مشتری' در سیستم وجود نداشت و به صورت خودکار ایجاد شد.")

                # ===== 2. اختصاص نقش به کاربر (در جدول واسط UserRole) ===== #
                UserRole.objects.get_or_create(
                    user=instance,
                    role=customer_role
                )
                
                logger.info(f"نقش 'مشتری' با موفقیت به کاربر {instance.phone_number} اختصاص یافت.")
                
            except Exception as e:
                # ===== لاگ کردن خطا در صورت بروز مشکل سیستمی ===== #
                logger.error(f"خطا در تخصیص نقش مشتری به کاربر {instance.phone_number}: {str(e)}")

# ===== Generate Invoce Full Payment ===== #
@receiver(post_save, sender=Payment)
def auto_generate_invoice_on_full_payment(sender, instance, created, **kwargs):
    """
    اگر پرداختی تأیید شده و جمع پرداخت‌های تأیید شده سفارش به مبلغ نهایی برسد،
    در صورت نبود فاکتور، فاکتور با وضعیت PAID_FULL صادر می‌شود.
    """
    if instance.status != Payment.Status.APPROVED:
        return

    order = instance.order
    if not order.final_price or order.final_price <= 0:
        return

    total_paid = sum(
        order.payments.filter(status=Payment.Status.APPROVED).values_list('amount', flat=True)
    )
    if total_paid >= order.final_price:
        if not Invoice.objects.filter(order=order).exists():
            with transaction.atomic():
                invoice = Invoice.objects.create(
                    order=order,
                    invoice_number=f"INV-{order.order_code}" if order.order_code else f"INV-{uuid.uuid4().hex[:8].upper()}",
                    paid_amount=total_paid,
                    items_amount=order.base_products_price,
                    final_amount=order.final_price,
                    status=Invoice.Status.PAID_FULL,
                )
                FinancialLog.log(
                    action_type=FinancialLog.ActionType.INVOICE_CREATED,
                    order=order,
                    user=order.user,
                    invoice=invoice,
                    description=f"صدور خودکار فاکتور پس از پرداخت کامل سفارش {order.order_code}",
                    created_by=instance.user,
                )
