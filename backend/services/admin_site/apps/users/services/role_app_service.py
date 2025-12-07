from typing import Dict, List, Any
from core.domain.identity.roles import RoleAdminDomainService, RoleRepository
from ..permissions import AppPermissionChecker

# ===== Role App Service ===== #
class RoleAppService:
    def __init__(self):
        self.domain_service = RoleAdminDomainService()
        self.repo = RoleRepository()

    def get_role_list(self, requester):
        AppPermissionChecker.check_has_permission(requester, 'view_role')
        return self.repo.get_all_roles()

    def create_role(self, requester, data: Dict[str, Any]):
        """ ایجاد نقش جدید """
        AppPermissionChecker.check_has_permission(requester, 'add_role')
        
        permission_ids = data.pop('permissions', [])
        return self.domain_service.create_role(data, permission_ids)

    def update_role(self, requester, role_id: int, data: Dict[str, Any]):
        AppPermissionChecker.check_has_permission(requester, 'change_role')
        
        permission_ids = data.pop('permissions', None)
        return self.domain_service.update_role(role_id, data, permission_ids)

    def delete_role(self, requester, role_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        return self.domain_service.delete_role(role_id)
    
    def bulk_delete(self, requester, role_ids: List[int]):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        return self.domain_service.bulk_delete_roles(role_ids)
