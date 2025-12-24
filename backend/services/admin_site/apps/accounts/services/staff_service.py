import logging
from typing import Dict, List, Any

from django.utils.translation import gettext as _

from core.models import User
from core.users.services import UserAdminService
from core.logger.services import LoggerService
from apps.permissions import AppPermissionChecker

# ===== Logger Initialization ===== #
logger = logging.getLogger('apps.users.services.staff_app_service')

# ===== Staff App Service ===== # 
class StaffAppService:
    def __init__(self):
        # ===== اتصال به سرویس ===== #
        self.domain_service = UserAdminService()
        self.audit_service = LoggerService()

    def get_staff_list(self, requester):
        """ مشاهده لیست کارکنان """
        AppPermissionChecker.check_has_permission(requester, 'view_user')
        return User.objects.get_all_staff()

    def create_staff(self, requester, data: Dict[str, Any]):
        """ ایجاد کارمند جدید """
        AppPermissionChecker.check_has_permission(requester, 'add_user')
        # ===== دریافت شناسه نقش ===== #
        try:
            role_id = data.pop('role_id')
            user = self.domain_service.create_staff(data, role_id)
            
            self.audit_service.record_log(
                user=requester,
                obj=user,
                action='CREATE_STAFF',
                changes={'username': user.username, 'role_id': role_id},
                description=_(f"ایجاد کارمند جدید: {user.username}")
            )
            logger.info(f"Staff created: '{user.username}' by Admin '{requester.username}'")
            return user
        except Exception as e:
            logger.error(f"Error creating staff by '{requester.username}': {str(e)}")
            raise e

    def update_staff(self, requester, user_id: int, data: Dict[str, Any]):
        """ ویرایش کارمند """
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        
        role_id = data.pop('role_id', None)
        try:
            user = self.domain_service.update_staff(user_id, data, role_id)
            
            changes_log = {'updated_fields': list(data.keys())}
            if role_id:
                changes_log['new_role_id'] = role_id
                
            self.audit_service.record_log(
                user=requester,
                obj=user,
                action='UPDATE_STAFF',
                changes=changes_log,
                description=_(f"ویرایش اطلاعات کارمند: {user.username}")
            )
            
            logger.info(f"Staff updated: ID {user_id} by Admin '{requester.username}'")
            return user
        except Exception as e:
            logger.error(f"Error updating staff ID {user_id}: {str(e)}")
            raise e

    def delete_staff(self, requester, user_id: int):
        """ حذف کارمند """
        AppPermissionChecker.check_has_permission(requester, 'delete_user')
        try:
            target_user = User.objects.filter(id=user_id).first()
            target_username = target_user.username if target_user else "Unknown"
            
            self.domain_service.delete_single_staff(user_id)
            
            self.audit_service.record_log(
                user=requester,
                obj=None,
                action='DELETE_STAFF',
                changes={'deleted_user_id': user_id, 'username': target_username},
                description=_(f"حذف کارمند: {target_username}")
            )
            
            logger.info(f"Staff deleted: ID {user_id} by Admin '{requester.username}'")
        except Exception as e:
            logger.error(f"Error deleting staff ID {user_id}: {str(e)}")
            raise e

    # ===== عملیات گروهی (Bulk Actions) ===== #
    
    def bulk_delete(self, requester, user_ids: List[int]):
        AppPermissionChecker.check_has_permission(requester, 'delete_user')
        res = self.domain_service.bulk_delete_staff(user_ids)
        
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='BULK_DELETE_STAFF',
            changes={'count': res.get('deleted', 0), 'ids': user_ids},
            description=_("حذف گروهی کارکنان")
        )
        
        logger.info(f"Bulk staff delete: {res['deleted']} users by '{requester.username}'")
        return res

    def bulk_toggle_active(self, requester, user_ids: List[int], is_active: bool):
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        count = self.domain_service.bulk_toggle_active_status(user_ids, is_active)
        action = "activated" if is_active else "deactivated"
        
        action_name = "ACTIVATE_STAFF" if is_active else "DEACTIVATE_STAFF"
        action_desc = "فعال‌سازی" if is_active else "غیرفعال‌سازی"
        
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action=action_name,
            changes={'count': count, 'ids': user_ids, 'new_status': is_active},
            description=_(f"{action_desc} گروهی کارکنان")
        )
        
        logger.info(f"Bulk staff {action}: {count} users by '{requester.username}'")
        return count
    
    def bulk_change_role(self, requester, user_ids: List[int], new_role_id: int):
        AppPermissionChecker.check_has_permission(requester, 'change_user')
        count = self.domain_service.bulk_change_role(user_ids, new_role_id)
        
        self.audit_service.record_log(
            user=requester,
            obj=None,
            action='BULK_ROLE_CHANGE',
            changes={'count': count, 'ids': user_ids, 'new_role_id': new_role_id},
            description=_("تغییر گروهی نقش کارکنان")
        )
        
        logger.info(f"Bulk role change: {count} users -> Role ID {new_role_id} by '{requester.username}'")
        return count
