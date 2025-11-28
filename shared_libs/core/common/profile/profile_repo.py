from typing import Optional, Dict, Any

from ...models import CustomerProfile
from ..repositories import IRepository

class CustomerProfileRepository(IRepository[CustomerProfile]):
    """
    مخزن برای عملیات سمت پروفایل کاربر
    """
    
    def __init__(self):
        super().__init__(CustomerProfile)
        
    def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        """
        دریافت پروفایل کاربر
        """
        try:
            return self.model.objects.get(user_id=user_id)
        except self.model.DoesNotExist:
            return None
        
    def update(self, instance: CustomerProfile, data: Dict[str, Any]) -> CustomerProfile:
        """
        ویرایش پروفایل کاربر
        """
        ALLOWED_FIELDS = ['first_name', 'last_name', 'phone_number', 'company', 'bio']
        # ===== فیلترینگ برای عدم نفوذ کاربر به اطلاعات حساس ===== # 
        filtered_data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        return super().update(instance, filtered_data)
