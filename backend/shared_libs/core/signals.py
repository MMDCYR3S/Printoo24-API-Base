from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import (
    User, CustomerProfile, Wallet,
    Cart, Role, UserRole, OrderCostReport,
    OrderCostItem
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

# ========== محاسبه قیمت سند مالی ========== #
@receiver(post_save, sender=OrderCostReport)
def update_sheet_on_report_change(sender, instance, created, **kwargs):
    """
    هرگاه گزارشی ذخیره شد (چه جدید، چه آپدیت وضعیت)،
    سند مادر (Sheet) باید دوباره محاسبه شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_delete, sender=OrderCostReport)
def update_sheet_on_report_delete(sender, instance, **kwargs):
    """
    اگر گزارشی حذف شد، مبالغ آن باید از سند مادر کسر شود.
    """
    if instance.sheet:
        instance.sheet.recalculate_totals()

@receiver(post_save, sender=OrderCostItem)
def update_sheet_on_item_change(sender, instance, created, **kwargs):
    """
    اگر مبلغ ریز اقلام تغییر کرد، باید روی ریپورت و سپس روی شیت تاثیر بگذارد.
    """
    if instance.report and instance.report.sheet:
        instance.report.sheet.recalculate_totals()
