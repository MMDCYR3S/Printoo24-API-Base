from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Permission

class AppPermissionChecker:
    """
    کلاس کمکی برای چک کردن دسترسی‌ها در لایه سرویس اپلیکیشن.
    """
    
    @staticmethod
    def check_has_permission(user, permission_codename: str):
        """
        بررسی می‌کند که آیا کاربر (بر اساس نقش خود) این مجوز را دارد؟
        مثال ورودی: 'core.add_user' یا 'view_order'
        """
        # 1. ابر کاربر همیشه دسترسی دارد
        if user.is_superuser:
            return True
            
        # 3. دریافت نقش کاربر
        user_role_rel = user.user_role.select_related('role').first()
        
        if not user_role_rel:
            raise PermissionDenied("هیچ نقشی برای شما تعریف نشده است.")

        role = user_role_rel.role

        # 4. اصلاح باگ: اگر نقش دسترسی کامل دارد (Full Access)
        if getattr(role, 'is_super_role', False):
            return True

        # 5. چک کردن مجوز از روی جدول Role
        if "." in permission_codename:
            codename = permission_codename.split(".")[1]
        else:
            codename = permission_codename

        has_perm = role.permission.filter(codename=codename).exists()
        
        if not has_perm:
            raise PermissionDenied(f"شما مجوز انجام این عملیات را ندارید: {permission_codename}")

        return True