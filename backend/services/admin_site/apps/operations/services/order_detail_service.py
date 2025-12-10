from rest_framework.exceptions import PermissionDenied

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
        # ===== دریافت جزئیات کامل سفارش ===== #
        order = self.repo.get_full_order_detail_for_admin(order_id)
        if not order:
            raise ValueError("سفارش یافت نشد.")

        # ===== چک کردن دسترسی کلی ===== #
        user_role = requester.user_role.first()
        if not user_role:
            raise PermissionDenied("شما نقشی ندارید.")
            
        role = user_role.role
        
        # ===== اگر ادمین نیست، محدوده دید را بررسی کن ===== #
        if not (requester.is_superuser or role.is_admin):
            allowed_groups = role.allowed_status_groups
            if order.current_status.group.code not in allowed_groups:
                raise PermissionDenied("شما دسترسی به مشاهده این سفارش در وضعیت فعلی را ندارید.")

            # ===== بررسی دسترسی به سفارش ===== #
            if role.slug == 'designer':
                has_accessed = False
                for item in order.order_item_order.all():
                    if item.assigned_to_id == requester.id or item.assigned_to_id is None:
                        has_accessed = True
                        break
                if not has_accessed:
                    raise PermissionDenied("این سفارش به همکاران دیگر اختصاص دارد و آیتم آزادی برای شما ندارد.")
                
                is_assigned = order.order_item_order.filter(assigned_to=requester).exists()
                if not is_assigned:
                     raise PermissionDenied("این سفارش به طراح دیگری اختصاص دارد.")

        return order, role.slug
