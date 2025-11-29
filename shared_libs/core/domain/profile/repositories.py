from typing import Optional, Dict, Any

from ...models import CustomerProfile
from ...utils.base_repository import BaseRepository

class CustomerProfileRepository(BaseRepository[CustomerProfile]):
    """
    مخزن برای عملیات سمت پروفایل کاربر
    """
    
    def __init__(self):
        super().__init__(CustomerProfile)
        
    def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        """
        دریافت پروفایل کاربر
        """
        return self.model.objects.filter(user_id=user_id).first()

    def get_by_username(self, username: str) -> Optional[CustomerProfile]:
        """
        دریافت پروفایل بر اساس نام کاربری
        """
        return self.model.objects.filter(user__username=username).first()
