from typing import List, Optional, Dict, Any

from .profile_repo import CustomerProfileRepository
from core.models import CustomerProfile

# ===== Customer Profile Service ===== #
class CustomerProfileService:
    """ سرویسی برای منطق پروفایل کاربر """
    
    def __init__(self, repository: CustomerProfileRepository):
        """ تعیین ریپازیتوری """
        self._repository = repository or CustomerProfileRepository()
        
    def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        """
        دریافت پروفایل کاربر
        """
        return self._repository.get_by_user_id(user_id)
    
    def update(self, instance: CustomerProfile, data: Dict[str, Any]) -> Optional[CustomerProfile]:
        """
        ویرایش پروفایل کاربر
        این قسمت شامل ویرایش اطلاعات خود پروفایل و
        همچنین ویرایش استان و شهر انتخابی کاربر است.
        """
        return self._repository.update(instance, data)
    