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
        user_role_rel = requester.user_role.select_related('role').first()
        if requester.is_superuser:
            return order, 'superuser'
        if not user_role_rel:
            raise PermissionDenied("شما نقشی ندارید.")
        
        role = user_role_rel.role
        
        if getattr(role, 'can_view_all_orders', False):
            return order, role.slug
         
        allowed_groups = role.allowed_status_groups
        if not allowed_groups:
             raise PermissionDenied("گروه وضعیتی برای شما تعریف نشده است.")
         
         # ===== 2. بررسی دسترسی مدیریتی (Global Access) ===== #
        is_global_access = order.current_status.group.code in allowed_groups
        
        is_order_item_access = order.order_item_order.filter(status__group__code__in=allowed_groups).exists()
        
        # ===== 3. بررسی دسترسی وظیفه‌محور (Task-Based Access) =====
        has_task_access = False
        
        if role.is_task_based:
            task_items_filter = Q(status__group__code__in=allowed_groups)
            assignment_filter = Q(assigned_to=requester) | Q(assigned_to__isnull=True)
            has_task_access = order.order_item_order.filter(
                task_items_filter & assignment_filter
            ).exists()

        if not (is_global_access or has_task_access or is_order_item_access):
            if role.is_task_based:
                raise PermissionDenied("این سفارش به همکار دیگری اختصاص دارد یا آیتمی در حوزه کاری شما ندارد.")
            else:
                raise PermissionDenied("شما دسترسی به مشاهده این سفارش در وضعیت فعلی را ندارید.")

        # ===== 5. بازگشت نتیجه =====
        return order, role.slug
