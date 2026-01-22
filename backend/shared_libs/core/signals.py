from django.db.models.signals import post_save, pre_delete
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.utils import timezone

from .models import(
    ProductCategoryRelation, Product,
    product_code_generator, OrderStatus,
    OrderStatusGroup
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
@receiver(pre_delete, sender=OrderStatus)
@receiver(pre_delete, sender=OrderStatusGroup)
def prevent_system_data_deletion(sender, instance, **kwargs):
    """
    جلوگیری از حذف رکوردهای سیستمی حیاتی.
    """
    if instance.is_system:
        raise PermissionDenied(f"حذف رکورد سیستمی '{instance}' مجاز نیست.")
    