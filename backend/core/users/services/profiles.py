from typing import Dict, Any
from ..models import CustomerProfile, User

# ===== Customer Profile Service ===== #
class CustomerProfileService:
    """ سرویسی برای منطق پروفایل کاربر """

    # ===== دریافت پروفایل کاربر ===== #
    def get_or_create_profile(self, user: User) -> CustomerProfile:
        """
        تضمین می‌کند که کاربر حتما پروفایل داشته باشد.
        """
        profile = CustomerProfile.objects.get_by_user_id(user.id)
        
        if not profile:
            profile = CustomerProfile.objects.create(user=user)
            
        return profile
    
    def update_profile(self, user: User, data: Dict[str, Any]) -> CustomerProfile:
        """
        ویرایش اطلاعات پروفایل با اعمال قوانین بیزنس.
        """
        profile = self.get_or_create_profile(user)
        
        # ===== بررسی قوانین بیزنس (فیلترینگ فیلدها) ===== #
        editable_fields = ['first_name', 'last_name', 'company', 'bio']

        clean_data = {k: v for k, v in data.items() if k in editable_fields}

        for key, value in clean_data.items():
            setattr(profile, key, value)
        
        profile.save()
        
        return profile
    