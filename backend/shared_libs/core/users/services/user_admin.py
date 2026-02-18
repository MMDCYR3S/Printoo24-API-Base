from typing import Dict, Any, List
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from core.users.models import User, UserRole, Role
from core.users.exceptions import (
    EmailAlreadyExistsException, 
    UsernameAlreadyExistsException
)

# ========== ADMIN SERVICE ========== #
class UserAdminService:
    """
    سرویس دامنه مدیریت داخلی (Internal Admin).
    """

    # ========== CREATE ========== #
    @transaction.atomic
    def create_staff(self, data: Dict[str, Any], role_id: int) -> User:
        """استخدام کارمند جدید"""
        # ===== اعتبارسنجی ===== #
        if User.objects.filter(email=data.get('email')).exists():
            raise EmailAlreadyExistsException("این ایمیل قبلا ثبت شده است.")
        if User.objects.filter(username=data.get('username')).exists():
            raise UsernameAlreadyExistsException("نام کاربری تکراری است.")

        # ===== اعتبارسنجی ===== #
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ValidationError("نقش انتخاب شده نامعتبر است.")

        # ===== ایجاد کاربر===== #
        user = User.objects.create_user(
            username=data['username'],
            email=data.get("email", None),
            password=data.get('password'),
            is_staff=True,
            is_active=True
        )

        # ===== ایجاد نقش ===== #
        UserRole.objects.create(user=user, role=role)
        return user

    # ========== UPDATE ========== #
    @transaction.atomic
    def update_staff(self, user_id: int, data: Dict[str, Any], role_id: int = None) -> User:
        """ویرایش اطلاعات کارمند و نقش او"""
        try:
            user = User.objects.get_staff_detail(user_id)
            if not user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            raise ValidationError("کارمند یافت نشد.")

        # ===== اعتبارسنجی نام کاربری ===== #
        if 'username' in data and data['username'] != user.username:
            if User.objects.filter(username=data['username']).exists():
                raise UsernameAlreadyExistsException("نام کاربری تکراری است.")

        # ===== مدیریت رمز عبور (Crucial Step) ===== #
        password = data.pop('password', None)
        if password:
            user.set_password(password)

        # ===== ویرایش فیلدهای مجاز مدل User ===== #
        allowed_fields = ['username', 'email', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()

        # ===== ویرایش نقش (بهینه‌سازی شده) ===== #
        if role_id:
            current_role_rel = user.user_role.first()
            if not current_role_rel or current_role_rel.role_id != role_id:
                if not Role.objects.filter(id=role_id).exists():
                     raise ValidationError("نقش نامعتبر است.")

                user.user_role.all().delete()
                UserRole.objects.create(user=user, role_id=role_id)

        return user

    # ========== DELETE ========== #
    def delete_staff(self, user_id: int):
        """حذف کارمند با ایمنی"""
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise ValidationError("کاربر یافت نشد.")
        if user.is_superuser:
            raise ValidationError("حذف سوپریوزر ممکن نیست.")
        user.delete()

    # ========== BULK ACTIONS - CHANGE ROLE ========== #
    @transaction.atomic
    def bulk_change_role(self, user_ids: List[int], new_role_id: int) -> int:
        """
        تغییر نقش گروهی.
        منطق دقیقاً طبق کد قبلی حفظ شده است.
        """
        if not Role.objects.filter(id=new_role_id).exists():
            raise ValidationError("نقش مقصد نامعتبر است.")
        # ===== اعتبارسنجی ===== #
        target_users_qs = User.objects.filter(
            Q(id__in=user_ids) & 
            (Q(is_staff=True) | Q(is_superuser=False) | Q(user_role__role__is_customer=True))
        )
        
        valid_user_ids = list(target_users_qs.values_list('id', flat=True))
        
        if not valid_user_ids:
            return 0

        # ===== حذف نقش‌های قبلی ===== #
        UserRole.objects.filter(user_id__in=valid_user_ids).delete()

        # ===== ایجاد نقش جدید ===== #
        new_relations = [
            UserRole(user_id=uid, role_id=new_role_id) 
            for uid in valid_user_ids
        ]
        UserRole.objects.bulk_create(new_relations)

        return len(new_relations)
    
    # ========== BULK ACTIONS - TOGGLE ACTIVE ========== #
    def bulk_toggle_active(self, user_ids: List[int], is_active: bool) -> int:
        """فعال/غیرفعال سازی گروهی"""
        qs = User.objects.filter(id__in=user_ids)
        if not is_active:
            qs = qs.exclude(is_superuser=True)
        return qs.update(is_active=is_active)

    @transaction.atomic
    def bulk_delete_staff(self, user_ids: List[int]) -> Dict[str, int]:
        users = User.objects.filter(id__in=user_ids)
        # ===== کارکنانی که ابرکاربر نیستند ===== #
        deletable_users = users.exclude(is_superuser=True)
        count = deletable_users.count()
        deletable_users.delete()
        return {'deleted': count}
