from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Count

from core.models import Role
from .repositories import RoleRepository

class RoleAdminDomainService:
    """
    سرویس مدیریت نقش‌ها و دسترسی‌ها.
    """
    def __init__(self):
        self.role_repo = RoleRepository()

    # ========== Single Role Management ========== #
    @transaction.atomic
    def create_role(self, data: Dict[str, Any], permission_ids: List[int] = None, scope_ids: List[int] = None) -> Role:
        """ ایجاد نقش جدید """
        # ===== بررسی کد تکراری ===== #
        if self.role_repo.get_role_by_code(data.get('code')):
            raise ValidationError("نقشی با این کد سیستمی وجود دارد.")
        
        role = self.role_repo.create_role(data)
        
        if permission_ids:
            self.role_repo.update_permissions(role, permission_ids)
            
        if scope_ids:
            role.scopes.set(scope_ids)
            
        return role

    @transaction.atomic
    def update_role(self, role_id: int, data: Dict[str, Any], permission_ids: List[int] = None, scope_ids: List[int] = None) -> Role:
        """ ویرایش نقش """
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValidationError("نقش یافت نشد.")
        
        if 'slug' in data and data['slug'] != role.slug:
             if self.role_repo.get_role_by_slug(data['slug']):
                raise ValidationError("کد سیستمی تکراری است.")

        self.role_repo.update(role, data)
        
        if permission_ids is not None:
            self.role_repo.update_permissions(role, permission_ids)
            
        if scope_ids is not None:
            role.scopes.set(scope_ids)
            
        return role

    def delete_single_role(self, role_id: int):
        """ حذف یک نقش با بررسی وابستگی """
        role = self.role_repo.get_by_id(role_id)
        if not role:
             raise ValidationError("نقش یافت نشد.")
        self._check_role_deletion_safety([role])
        role.delete()

    # ========== Bulk Operations (Roles) ========== #
    @transaction.atomic
    def bulk_delete_roles(self, role_ids: List[int]) -> int:
        """
        حذف گروهی نقش‌ها.
        قبل از حذف چک می‌کند که آیا کاربری به این نقش‌ها متصل است یا خیر.
        """
        roles = self.role_repo.model.objects.filter(id__in=role_ids)
        
        # ===== بررسی ایمنی حذف نقش جمعی ===== #
        self._check_role_deletion_safety(roles)
        
        # ===== حذف ===== #
        deleted_count, _ = roles.delete()
        return deleted_count

    # ========== Helper Methods ========== #
    def _check_role_deletion_safety(self, roles):
        """
        بررسی قوانین بیزینسی قبل از حذف نقش.
        1. نقش‌های سیستمی (مثل Super Admin) حذف نشوند.
        2. نقش‌هایی که کاربر فعال دارند حذف نشوند.
        """
        system_codes = ['admin_internal', 'super_admin', 'customer']
        
        for role in roles:
            # ===== قانون اول: نقش سیستمی ===== #
            if role.code in system_codes:
                raise ValidationError(f"نقش '{role.name}' سیستمی است و قابل حذف نیست.")
            
            # ===== قانون دوم: کاربرهای متصل به نقش ===== #
            if role.role_user.exists():
                user_count = role.role_user.count()
                raise ValidationError(
                    f"نقش '{role.name}' به {user_count} کاربر اختصاص داده شده است. ابتدا نقش آن‌ها را تغییر دهید."
                )
