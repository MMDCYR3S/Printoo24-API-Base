from typing import Dict, Any, Optional
from django.db import transaction

from core.common.profile import CustomerProfileService, CustomerProfileRepository    
from core.common.users.user_repo import UserRepository
from core.common.users.user_services import UserService
from core.models import User, CustomerProfile

# ===== Profile Detail Service ===== #
class ProfileDetailService:
    """
    سرویسی برای منطق پروفایل کاربر
    """
    
    def __init__(self):
        """ تعیین ریپازیتوری و تزریق وابستگی """
        self._user_repo = UserRepository()
        self._user_service = UserService(repository=UserRepository())
        self._profile_repo = CustomerProfileRepository()
        self._profile_serivce = CustomerProfileService(repository=CustomerProfileRepository())
        
    # ===== متد دیدن جزئیات و اطلاعات کاربر ===== #
    def get_profile_detail(self, user_id: int) -> Optional[CustomerProfile]:
        """
        دریافت جزئیات و اطلاعات کاربر
        اگر کاربر وجود نداشته باشد، None برگرداند
        """
        # ===== اعتبارسنجی اطلاعات کاربر ===== #
        user = self._user_service.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر وجود ندارد")
        
        profile = self._profile_serivce.get_by_user_id(user_id)
        if not profile:
            raise ValueError("پروفایل کاربر وجود ندارد")
        
        # ===== دریافت اطلاعات کاربر به همراه اطلاعات پروفایل ===== #
        user_profile = {
            "user": user,
            "profile": profile
        }
        
        return user_profile
    
    # ===== متد ویرایش پروفایل کاربر ===== #
    def update_profile(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        """
        ویرایش پروفایل کاربر
        """

        # ===== دریافت و اعتبارسنجی اطلاعات کاربر ===== #
        user = self._user_service.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر وجود ندارد")

        # ===== دریافت و اعتبارسنجی اطلاعات پروفایل ===== #
        profile = self._profile_serivce.get_by_user_id(user)
        if not profile:
            raise ValueError("پروفایل کاربر وجود ندارد")
        
        # ===== ویرایش پروفایل کاربر- حالت اتومیک ===== #
        try:
            with transaction.atomic():
                # ===== ویرایش اطلاعات کاربر ===== #
                updated_user = self._user_service.update(user_id, data)
                
                # ===== اعتبارسنجی اطلاعات کاربر ===== #
                username = data.get("username")
                email = data.get("email")
                if User.objects.filter(username=username).exists():
                    raise ValueError("نام کاربری قبلاً ثبت شده است")
                if User.objects.filter(email=email).exists():
                    raise ValueError("ایمیل قبلاً ثبت شده است")
                
                # ===== ویرایش اطلاعات پروفایل ===== #
                updated_profile = self._profile_serivce.update(user_id, data)

                # ===== اعتبارسنجی اطلاعات پروفایل ===== #
                phone_number = data.get("phone_number")
                if CustomerProfile.objects.filter(phone_number=phone_number).exists():
                    raise ValueError("شماره تلفن قبلاً ثبت شده است")
                
        except Exception as e:
            raise ValueError(f"خطایی در ویرایش پروفایل کاربر: {str(e)}")
        
        return {
            "user" : updated_user,
            "profile": updated_profile
        }