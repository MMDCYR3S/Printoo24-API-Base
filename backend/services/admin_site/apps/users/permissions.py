from rest_framework.exceptions import PermissionDenied

# ===== App Permission Checker ===== #
class AppPermissionChecker:
    """
    کلاس کمکی برای چک کردن دسترسی‌ها در لایه سرویس اپلیکیشن.
    """
    
    @staticmethod
    def check_has_permission(user, permission_codename: str):
        """
        بررسی می‌کند که آیا کاربر (بر اساس نقش خود) این مجوز را دارد؟
        مثال: check_has_permission(user, 'core.add_user')
        """
        # ===== ابر کاربر همیشه دسترسی دارد ===== #
        if user.is_superuser:
            return True
            
        # ===== آیا کاربر نقش کارمندی دارد ===== #
        if not user.is_staff or not hasattr(user, 'user_role'):
            raise PermissionDenied("شما دسترسی به پنل مدیریت را ندارید.")

        # ===== چک کردن مجوزها ===== #
        full_perm_code = f"core.{permission_codename}"
        
        if not user.has_perm(full_perm_code):
            raise PermissionDenied(f"شما مجوز انجام این عملیات را ندارید: {permission_codename}")