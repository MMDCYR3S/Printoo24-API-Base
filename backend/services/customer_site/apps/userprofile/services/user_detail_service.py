import logging
from typing import Dict, Any

from django.db import transaction

from core.users.services import CustomerService, CustomerProfileService
from core.infrastructure.messages import msg_provider

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
        self._user_domain = CustomerService()
        self._profile_domain = CustomerProfileService()
        
    def get_profile_detail(self, user_id: int) -> Dict[str, Any]:
        """
        دریافت اطلاعات پروفایل کاربر
        :param user_id: شناسه کاربر
        :return: دیکشنری شامل آبجکت User و Profile
        """
        logger.info(f"Fetching profile details for User ID: {user_id}")
        user = self._user_domain.get_customer_by_id(user_id)
        if not user:
            logger.warning(f"User ID {user_id} not found.")
            raise ValueError(msg_provider.get("profile.E8005"))
        
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
        user = self._user_domain.get_customer_by_id(user_id)
        
        if 'username' in data or 'email' in data:
            self._user_domain.update_customer(user, data)
            
        profile_data = {k:v for k,v in data.items() if k in ['first_name', 'last_name', 'phone_number', 'company', 'bio']}
        updated_profile = self._profile_domain.update_profile(user, profile_data)
        
        return {
            "user": user,
            "profile": updated_profile
        }
