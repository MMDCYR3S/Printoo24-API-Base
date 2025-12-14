from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

from core.domain.commerce.order import OrderRepository
from core.models import User

# ========== Order Detail App Service ========== # 
class OrderDetailAppService:
    """
    سرویس اپلیکیشن برای دیدن جزئیات کامل یک سفارش براساس نقش
    """
    def __init__(self):
        self.repo = OrderRepository()

    def get_order_detail(self, requester: User, order_id: int):
        """
        مشاهده جزئیات براساس نقش و مجوزهای دسترسی
        """
        # ===== دریافت جزئیات کامل سفارش (از کوئری ریپازیتوری قبلاً اصلاح شده) ===== #
        order = self.repo.get_full_order_detail_for_admin(order_id)
        if not order:
            raise ValueError("سفارش یافت نشد.")
        
        # ===== 1. دریافت نقش کاربر و چک‌های اولیه ===== #
        if requester.is_superuser:
            return order, 'superuser'
        # ===== یافتن نقش و بررسی وجود آین ===== #
        user_role_rel = requester.user_role.select_related('role').first()
        if not user_role_rel:
            raise PermissionDenied("شما نقشی ندارید.")
        
        role = user_role_rel.role
         
        # ===== بررسی وجود گروه وضعیتی ===== #
        allowed_groups = role.allowed_status_groups
        if not allowed_groups:
             raise PermissionDenied("گروه وضعیتی برای شما تعریف نشده است.")
         
         # ===== بررسی دسترسی مدیریتی ===== #
        is_global_access = order.current_status.group.code in allowed_groups
        
        if not (is_global_access):
             raise PermissionDenied("شما دسترسی به مشاهده این سفارش در وضعیت فعلی را ندارید.")

        # ===== 5. بازگشت نتیجه =====
        return order, role.slug
