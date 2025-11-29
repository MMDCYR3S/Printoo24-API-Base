import logging
from typing import Dict, Any

from django.db import transaction

from core.domain.users.services import UserDomainService
from core.domain.profile.services import CustomerProfileDomainService

# ===== تعریف لاگر اختصاصی برای سرویس پروفایل ===== #
logger = logging.getLogger('userprofile.services.profile')

class ProfileDetailService:
    """
    سرویس مدیریت منطق تجاری پروفایل کاربر.
    
    این سرویس وظیفه دارد اطلاعات کاربر (User) و اطلاعات تکمیلی (CustomerProfile)
    را به صورت یکپارچه مدیریت کند و عملیات بروزرسانی را به صورت اتمیک انجام دهد.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی‌ها ===== #
        self._user_domain = UserDomainService()
        self._profile_domain = CustomerProfileDomainService()
        
    def get_profile_detail(self, user_id: int) -> Dict[str, Any]:
        """
        دریافت اطلاعات پروفایل کاربر
        :param user_id: شناسه کاربر
        :return: دیکشنری شامل آبجکت User و Profile
        """
        logger.info(f"Fetching profile details for User ID: {user_id}")
        user = self._user_domain._repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User ID {user_id} not found.")
            raise ValueError("کاربر یافت نشد.")
        
        profile = self._profile_domain.get_or_create_profile(user)
        
        return {
            "user": user,
            "profile": profile
        }

    @transaction.atomic
    def update_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ویرایش اطلاعات کاربری و پروفایل به صورت اتمیک.

        این متد همزمان جداول User و CustomerProfile را آپدیت می‌کند و
        از یکتایی ایمیل، نام کاربری و شماره تلفن اطمینان حاصل می‌کند.
        """
        logger.info(f"Updating profile for User {user_id}")
        
        
        # ===== 1. دریافت آبجکت‌ها ===== #
        user = self._user_domain._repo.get_by_id(user_id)
        
        if 'username' in data or 'email' in data:
            self._user_domain.update(user, data)
            
        profile_data = {k:v for k,v in data.items() if k in ['first_name', 'last_name', 'phone_number', 'company', 'bio']}
        updated_profile = self._profile_domain.update_profile(user, profile_data)
        
        return {
            "user": user,
            "profile": updated_profile
        }
