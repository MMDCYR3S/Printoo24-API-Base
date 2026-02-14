from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import(
    ProductCategoryRelation, Product,
    product_code_generator, OrderStateLog,
    OrderStatusGroup, Role, Order
)   

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
        
# =========== PREVENT SYSTEM DATA DELETION =========== #
# @receiver(pre_delete, sender=OrderStatus)
# @receiver(pre_delete, sender=OrderStatusGroup)
# def prevent_system_data_deletion(sender, instance, **kwargs):
#     """
#     جلوگیری از حذف رکوردهای سیستمی حیاتی.
#     """
#     if instance.is_system:
#         raise PermissionDenied(f"حذف رکورد سیستمی '{instance}' مجاز نیست.")
    
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