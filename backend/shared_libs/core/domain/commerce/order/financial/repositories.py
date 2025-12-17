from typing import List, Optional
from django.db.models import QuerySet
from core.utils.base_repository import BaseRepository
from core.models import (
    OrderCostSheet, OrderCostReport, OrderCostItem, 
    OrderCostCategory, OrderCostAttachment
)

# ===== 1. Repository for Cost Sheet (Ledger) ===== #
class OrderCostSheetRepository(BaseRepository[OrderCostSheet]):
    def __init__(self):
        super().__init__(OrderCostSheet)

    def get_by_order_id(self, order_id: int) -> Optional[OrderCostSheet]:
        """ دریافت شیت (فقط اعداد نهایی) """
        return self.model.objects.filter(order_id=order_id).first()

# ===== 2. Repository for Cost Reports (Journal) ===== #
class OrderCostReportRepository(BaseRepository[OrderCostReport]):
    def __init__(self):
        super().__init__(OrderCostReport)
        
    def get_reports_by_sheet(self, sheet_id: int) -> QuerySet[OrderCostReport]:
        return self.model.objects.filter(sheet_id=sheet_id)\
            .select_related('submitter')\
            .order_by('-created_at')
            
    def get_report_detail(self, report_id: int) -> Optional[OrderCostReport]:
        return self.model.objects.filter(id=report_id)\
            .select_related('sheet__order', 'submitter')\
            .prefetch_related('items__catalog_item', 'attachments')\
            .first()

# ===== 3. Repository for Cost Items ===== #
class OrderCostItemRepository(BaseRepository[OrderCostItem]):
    def __init__(self):
        super().__init__(OrderCostItem)
    
    def bulk_create_items(self, items: List[OrderCostItem]):
        return self.model.objects.bulk_create(items)
        
    def get_items_by_report(self, report_id: int) -> QuerySet[OrderCostItem]:
        return self.model.objects.filter(report_id=report_id)

# ===== 4. Repository for Attachments ===== #
class OrderCostAttachmentRepository(BaseRepository[OrderCostAttachment]):
    def __init__(self):
        super().__init__(OrderCostAttachment)
        
    def bulk_create_attachments(self, attachments: List[OrderCostAttachment]):
        return self.model.objects.bulk_create(attachments)

# ===== 5. Repository for Categories (Master Data) ===== #
class OrderCostCategoryRepository(BaseRepository[OrderCostCategory]):
    def __init__(self):
        super().__init__(OrderCostCategory)

    def get_all_active(self) -> QuerySet[OrderCostCategory]:
        return self.model.objects.all().order_by('title')
        
    def get_by_slug(self, slug: str) -> Optional[OrderCostCategory]:
        return self.model.objects.filter(slug=slug).first()
