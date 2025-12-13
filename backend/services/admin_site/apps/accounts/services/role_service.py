import logging
from typing import Dict, List, Any

from core.domain.identity.roles import RoleAdminDomainService, RoleRepository
from apps.permissions import AppPermissionChecker

# ===== Logger Initialization ===== #
logger = logging.getLogger('apps.users.services.role_app_service')

# ===== Role App Service ===== #
class RoleAppService:
    def __init__(self):
        self.domain_service = RoleAdminDomainService()
        self.repo = RoleRepository()

    def get_role_list(self, requester):
        AppPermissionChecker.check_has_permission(requester, 'view_role')
        return self.repo.get_all_roles().prefetch_related('scopes')

    def create_role(self, requester, data: Dict[str, Any]):
        """
        تابع ساخت نقش براساس مجوزها و محدوده ها
        """
        AppPermissionChecker.check_has_permission(requester, 'add_role')
        
        permission_ids = data.pop('permissions', [])
        scope_ids = data.pop('scope_ids', None)
        
        try:
            role = self.domain_service.create_role(data, permission_ids)
            logger.info(f"Role created: '{role.name}' (Slug: {role.slug}) by '{requester.username}'")
            return role
        except Exception as e:
            logger.error(f"Error creating role by '{requester.username}': {str(e)}")
            raise e

    def update_role(self, requester, role_id: int, data: Dict[str, Any]):
        """
        تابع بروزرسانی یک نقش
        """
        AppPermissionChecker.check_has_permission(requester, 'change_role')
        
        permission_ids = data.pop('permissions', None)
        scope_ids = data.pop('scope_ids', None)
        
        try:
            role = self.domain_service.update_role(role_id, data, permission_ids, scope_ids)
            logger.info(f"Role updated: ID {role_id} by '{requester.username}'")
            return role
        except Exception as e:
            logger.error(f"Error updating role ID {role_id}: {str(e)}")
            raise e
    def delete_role(self, requester, role_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        try:
            self.domain_service.delete_role(role_id)
            logger.info(f"Role deleted: ID {role_id} by '{requester.username}'")
        except Exception as e:
            logger.error(f"Error deleting role ID {role_id}: {str(e)}")
            raise e
    
    def bulk_delete(self, requester, role_ids: List[int]):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        try:
            count = self.domain_service.bulk_delete_roles(role_ids)
            logger.info(f"Bulk role delete: {count} roles by '{requester.username}'")
            return count
        except Exception as e:
            logger.error(f"Error in bulk delete roles by '{requester.username}': {str(e)}")
            raise e
