from typing import Dict, Any

from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from core.models import User, Role, UserRole
from core.common.users.user_services import UserService
from .verify_service import VerificationService
from .token_serivce import TokenService

# ======= Registration Service ======= #
class AuthService:
    """ کلاس برای ایجاد اکانت مشتری جدید """
    def __init__(self, user_service: UserService, verify_service: VerificationService):
        """ تعیین سرویس کاربر """
        self._user_service = user_service
        self._verify_service = verify_service
        
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
        
        self._verify_service.send_verification_code(user.email)
        
        return user

    def login_user(self, username: str, password: str) -> User:
        """
        ورود کاربر با استفاده از نام کاربری و رمز عبور
        """
        # ====== اعتبار سنجی کاربر ====== #
        user = authenticate(username=username, password=password)
        if not user:
            raise ValidationError("کاربر نامعتبر")
        
        # ====== ایجاد توکن برای کاربر پس از ورود ====== #
        tokens = TokenService.create_token_for_user(user)
        
        return {
            "user" : user,
            "tokens" : tokens,
        }