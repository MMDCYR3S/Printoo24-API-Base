from typing import Dict, List, Any
from datetime import datetime
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q
from .base import BaseQuerySet

# ========== User QuerySet ========== #
class UserQuerySet(BaseQuerySet):
    """
    متدهای فیلتر و کوئری‌های زنجیره‌ای.
    """
    
    # ===== فیلترهای پایه ===== #
    def customers(self):
        """فیلتر کردن فقط مشتریان"""
        return self.filter(
            is_superuser=False, 
            is_staff=False,
            user_role__role__is_customer=True 
        )

    def staff(self):
        """فیلتر کردن فقط پرسنل"""
        return self.filter(user_role__role__is_customer=False)

    # ===== بهینه‌سازی کوئری‌ها (Eager Loading) ===== #
    def with_full_profile(self):
        """همراه با پروفایل و کیف پول (برای مشتریان)"""
        return self.select_related('customer_profile', 'wallet')

    def with_roles(self):
        """همراه با نقش‌ها و دسترسی‌ها (برای پرسنل)"""
        return self.prefetch_related('user_role__role', 'user_permissions')

    # ===== عملیات بالک (Bulk) ===== #
    def bulk_toggle_active(self, is_active: bool):
        return self.update(is_active=is_active)

# ========== User Manager ========== #
class UserManager(BaseUserManager):
    """
    مدیر مدل کاربر.
    """
    
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    # ===== متدهای دسترسی به QuerySet سفارشی ===== #
    def get_all_customers(self):
        """دریافت لیست کامل مشتریان با پرفورمنس بالا"""
        return self.get_queryset().customers().with_full_profile().order_by('-created_at')

    def get_all_staff(self):
        """دریافت لیست کارکنان"""
        return self.get_queryset().staff().with_roles().order_by('-created_at')

    def get_staff_detail(self, user_id: int):
        """دریافت جزئیات یک کارمند خاص"""
        return self.get_queryset().staff().with_roles().filter(id=user_id).first()

    # ===== ایجاد کاربر (Standard Django + Custom Logic) ===== #
    def create_user(self, username, password=None, email=None, **extra_fields):
        """
        ایجاد و ذخیره یک کاربر عادی
        """
        if not username:
            raise ValueError(_('نام کاربری الزامی است'))
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    def create_superuser(self, username, password=None, **extra_fields):
        """
        ایجاد و ذخیره یک سوپریوزر
        توجه: email اختیاریه و از extra_fields می‌گیریمش
        """
        email = extra_fields.pop('email', None)
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser باید is_staff=True باشد.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser باید is_superuser=True باشد.'))
        
        return self.create_user(username, password, email, **extra_fields)
    
    def get_by_natural_key(self, username):
        """
        بازیابی کاربر با username
        """
        return self.get(**{self.model.USERNAME_FIELD: username})
    # ===== داشبورد و آمار (Stats) ===== #
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        تجمیع تمام آمارهای داشبورد.
        """
        total_count = self.count()
        status_breakdown = self.aggregate(
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False)),
            staff_count=Count('id', filter=Q(is_staff=True)),
            customer_count=Count('id', filter=Q(is_staff=False, is_superuser=False))
        )
        
        return {
            "total": total_count,
            **status_breakdown
        }
    
    def get_all_customers(self):
        """دریافت لیست کامل مشتریان با پروفایل، کیف پول و آدرس‌ها"""
        return self.get_queryset().customers()\
                .with_full_profile()\
                .prefetch_related('addresses__province', 'addresses__city')\
                .distinct()\
                .order_by('-created_at')

    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        return self.filter(created_at__range=(start_date, end_date)).count()

    def get_role_breakdown(self) -> List[Dict[str, Any]]:
        from django.db.models import F
        return self.get_queryset().values(
            role_name=F('user_role__role__name'),
            role_slug=F('user_role__role__slug')
        ).annotate(count=Count('id')).order_by('-count')
