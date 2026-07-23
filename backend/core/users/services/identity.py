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

    def check_uniqueness(self, phone_number: str, exclude_user_id: int = None):
        query = User.objects.filter(phone_number=phone_number)
        if exclude_user_id:
            query = query.exclude(id=exclude_user_id)
        if query.exists():
            raise UsernameAlreadyExistsException("ئەم ژمارەی پەیوەندییە پێشتر تۆمارکراوە.")

    # ========== REGISTRATION ========== #
    @transaction.atomic
    def register_new_customer(self, data: Dict[str, Any]) -> User:
        # ===== بررسی یکتا بودن شماره تلفن ===== #
        self.check_uniqueness(phone_number=data.get("phone_number"))

        # ===== ایجاد کاربر اصلی ===== #
        user = User.objects.create_user(
            phone_number=data["phone_number"],
            password=data["password"]
        )
        
        # ===== ایجاد پروفایل با نام و نام خانوادگی ===== #
        from core.users.models import CustomerProfile
        CustomerProfile.objects.create(
            user=user,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", "")
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
        new_username = data.get('phone_number')

        # ===== بررسی یکتایی ===== #
        if (new_username and new_username != user.username):
            self.check_uniqueness(
                username=new_username if new_username != user.username else None,
            )

        # ===== ویرایش اطلاعات ===== #
        allowed_fields = ['phone_number', 'first_name', 'last_name']
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