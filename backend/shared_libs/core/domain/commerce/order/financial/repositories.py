from typing import List, Optional
from django.db.models import QuerySet
from core.utils.base_repository import BaseRepository
from core.models import (
    OrderCostReport, 
    OrderCostItem, 
    OrderCostCatalog, 
    OrderCostType
)

# ===== 1. Repository for Cost Reports (Header) ===== #
class OrderCostReportRepository(BaseRepository[OrderCostReport]):
    def __init__(self):
        super().__init__(OrderCostReport)

    def get_reports_by_order(self, order_id: int) -> QuerySet[OrderCostReport]:
        """ دریافت تمام گزارش‌های یک سفارش با جزئیات اقلام """
        return self.model.objects.filter(order_id=order_id)\
            .select_related('created_by')\
            .prefetch_related('items__catalog_item', 'items__cost_type')\
            .order_by('-created_at')

# ===== 2. Repository for Cost Items (Details) ===== #
class OrderCostItemRepository(BaseRepository[OrderCostItem]):
    def __init__(self):
        super().__init__(OrderCostItem)
        
    def bulk_create_items(self, items: List[OrderCostItem]):
        """ ثبت گروهی اقلام برای جلوگیری از فشار به دیتابیس """
        return self.model.objects.bulk_create(items)

# ===== 3. Repository for Cost Catalog (Master Data) ===== #
class OrderCostCatalogRepository(BaseRepository[OrderCostCatalog]):
    def __init__(self):
        super().__init__(OrderCostCatalog)

    def get_active_items_by_type(self, cost_type_id: int = None) -> QuerySet[OrderCostCatalog]:
        """ دریافت لیست کالا/خدمات فعال (برای دراپ‌دان فرانت) """
        qs = self.model.objects.filter(is_active=True)
        if cost_type_id:
            qs = qs.filter(cost_type_id=cost_type_id)
        return qs

# ===== 4. Repository for Cost Types ===== #
class OrderCostTypeRepository(BaseRepository[OrderCostType]):
    def __init__(self):
        super().__init__(OrderCostType)