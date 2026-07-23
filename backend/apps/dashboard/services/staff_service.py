from typing import Dict, Any, List
from django.core.exceptions import ValidationError

from core.models import User
from core.users.services import UserAdminService

# ===== STAFF DASHBOARD SERVICE ===== #
class StaffDashboardService:
    """
    سرویس اپلیکیشن برای مدیریت کارمندان در داشبورد ادمین.
    ترکیب کوئری‌های خواندن و ارجاع عملیات نوشتن به سرویس دامنه.
    """
    def __init__(self):
        self.domain_service = UserAdminService()

    # ===== دریافت لیست و جزئیات ===== #
    def get_staff_list(self):
        """ دریافت تمامی کارمندان (پرسنل و ادمین‌ها) """
        return User.objects.get_all_staff()

    def get_staff_detail(self, user_id: int) -> User:
        """ دریافت جزئیات یک کارمند """
        user = User.objects.get_staff_detail(user_id)
        if not user:
            raise ValidationError("کارمند مورد نظر یافت نشد.")
        return user

    # ===== عملیات تکی ===== #
    def create_staff(self, data: Dict[str, Any]) -> User:
        role_id = data.pop('role_id', None)
        return self.domain_service.create_staff(data, role_id)

    def update_staff(self, user_id: int, data: Dict[str, Any]) -> User:
        role_id = data.pop('role_id', None)
        return self.domain_service.update_staff(user_id, data, role_id)

    def delete_staff(self, user_id: int):
        self.domain_service.delete_staff(user_id)

    # ===== عملیات گروهی ===== #
    def bulk_toggle_status(self, user_ids: List[int], is_active: bool) -> int:
        return self.domain_service.bulk_toggle_active(user_ids, is_active)

    def bulk_change_role(self, user_ids: List[int], new_role_id: int) -> int:
        return self.domain_service.bulk_change_role(user_ids, new_role_id)

    def bulk_delete(self, user_ids: List[int]) -> Dict[str, int]:
        return self.domain_service.bulk_delete_staff(user_ids)