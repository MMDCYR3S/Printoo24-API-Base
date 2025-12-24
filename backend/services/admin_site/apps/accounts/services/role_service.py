import logging
from typing import Dict, List, Any

from django.utils.translation import gettext_lazy as _

from core.models import Role
from core.users.services import RoleAdminService
from core.logger.services import LoggerService
from apps.permissions import AppPermissionChecker

# ===== Logger Initialization ===== #
logger = logging.getLogger('apps.users.services.role_app_service')

# ========== ROLE APP SERVICE ========== #
class RoleAppService:
    def __init__(self):
        self.domain_service = RoleAdminService()
        self.audit_service = LoggerService()

    def get_role_list(self, requester):
        AppPermissionChecker.check_has_permission(requester, 'view_role')
        return Role.objects.get_all_roles().prefetch_related('allowed_groups')

    def create_role(self, requester, data: Dict[str, Any]):
        """
        تابع ساخت نقش براساس مجوزها و محدوده ها
        """
        AppPermissionChecker.check_has_permission(requester, 'add_role')
        
        permission_ids = data.pop('permissions', [])
        allowed_groups_ids = data.pop('allowed_groups_ids', None)
        
        try:
            role = self.domain_service.create_role(data, permission_ids, allowed_groups_ids)
            # ===== ثبت لاگ ===== #
            self.audit_service.record_log(
                user=requester,
                obj=role,
                action='CREATE_ROLE',
                changes={
                    'name': role.name,
                    'permissions_count': len(permission_ids),
                    'groups_count': len(allowed_groups_ids) if allowed_groups_ids else 0
                },
                description=_(f"ایجاد نقش جدید: {role.name}")
            )
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
        # ===== بررسی نوع دسترسی کاربر ===== #
        permission_ids = data.pop('permissions', None)
        allowed_groups_ids = data.pop('allowed_groups_ids', None)
        
        try:
            role = self.domain_service.update_role(role_id, data, permission_ids, allowed_groups_ids)
            # ===== ثبت لاگ ===== #
            self.audit_service.record_log(
                user=requester,
                obj=role,
                action='UPDATE_ROLE',
                changes={'updated_fields': list(data.keys())},
                description=_(f"ویرایش نقش: {role.name}")
            )
            logger.info(f"Role updated: ID {role_id} by '{requester.username}'")
            return role
        except Exception as e:
            logger.error(f"Error updating role ID {role_id}: {str(e)}")
            raise e
    def delete_role(self, requester, role_id: int):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        try:
            role = self.repo.get_role_by_id(role_id)
            role_name = role.name if role else "Unknown"
            
            self.domain_service.delete_role(role_id)
            
            self.audit_service.record_log(
                user=requester,
                obj=None, # آبجکت حذف شده
                action='DELETE_ROLE',
                changes={'deleted_role_id': role_id, 'deleted_role_name': role_name},
                description=_(f"حذف نقش: {role_name}")
            )
            logger.info(f"Role deleted: ID {role_id} by '{requester.username}'")
        except Exception as e:
            logger.error(f"Error deleting role ID {role_id}: {str(e)}")
            raise e
    
    def bulk_delete(self, requester, role_ids: List[int]):
        AppPermissionChecker.check_has_permission(requester, 'delete_role')
        try:
            count = self.domain_service.bulk_delete_roles(role_ids)
            
            self.audit_service.record_log(
                user=requester,
                obj=None,
                action='BULK_DELETE_ROLE',
                changes={'count': count, 'ids': role_ids},
                description=_(f"حذف گروهی {count} نقش")
            )
            logger.info(f"Bulk role delete: {count} roles by '{requester.username}'")
            return count
        except Exception as e:
            logger.error(f"Error in bulk delete roles by '{requester.username}': {str(e)}")
            raise e
