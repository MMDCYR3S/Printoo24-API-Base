from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import (
    User, CustomerProfile, Wallet,
    Cart, Role, UserRole, AccessScope, OrderStatusGroup
)

# ====== Create Wallet When User Created ====== #
@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    """
    این تابع به صورت خودکار اجرا میشود زمانی که یک کاربر ساخته میشود
    و یک کیف پول برای او ساخته میشود
    """
    if created:
        Wallet.objects.create(user=instance)
        
# ====== Create Cart When User Created ====== #
@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    """
    این تابع به صورت خودکار اجرا میشود زمانی که یک کاربر ساخته میشود
    و یک کیف پول برای او ساخته میشود
    """
    if created:
        Cart.objects.create(user=instance)
        
# ========= Create Customer's Profile When User Created ========= #
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    اين تابع به صورت خودکار اجرا مي شود زماني که یک كاربر ساخته مي شود
    و يك كاكيل پايلي براي او ساخته مي شود
    """
    if created:
        CustomerProfile.objects.create(user=instance)

# ========= Create Customer Role If User is Not Admin ========= #
@receiver(post_save, sender=User)
def create_customer_role(sender, instance, created, **kwargs):
    """
    اين تابع به صورت خودکار اجرا مي شود زمانی که یک كاربر ساخته مي شود
    و يك كاربر مي باشد
    """
    if created and not instance.is_superuser and not instance.is_staff:
        try:
            customer_role, _ = Role.objects.get_or_create(name="مشتری", description="نقش مشتری", is_customer=True, type="normal")
            UserRole.objects.create(user=instance, role=customer_role)
        except Role.DoesNotExist:
            pass
    
# ========== Access Scope Signals ========== #
@receiver(post_save, sender=OrderStatusGroup)
def sync_access_scope_create_update(sender, instance, created, **kwargs):
    """
    هر وقت یک گروه وضعیت (مثلا 'برش لیزر') ساخته یا آپدیت شد،
    یک AccessScope متناظر با آن در سیستم امنیتی بساز/آپدیت کن.
    """
    AccessScope.objects.update_or_create(
        code=instance.code, # کلید اتصال کد سیستمی است
        defaults={
            'name': instance.name,
            'description': f"دسترسی اتوماتیک تولید شده برای گروه: {instance.name}"
        }
    )

@receiver(post_delete, sender=OrderStatusGroup)
def sync_access_scope_delete(sender, instance, **kwargs):
    """
    اگر گروه وضعیت پاک شد، اسکوپ دسترسی آن هم پاک شود.
    """
    AccessScope.objects.filter(code=instance.code).delete()
