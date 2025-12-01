from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import (
    User,
    CustomerProfile,
    Wallet,
    Cart,
    Role
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
        Role.objects.create(name="مشتری", description="نقش مشتری")
