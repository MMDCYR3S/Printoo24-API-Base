from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, CustomerProfile, Wallet, Role, UserRole
from core.domain.users import UserRepository

class CustomerOrchestratorService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_customer_list(self):
        return self.user_repo.get_all_customers()

    def get_customer_detail(self, user_id: int) -> User:
        """ دریافت جزئیات کامل مشتری به همراه پروفایل و کیف پول """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("کاربر یافت نشد.")
        return user

    # ===== شاهکار: ایجاد اتمیک مشتری ===== #
    @transaction.atomic
    def create_customer(self, data: Dict[str, Any]) -> User:
        """
        این متد وظیفه دارد تمام متعلقات یک مشتری را یکجا بسازد.
        data شامل: {username, email, password, first_name, last_name, phone_number, ...}
        """
        # ===== ایجاد کاربر ===== #
        user_data = {
            k: v for k, v in data.items() 
            if k in ['username', 'email', 'password', 'is_active']
        }
        profile_data = {
            k: v for k, v in data.items() 
            if k in ['first_name', 'last_name', 'phone_number', 'company', 'bio']
        }

        # ===== ایجاد کاربر ===== #
        user = self.user_repo.create_user(user_data)

        # ===== ایجاد پروفایل ===== #
        CustomerProfile.objects.create(user=user, **profile_data)

        # ===== ایجاد کیف پول ===== #
        Wallet.objects.create(user=user, decimal=0)

        # ===== افزودن نقش ===== #
        customer_role = Role.objects.filter(is_customer=True).first()
        if customer_role:
            UserRole.objects.create(user=user, role=customer_role)

        return user

    # ===== ویرایش اتمیک مشتری ===== #
    @transaction.atomic
    def update_customer(self, user_id: int, data: Dict[str, Any]) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("کاربر یافت نشد.")

        # ===== بروزرسانی اطلاعات پایه ===== #
        allowed_user_fields = ['email', 'username', 'is_active']
        user_update_data = {k: v for k, v in data.items() if k in allowed_user_fields}
        
        if user_update_data:
            self.user_repo.update(user, user_update_data)
        
        # ===== بروزرسانی کلمه عبور ===== #
        if 'password' in data and data['password']:
            user.set_password(data['password'])
            user.save()

        # ===== بروزرسانی اطلاعات بیشتر ===== #
        if hasattr(user, 'customer_profile'):
            profile = user.customer_profile
            profile_fields = ['first_name', 'last_name', 'phone_number', 'company', 'bio']
            for field in profile_fields:
                if field in data:
                    setattr(profile, field, data[field])
            profile.save()

        return user

    # ===== عملیات حذف تکی ===== #
    @transaction.atomic
    def delete_customer(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if user:
            user.delete()

    # ===== عملیات بالک ===== #
    def bulk_toggle_status(self, user_ids: List[int], is_active: bool):
        return self.user_repo.bulk_toggle_active(user_ids, is_active)

    def bulk_delete(self, user_ids: List[int]):
        return self.user_repo.bulk_delete(user_ids)
