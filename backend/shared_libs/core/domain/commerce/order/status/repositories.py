from typing import Optional
from django.db.models import QuerySet, Count
from core.utils.base_repository import BaseRepository
from core.models import Order, OrderStatus, OrderStatusGroup

class StatusFlowRepository(BaseRepository[OrderStatus]):
    """
    ریپازیتوری اختصاصی برای مدیریت Status و StateLog.
    """
    def __init__(self):
        super().__init__(OrderStatus)

    def get_status_by_code(self, internal_code: str) -> Optional[OrderStatus]:
        """
        دریافت آبجکت وضعیت بر اساس کد سیستمی (برای امنیت کدنویسی).
        """
        return self.model.objects.filter(internal_code=internal_code).first()
    
class OrderStatusGroupRepository(BaseRepository[OrderStatusGroup]):
    """
    ریپازیتوری مدیریت گروه وضعیت (CRUD).
    """
    def __init__(self):
        super().__init__(OrderStatusGroup)

    def get_group_by_code(self, code: str) -> Optional[OrderStatusGroup]:
        """ دریافت گروه وضعیت بر اساس کد سیستمی. """
        return self.model.objects.filter(code=code).first()

    def get_all_groups_with_status_count(self) -> QuerySet[OrderStatusGroup]:
        """ دریافت تمام گروه‌ها با تعداد وضعیت‌های مرتبط (برای نمایش در لیست). """
        return self.model.objects.annotate(
            status_count=Count('order_status')
        ).order_by('id')
    
# ========== Order Status Repository ========== #
class OrderStatusRepository(BaseRepository[OrderStatus]):
    """
    ریپازیتوری مدیریت مدل OrderStatus.
    """
    def __init__(self):
        super().__init__(OrderStatus)

    def get_status_by_code(self, internal_code: str) -> Optional[OrderStatus]:
        """ دریافت وضعیت بر اساس کد سیستمی (برای چک کردن یکتایی). """
        return self.model.objects.filter(internal_code=internal_code).first()

    def get_status_with_group_detail(self, status_id: int) -> Optional[OrderStatus]:
        """ دریافت وضعیت همراه با جزئیات گروه آن. """
        return self.model.objects.select_related('group').filter(id=status_id).first()

    def get_all_statuses_with_details(self) -> QuerySet[OrderStatus]:
        """ دریافت تمام وضعیت‌ها همراه با نام گروه. """
        return self.model.objects.select_related('group').order_by('id')

    def check_for_active_orders(self, status: OrderStatus) -> bool:
        """ بررسی می‌کند که آیا سفارشی در حال حاضر از این وضعیت استفاده می‌کند؟ """
        # Order.current_status از on_delete=PROTECT استفاده می‌کند.
        return Order.objects.filter(current_status=status).exists()
    