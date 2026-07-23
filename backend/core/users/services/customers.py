from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import User, CustomerProfile, UserRole, Role

class CustomerService:
    """
    سرویس مدیریت مشتریان (توسط ادمین یا سیستم).
    این سرویس وظیفه دارد کاربر، پروفایل، نقش و کیف پول را به صورت یکپارچه مدیریت کند.
    """

    def get_by_id(self, user_id: int):
        return User.objects.get(pk=user_id)

    def get_all_customers(self):
        """دریافت لیست تمام مشتریان (Read Operation)"""
        return User.objects.get_all_customers()
    
    def get_all_customers_admin(self):
        """دریافت لیست تمام مشتریان (Read Operation)"""
        return User.objects.get_all_customers_admin()

    def get_customer_by_id(self, user_id: int) -> User:
        """دریافت یک مشتری خاص"""
        user = User.objects.filter(pk=user_id).with_full_profile().first()
        if not user:
            raise ValidationError("مشتری یافت نشد.")
        return user
    
    def get_customer_by_id_admin(self, user_id: int) -> User:
        """دریافت یک مشتری خاص"""
        user = User.objects.filter(pk=user_id).with_full_profile_admin().first()
        if not user:
            raise ValidationError("مشتری یافت نشد.")
        return user

    @transaction.atomic
    def create_customer(self, data: Dict[str, Any]) -> User:
        """
        ایجاد یک مشتری (یا مدیر/کارمند) جدید.
        """
        # ===== دریافت کاربر ===== #
        phone_number = data.get('phone_number')
        password = data.get('password')

        # ===== ایجاد یوزر ===== #
        # اضافه شدن فیلدهای دسترسی به متد ساخت
        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            is_active=data.get('is_active', True),
            is_staff=data.get('is_staff', False),
            is_superuser=data.get('is_superuser', False),
            is_verified=data.get('is_verified', False)
        )

        # ===== ایجاد پروفایل ===== #
        profile_data = {
            'user': user,
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'company': data.get('company', ''),
            'bio': data.get('bio', '')
        }
        CustomerProfile.objects.create(**profile_data)

        # ===== تخصیص نقش ===== #
        try:
            customer_role = Role.objects.get(slug='normal')
        except Role.DoesNotExist:
            customer_role = Role.objects.create(name="مشتری", slug="normal", type="normal", is_customer=True)
            
        UserRole.objects.create(user=user, role=customer_role)

        return user

    @transaction.atomic
    def update_customer(self, user_id: int, data: Dict[str, Any]) -> User:
        user = self.get_customer_by_id_admin(user_id)
        profile = getattr(user, 'customer_profile', None)

        # ===== فیلدهای مورد نیاز جهت دریافت از api ===== #
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
            
        # ===== اضافه شدن فیلدهای دسترسی در هنگام ویرایش ===== #
        if 'is_staff' in data:
            user.is_staff = data['is_staff']
        if 'is_superuser' in data:
            user.is_superuser = data['is_superuser']
        # =================================================== #
        
        if data.get('password'):
            user.set_password(data['password'])
        user.save()

        if profile:
            for field in ('first_name', 'last_name', 'company', 'bio'):
                if field in data:
                    setattr(profile, field, data[field])
            profile.save()

        return user


    @transaction.atomic
    def delete_customer(self, user_id: int):
        """
        حذف مشتری.
        """
        user = self.get_customer_by_id(user_id)
        user.delete()

    # ================= Bulk Actions ================= #

    @transaction.atomic
    def bulk_toggle_active(self, user_ids: List[int], is_active: bool) -> int:
        """
        تغییر وضعیت فعال/غیرفعال گروهی مشتریان.
        نکته امنیتی: از فیلتر .customers() استفاده می‌کنیم تا مطمئن شویم
        هیچ ادمین یا کارمندی به اشتباه تغییر وضعیت ندهد.
        """
        # ===== دریافت کوئری‌ست فقط شامل مشتریان===== #
        customers_queryset = User.objects.customers().filter(id__in=user_ids)
        
        # ===== تغییر وضعیت ===== #
        updated_count = customers_queryset.bulk_toggle_active(is_active)
        
        return updated_count

    @transaction.atomic
    def bulk_delete_customers(self, user_ids: List[int]) -> int:
        """
        حذف گروهی مشتریان.
        فقط مشتریانی که ID آنها در لیست است و واقعاً مشتری هستند حذف می‌شوند.
        """
        # ===== دریافت کوئری‌ست فقط شامل مشتریان===== # 
        customers_queryset = User.objects.customers().filter(id__in=user_ids)
        
        # ===== حذف ===== #
        deleted_count, _ = customers_queryset.delete()
        
        return deleted_count
