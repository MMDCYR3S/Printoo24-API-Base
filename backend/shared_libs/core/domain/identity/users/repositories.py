from typing import Any, Dict, Optional

from django.db.models import QuerySet

from ....utils.base_repository import BaseRepository
from core.models import User
from .exceptions import (
    EmailAlreadyExistsException,
    EmailNotFoundException,
    UsernameNotFoundException
)

# ====== User Repository ====== #
class UserRepository(BaseRepository[User]):
    """ ریپازیتوری مربوط به قوانین کاربران سیستم """
    
    def __init__(self):
        super().__init__(User)
    
    # ===== دریافت براساس شناسه ===== #
    def get_by_id(self, id: int) -> Optional[User]:
        """ دریافت یک کاربر با شناسه """
        return self.model.objects.filter(id=id).first()
        
    # ===== دریافت براساس نام کاربری ===== #
    def get_by_username(self, username: str) -> Optional[User]:
        """ دریافت کاربر با نام کاربری مشخص """
        return self.model.objects.filter(username=username).first()
    
    # ===== دریافت براساس ایمیل ===== #
    def get_by_email(self, email: str) -> Optional[User]:
        """ دریافت کاربر با ایمیل مشخص """
        return self.model.objects.filter(email=email).first()
    
    # ===== ایجاد کاربر ===== #
    def create_user(self, data: Dict[str, Any]) -> User:
        """
        ایجاد یک کاربر جدید با داده های مشخص شده
        """
        return self.model.objects.create_user(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            **{k: v for k, v in data.items() if k not in ['username', 'email', 'password']}
        )

    # ===== ذخیره کاربر ===== #
    def save(self, user: User) -> User:
        """ ذخیره کاربر """
        user.save()
        return user

    # ===== دریافت لیست مشتریان ===== #
    def get_all_customers(self) -> QuerySet[User]:
        """
        دریافت کاربرانی که پروفایل مشتری دارند یا نقش مشتری دارند.
        تحلیل‌گر: برای پرفورمنس، related_models را prefetch می‌کنیم.
        """
        return self.model.objects.filter(
            is_superuser=False, 
            is_staff=False,
            user_role__role__is_customer=True
        ).select_related('customer_profile', 'wallet').order_by('-created_at')

    # ===== عملیات بالک (دسته‌جمعی) ===== #
    def bulk_toggle_active(self, user_ids: list[int], is_active: bool) -> int:
        return self.model.objects.filter(id__in=user_ids).update(is_active=is_active)

    def bulk_delete(self, user_ids: list[int]) -> tuple:
        return self.model.objects.filter(id__in=user_ids).delete()
