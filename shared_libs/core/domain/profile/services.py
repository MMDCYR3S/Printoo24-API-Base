from typing import List, Optional, Dict, Any

from .repositories import CustomerProfileRepository
from core.models import CustomerProfile, User

# ===== Customer Profile Service ===== #
class CustomerProfileDomainService:
    """ سرویسی برای منطق پروفایل کاربر """
    
    def __init__(self):
        """ تعیین ریپازیتوری """
        self._repo = CustomerProfileRepository()

    # ===== دریافت پروفایل کاربر ===== #
    def get_or_create_profile(self, user: User) -> CustomerProfile:
        """
        تضمین می‌کند که کاربر حتما پروفایل داشته باشد.
        """
        profile = self._repo.get_by_user_id(user.id)
        if not profile:
            profile = self._repo.create({"user": user})
        return profile
    
    def update_profile(self, user: User, data: Dict[str, Any]) -> CustomerProfile:
        """
        ویرایش اطلاعات پروفایل با اعمال قوانین بیزنس.
        """
        profile = self.get_or_create_profile(user)
        
        # ===== بررسی قوانین بیزنس ===== #
        editable_fields = ['first_name', 'last_name', 'phone_number', 'company', 'bio']
        clean_data = {k: v for k, v in data.items() if k in editable_fields}
        
        return self._repo.update(profile, clean_data)