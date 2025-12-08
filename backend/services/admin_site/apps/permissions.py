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
            
       
        # if not user.is_staff:
        #     raise PermissionDenied("شما دسترسی به پنل مدیریت را ندارید.")

        # 3. دریافت نقش کاربر
        # نکته: ما از related_name='user_role' استفاده می‌کنیم
        user_role_rel = user.user_role.select_related('role').first()
        
        if not user_role_rel:
            raise PermissionDenied("هیچ نقشی برای شما تعریف نشده است.")

        role = user_role_rel.role

        # 4. اصلاح باگ: اگر نقش دسترسی کامل دارد (Full Access)
        # در مدل Role فیلدی به نام is_super_role یا در JSON تعریف کردیم
        # اگر آن فیلد True باشد، نیازی به چک کردن پرمیشن نیست
        if getattr(role, 'is_super_role', False):
            return True

        # 5. چک کردن مجوز از روی جدول Role
        # ورودی معمولا 'app_label.codename' است (مثل core.view_order)
        # ما باید بخش codename را جدا کنیم
        if "." in permission_codename:
            codename = permission_codename.split(".")[1]
        else:
            codename = permission_codename

        has_perm = role.permission.filter(codename=codename).exists()
        
        if not has_perm:
            raise PermissionDenied(f"شما مجوز انجام این عملیات را ندارید: {permission_codename}")

        return True