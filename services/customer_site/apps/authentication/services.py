from typing import Dict, Any

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from core.models import User, Role, UserRole
from core.common.users.user_services import UserService

# ======= Registration Service ======= #
class RegistrationService:
    """ کلاس برای ایجاد اکانت مشتری جدید """
    def __init__(self, user_service: UserService):
        """ تعیین سرویس کاربر """
        self._user_service = user_service
        
    @transaction.atomic
    def register_user(self, validated_data: Dict[str, Any]) -> User:
        """
        سرویس برای ثبت نام مشتری جدید با فیلد های چک شده
        منطق کامل:
        1- ایجاد کاربر توسط سرویس UserService
        2- بررسی وجود نقش Customer و در صورت وجود، اختصاص به مشتری
        3- پس از ساخت، به لطف سیگنال های ایجاد شده، یک سبد خرید، کیف پول
        و پروفایل برای کاربر ساخته خواهد شد.
        """
        
        # ===== ایجاد کاربر ===== #
        user = self._user_service.create_user(validated_data)
        
        # ===== بررسی وجود نقش مشتری (Customer) ===== #
        try:
            customer_role, created = Role.objects.get_or_create(name="مشتری")
            UserRole.objects.create(user=user, role=customer_role)
        except Exception as e:
            raise ValidationError(e)
        
        return user
