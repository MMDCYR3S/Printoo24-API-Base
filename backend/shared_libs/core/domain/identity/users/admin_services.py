from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q

from core.models import User, UserRole
from .repositories import UserRepository
from ..roles.repositories import RoleRepository 
from .exceptions import UsernameAlreadyExistsException, EmailAlreadyExistsException

class UserAdminDomainService:
    """
    سرویس جامع مدیریت کارکنان و عملیات گروهی مربوط به آن‌ها.
    """
    def __init__(self):
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    # ========================================== #
    # ====== Single Staff Management =========== #
    # ========================================== #
    
    @transaction.atomic
    def create_staff(self, data: Dict[str, Any], role_id: int) -> User:
        """ استخدام کارمند جدید """
        # 1. بررسی یکتایی
        if self.user_repo.get_by_email(data.get('email')):
            raise EmailAlreadyExistsException("این ایمیل قبلا ثبت شده است.")
        if self.user_repo.get_by_username(data.get('username')):
            raise UsernameAlreadyExistsException("این نام کاربری قبلا ثبت شده است.")

        # 2. بررسی نقش
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise ValidationError("نقش انتخاب شده نامعتبر است.")

        # 3. آماده‌سازی داده‌ها
        user_data = data.copy()
        user_data['is_staff'] = True   # دسترسی به پنل
        user_data['is_active'] = True  # فعال بودن پیش‌فرض
        
        # 4. ایجاد کاربر
        user = self.user_repo.create_user(user_data)

        # 5. انتساب نقش
        UserRole.objects.create(user=user, role=role)

        return user

    @transaction.atomic
    def update_staff(self, user_id: int, data: Dict[str, Any], role_id: int = None) -> User:
        """ ویرایش کارمند """
        user = self.user_repo.get_staff_detail(user_id)
        if not user:
            raise ValidationError("کارمند یافت نشد.")

        # ===== اعتبارسنجی و بررسی تکراری بودن نام کاربری ===== #
        if 'username' in data and data['username'] != user.username:
            if self.user_repo.get_by_username(data['username']):
                raise UsernameAlreadyExistsException("نام کاربری تکراری است.")

        # ===== ویرایش اطلاعات پایه ===== #
        clean_data = {k: v for k, v in data.items() if k not in ['password', 'email']}
        self.user_repo.update(user, clean_data)

        # ==== تغییر نقش در صورت وجود ===== #
        if role_id:
            current_role_rel = user.user_role.first()
            # ===== در صورت نبود نقش ===== #
            if not current_role_rel or current_role_rel.role_id != role_id:
                new_role = self.role_repo.get_by_id(role_id)
                if not new_role:
                    raise ValidationError("نقش نامعتبر است.")
                
                # ===== حذف نقش قبلی ===== #
                UserRole.objects.filter(user=user).delete()
                UserRole.objects.create(user=user, role=new_role)
                
        return user

    def delete_single_staff(self, user_id: int):
        """ حذف تکی با بررسی ایمنی """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("کاربر یافت نشد.")
        
        if user.is_superuser:
            raise ValidationError("امکان حذف مدیر کل سیستم (Superuser) وجود ندارد.")
            
        user.delete()

    # ========================================== #
    # ====== Bulk Operations (Staff) =========== #
    # ========================================== #

    @transaction.atomic
    def bulk_delete_staff(self, user_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی کارکنان.
        مدیران کل (Superusers) از لیست حذف فیلتر می‌شوند.
        """
        # ===== جدا کردن مدیران کل از کارکنان برای حذف ===== #
        safe_users = self.user_repo.model.objects.filter(id__in=user_ids, is_superuser=False, is_staff=True)
        count = safe_users.count()
        safe_users.delete()
        
        return {"deleted": count, "requested": len(user_ids)}

    @transaction.atomic
    def bulk_toggle_active_status(self, user_ids: List[int], is_active: bool) -> int:
        """
        فعال/غیرفعال کردن گروهی کارکنان (مثلا تعلیق گروهی).
        نکته: مدیر کل را نمی‌توان غیرفعال کرد.
        """
        query = self.user_repo.model.objects.filter(id__in=user_ids, is_staff=True)
        
        if not is_active:
            # ===== ابرکاربران نمیتوانند غیر فعال شوند ===== #
            query = query.exclude(is_superuser=True)
            
        updated_count = query.update(is_active=is_active)
        return updated_count

    @transaction.atomic
    def bulk_change_role(self, user_ids: List[int], new_role_id: int) -> int:
        """
        تغییر نقش گروهی (مثلا انتقال ۵ نفر از انبار به QC).
        """
        role = self.role_repo.get_by_id(new_role_id)
        if not role:
            raise ValidationError("نقش مقصد نامعتبر است.")

        # ===== پیدا کردن کارکنان معتبر ===== #
        target_users = self.user_repo.model.objects.filter(
            Q(id__in=user_ids) | 
            Q(is_staff=True) |
            Q(is_superuser=False) |
            Q(user_role__role__is_customer=True)
        )
        valid_user_ids = list(target_users.values_list('id', flat=True))

        if not valid_user_ids:
            return 0

        # ===== حذف نقش های قبلی کارکنان ===== #
        UserRole.objects.filter(user_id__in=valid_user_ids).delete()

        # ===== ایجاد ارتباطات جدید ===== #
        new_relations = [
            UserRole(user_id=uid, role=role) for uid in valid_user_ids
        ]
        UserRole.objects.bulk_create(new_relations)

        return len(new_relations)
