from django.db.models.signals import post_save, pre_delete, post_migrate
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.utils import timezone

from .models import(
    ProductCategoryRelation, Product,
    product_code_generator, OrderStatus,
    OrderStatusGroup, Role
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
