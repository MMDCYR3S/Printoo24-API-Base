from typing import Any, Dict, Optional, List
from datetime import datetime

from django.db.models import QuerySet, Count, Q

from core.utils import BaseRepository
from core.models import User, UserRole

# ====== User Repository ====== #
class UserRepository(BaseRepository[User]):
    """ ریپازیتوری مربوط به قوانین کاربران سیستم """
    
    def __init__(self):
        super().__init__(User)
    
    # ===== دریافت براساس شناسه ===== #
    def get_by_id(self, id: int) -> Optional[User]:
        """ دریافت یک کاربر با شناسه """
        return self.model.objects.filter(id=id).first()
        
    # ===== دریافت براساس نام کاربری ===== #
    def get_by_username(self, username: str) -> Optional[User]:
        """ دریافت کاربر با نام کاربری مشخص """
        return self.model.objects.filter(username=username).first()
    
    # ===== دریافت براساس ایمیل ===== #
    def get_by_email(self, email: str) -> Optional[User]:
        """ دریافت کاربر با ایمیل مشخص """
        return self.model.objects.filter(email=email).first()
    
    # ===== ایجاد کاربر ===== #
    def create_user(self, data: Dict[str, Any]) -> User:
        """
        ایجاد یک کاربر جدید با داده های مشخص شده
        """
        return self.model.objects.create_user(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            **{k: v for k, v in data.items() if k not in ['username', 'email', 'password']}
        )

    # ===== ذخیره کاربر ===== #
    def save(self, user: User) -> User:
        """ ذخیره کاربر """
        user.save()
        return user

    # ===== دریافت لیست مشتریان ===== #
    def get_all_customers(self) -> QuerySet[User]:
        """
        دریافت کاربرانی که پروفایل مشتری دارند یا نقش مشتری دارند.
        تحلیل‌گر: برای پرفورمنس، related_models را prefetch می‌کنیم.
        """
        return self.model.objects.filter(
            is_superuser=False, 
            is_staff=False,
            user_role__role__is_customer=True
        ).select_related('customer_profile', 'wallet').order_by('-created_at')

    # ===== عملیات بالک (دسته‌جمعی) ===== #
    def bulk_toggle_active(self, user_ids: list[int], is_active: bool) -> int:
        return self.model.objects.filter(id__in=user_ids).update(is_active=is_active)

    def bulk_delete(self, user_ids: list[int]) -> tuple:
        return self.model.objects.filter(id__in=user_ids).delete()

    # ========== بخش مربوط به سیستم مدیریت داخلی و ادمین ========== #
    def get_all_staff(self) -> QuerySet[User]:
        return self.model.objects.filter(user_role__role__is_customer=False)\
            .prefetch_related('user_role__role')\
            .order_by('-created_at')

    def get_staff_detail(self, user_id: int) -> Optional[User]:
        return self.model.objects.filter(id=user_id, user_role__role__is_customer=False)\
            .prefetch_related('user_role__role', 'user_permissions')\
            .first()
            
    def get_user_role(self, user: User) -> Optional[User]:
        return user.user_role.select_related('role').first()

    # ========================================= #
    # ======== Dashboard / Stats Methods ======= #
    # ========================================= #

    def get_total_count(self) -> int:
        """تعداد کل کاربران سیستم"""
        return self.model.objects.count()

    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """
        تعداد کاربران ثبت‌نام کرده در یک بازه زمانی خاص.
        کاربرد: محاسبه رشد ماهانه.
        """
        return self.model.objects.filter(created_at__range=(start_date, end_date)).count()

    def get_status_breakdown(self) -> Dict[str, int]:
        """
        تفکیک وضعیت فعال/غیرفعال کاربران.
        """
        return self.model.objects.aggregate(
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False))
        )

    def get_role_breakdown(self) -> List[Dict[str, Any]]:
        """
        تفکیک کاربران بر اساس نقش (Role).
        نکته: از مدل UserRole برای شمارش استفاده می‌کنیم.
        خروجی: [{'role__name': 'Admin', 'count': 5}, ...]
        """
        # ما می‌خواهیم بدانیم از هر نقش چند کاربر داریم
        return UserRole.objects.values('role__name', 'role__slug') \
            .annotate(count=Count('user_id')) \
            .order_by('-count')

    def get_customer_vs_staff_count(self) -> Dict[str, int]:
        """
        مقایسه تعداد پرسنل و مشتریان
        """
        return self.model.objects.aggregate(
            staff_count=Count('id', filter=Q(is_staff=True)),
            customer_count=Count('id', filter=Q(is_staff=False, is_superuser=False))
        )
