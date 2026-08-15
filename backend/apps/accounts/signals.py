from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from core.models import User

from core.financial.models import Payment
from core.financial.services import PaymentService

# ====== Signals ====== #

@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    """
    سیگنال برای ایجاد خودکار کیف پول پس از ثبت نام کاربر
    """
    if created:
        try:
            from .models import Wallet
            Wallet.objects.create(user=instance)
        except Exception as e:
            print(f"خطا در ایجاد کیف پول برای کاربر {instance.phone_number}: {e}")


@receiver(post_save, sender=User)
def create_customer_profile_for_new_user(sender, instance, created, **kwargs):
    """
    سیگنال برای ایجاد خودکار پروفایل مشتری پس از ثبت نام کاربر
    """
    if created:
        try:
            from .models import CustomerProfile
            CustomerProfile.objects.create(
                user=instance,
                first_name='',
                last_name='',
                phone_number=''
            )
        except Exception as e:
            print(f"خطا در ایجاد پروفایل مشتری برای کاربر {instance.phone_number}: {e}")


@receiver(post_save, sender=User)
def assign_default_role_to_new_user(sender, instance, created, **kwargs):
    """
    سیگنال برای تخصیص نقش پیش‌فرض به کاربر جدید
    (اختیاری - در صورتی که نیاز باشد)
    """
    if created:
        try:
            from .models import Role, UserRole
            
            # ===== پیدا کردن نقش کاربر ===== #
            default_role, _ = Role.objects.get_or_create(name="موشته‌ری" ,type='normal', is_customer=True)
            
            if default_role:
                UserRole.objects.create(
                    user=instance,
                    role=default_role
                )
        except Exception as e:
            print(f"خطا در تخصیص نقش به کاربر {instance.phone_number}: {e}")

@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    if instance.pk:
        instance._old_status = Payment.objects.get(pk=instance.pk).status
    else:
        instance._old_status = None

@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    # اگر پرداخت از داخل سرویس تأیید/رد شده باشد، از اعمال مجدد جلوگیری می‌کنیم
    # تا از بازگشت بی‌پایان سیگنال جلوگیری شود.
    if getattr(instance, '_signal_internal', False):
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status == Payment.Status.PENDING and instance.status == Payment.Status.APPROVED:
        # فقط اثر مالی را اعمال می‌کنیم؛ بدون ذخیره مجدد پرداخت.
        PaymentService().apply_approved_effect(instance)
