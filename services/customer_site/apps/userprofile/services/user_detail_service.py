from typing import Dict, Any
from django.db import transaction
from core.models import User, CustomerProfile
from core.common.users.user_repo import UserRepository
from core.common.users.user_services import UserService
from core.common.profile import CustomerProfileService, CustomerProfileRepository

class ProfileDetailService:
    """
    سرویسی برای منطق پروفایل کاربر
    """
    
    def __init__(self):
        self._user_service = UserService(repository=UserRepository())
        # اصلاح نام متغیر برای خوانایی بهتر
        self._profile_service = CustomerProfileService(repository=CustomerProfileRepository())
        
    def get_profile_detail(self, user_id: int) -> Dict[str, Any]:
        """ دریافت جزئیات """
        user = self._user_service.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر وجود ندارد")
        
        profile = self._profile_service.get_by_user_id(user_id)
        
        return {
            "user": user,
            "profile": profile
        }

    def update_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ویرایش پروفایل با حل مشکل NoneType
        """
        # 1. دریافت آبجکت‌ها
        user = self._user_service.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد")

        profile = self._profile_service.get_by_user_id(user_id)
        if not profile:
            raise ValueError("پروفایل کاربر یافت نشد")
        
        try:
            with transaction.atomic():
                # 2. بررسی تکراری بودن (Validations)
                username = data.get("username")
                email = data.get("email")
                phone_number = data.get("phone_number")

                if username and User.objects.filter(username=username).exclude(pk=user_id).exists():
                    raise ValueError("نام کاربری قبلاً توسط شخص دیگری ثبت شده است")
                
                if email and User.objects.filter(email=email).exclude(pk=user_id).exists():
                    raise ValueError("ایمیل قبلاً توسط شخص دیگری ثبت شده است")
                
                if phone_number and CustomerProfile.objects.filter(phone_number=phone_number).exclude(pk=profile.pk).exists():
                    raise ValueError("شماره تلفن قبلاً ثبت شده است")

                # 3. اعمال آپدیت‌ها
                # نکته مهم: ما دیگر نتیجه را در متغیر نمی‌ریزیم تا اگر سرویس None برگرداند، به مشکل نخوریم
                self._user_service.update(user, data)
                self._profile_service.update(profile, data)

                # 4. رفرش کردن داده‌ها از دیتابیس برای اطمینان از صحت اطلاعات
                # این کار باعث می‌شود تغییرات اعمال شده حتما روی آبجکت‌ها بنشیند
                user.refresh_from_db()
                profile.refresh_from_db()

        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"خطای سیستمی در ویرایش پروفایل: {str(e)}")
        
        # 5. بازگرداندن آبجکت‌های اصلی که رفرش شده‌اند
        return {
            "user": user,
            "profile": profile
        }
