import logging
from typing import Dict, Any

from django.db import transaction
from core.models import User, CustomerProfile
from core.common.users.user_repo import UserRepository
from core.common.users.user_services import UserService
from core.common.profile import CustomerProfileService, CustomerProfileRepository

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
        self._user_service = UserService(repository=UserRepository())
        self._profile_service = CustomerProfileService(repository=CustomerProfileRepository())
        
    def get_profile_detail(self, user_id: int) -> Dict[str, Any]:
        """
        دریافت جزئیات کامل پروفایل کاربر.

        Args:
            user_id (int): شناسه کاربر.

        Returns:
            Dict: دیکشنری شامل آبجکت User و Profile.
        """
        logger.info(f"Fetching profile details for User ID: {user_id}")
        
        user = self._user_service.get_by_id(user_id)
        if not user:
            logger.warning(f"User ID {user_id} not found.")
            raise ValueError("کاربر وجود ندارد")
        
        profile = self._profile_service.get_by_user_id(user_id)
        
        return {
            "user": user,
            "profile": profile
        }

    def update_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ویرایش اطلاعات کاربری و پروفایل به صورت اتمیک.

        این متد همزمان جداول User و CustomerProfile را آپدیت می‌کند و
        از یکتایی ایمیل، نام کاربری و شماره تلفن اطمینان حاصل می‌کند.
        """
        logger.info(f"Starting profile update for User ID: {user_id}")
        
        # ===== 1. دریافت آبجکت‌ها ===== #
        user = self._user_service.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد")

        profile = self._profile_service.get_by_user_id(user_id)
        if not profile:
            raise ValueError("پروفایل کاربر یافت نشد")
        
        try:
            with transaction.atomic():
                # ===== 2. استخراج داده‌ها و اعتبارسنجی ===== #
                username = data.get("username")
                email = data.get("email")
                phone_number = data.get("phone_number")

                # ===== بررسی تکراری نبودن نام کاربری ===== #
                if username and User.objects.filter(username=username).exclude(pk=user_id).exists():
                    logger.warning(f"Duplicate username attempt: {username} by User ID: {user_id}")
                    raise ValueError("نام کاربری قبلاً توسط شخص دیگری ثبت شده است")
                
                # ===== بررسی تکراری نبودن ایمیل ===== #
                if email and User.objects.filter(email=email).exclude(pk=user_id).exists():
                    logger.warning(f"Duplicate email attempt: {email} by User ID: {user_id}")
                    raise ValueError("ایمیل قبلاً توسط شخص دیگری ثبت شده است")
                
                # ===== بررسی تکراری نبودن شماره تلفن ===== #
                if phone_number and CustomerProfile.objects.filter(phone_number=phone_number).exclude(pk=profile.pk).exists():
                    logger.warning(f"Duplicate phone attempt: {phone_number} by User ID: {user_id}")
                    raise ValueError("شماره تلفن قبلاً ثبت شده است")

                # ===== 3. اعمال آپدیت‌ها ===== #
                self._user_service.update(user, data)
                self._profile_service.update(profile, data)

                # ===== 4. رفرش کردن داده‌ها از دیتابیس ===== #
                user.refresh_from_db()
                profile.refresh_from_db()
                
                logger.info(f"Profile updated successfully for User ID: {user_id}")

        except ValueError as e:
            # خطاهای اعتبارسنجی را مستقیماً لاگ نمی‌کنیم (یا به صورت INFO لاگ می‌کنیم)
            raise e
        except Exception as e:
            logger.exception(f"System error during profile update for User ID: {user_id}")
            raise ValueError(f"خطای سیستمی در ویرایش پروفایل: {str(e)}")
        
        # ===== 5. بازگرداندن آبجکت‌های بروزرسانی شده ===== #
        return {
            "user": user,
            "profile": profile
        }
