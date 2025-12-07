from typing import Dict, List, Any
from core.domain.identity.users import UserAdminDomainService, UserRepository
from ..permissions import AppPermissionChecker

class StaffAppService:
    def __init__(self):
        # ===== اتصال به سرویس ===== #
        self.domain_service = UserAdminDomainService()
        self.repo = UserRepository()

    def get_staff_list(self, requester):
        """ مشاهده لیست کارکنان """
        AppPermissionChecker.check_has_permission(requester, 'view_user')
        return self.repo.get_all_staff()

    def create_staff(self, requester, data: Dict[str, Any]):
        """ ایجاد کارمند جدید """
        AppPermissionChecker.check_has_permission(requester, 'add_user')
        
        # ===== دریافت شناسه نقش ===== #
        role_id = data.pop('role_id')
        
        # ===== ایجاد کارکن ===== #
        return self.domain_service.create_staff(data, role_id)

    def update_staff(self, requester, user_id: int, data: Dict[str, Any]):
        """ ویرایش کارمند """
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        
        role_id = data.pop('role_id', None)
        return self.domain_service.update_staff(user_id, data, role_id)

    def delete_staff(self, requester, user_id: int):
        """ حذف کارمند """
        AppPermissionChecker.check_has_permission(requester, 'delete_user')
        return self.domain_service.delete_single_staff(user_id)

    # ===== عملیات گروهی (Bulk Actions) ===== #
    
    def bulk_delete(self, requester, user_ids: List[int]):
        AppPermissionChecker.check_has_permission(requester, 'delete_user')
        return self.domain_service.bulk_delete_staff(user_ids)

    def bulk_toggle_active(self, requester, user_ids: List[int], is_active: bool):
        # ===== برای تغییرات مورد نظر ===== #
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        return self.domain_service.bulk_toggle_active_status(user_ids, is_active)
    
    def bulk_change_role(self, requester, user_ids: List[int], new_role_id: int):
        # ===== تغییر نقش دسته جمعی ===== #
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        return self.domain_service.bulk_change_role(user_ids, new_role_id)