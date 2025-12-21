from typing import Dict, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from core.users.models import User
from core.users.exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException
)

# ========== IDENTITY SERVICE ========== #
class UserIdentityService:
    """
    سرویس دامنه مربوط به هویت و عملیات‌های سمت مشتری (Customer-Facing).
    """

    def check_uniqueness(self, username: str = None, email: str = None, exclude_user_id: int = None):
        """
        بررسی یکتایی نام کاربری و ایمیل.
        """
        if username:
            query = User.objects.filter(username=username)
            if exclude_user_id:
                query = query.exclude(id=exclude_user_id)
            if query.exists():
                raise UsernameAlreadyExistsException("نام کاربری از قبل وجود دارد.")

        if email:
            query = User.objects.filter(email=email)
            if exclude_user_id:
                query = query.exclude(id=exclude_user_id)
            if query.exists():
                raise EmailAlreadyExistsException("ایمیل از قبل وجود دارد.")

    # ========== REGISTRATION ========== #
    @transaction.atomic
    def register_new_customer(self, data: Dict[str, Any]) -> User:
        """
        ثبت نام مشتری جدید.
        """
        # ===== اعتبارسنجی ===== #
        self.check_uniqueness(username=data.get("username"), email=data.get("email"))

        # ===== ایجاد کاربر ===== #
        create_kwargs = {k: v for k, v in data.items() if k not in ['username', 'email', 'password']}
        
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            **create_kwargs
        )
        
        return user

    # ========== VERIFY ========== #
    def verify_user(self, user: User) -> User:
        """تایید حساب کاربری (فعال‌سازی)"""
        if user.is_verified:
            return user
        
        user.is_verified = True
        user.is_active = True
        user.save(update_fields=["is_verified", "is_active"])
        return user

    # ========== UPDATE PROFILE ========== #
    def update_profile_credentials(self, user: User, data: Dict[str, Any]) -> User:
        """
        ویرایش اطلاعات حساس (نام کاربری/ایمیل) توسط خود کاربر.
        """
        new_username = data.get('username')
        new_email = data.get('email')

        # ===== بررسی یکتایی ===== #
        if (new_username and new_username != user.username) or (new_email and new_email != user.email):
            self.check_uniqueness(
                username=new_username if new_username != user.username else None,
                email=new_email if new_email != user.email else None
            )

        # ===== ویرایش اطلاعات ===== #
        allowed_fields = ['username', 'email', 'first_name', 'last_name'] # مثال
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        return user

    # ========== CHANGE PASSWORD ========== #
    def change_password(self, user: User, new_password: str):
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return user