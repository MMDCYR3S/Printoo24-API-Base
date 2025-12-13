from typing import List, Optional
from django.db.models import QuerySet
from core.utils.base_repository import BaseRepository
from core.models import OrderPrintReport, OrderPrintItem, OrderPrintAttachment

# ===== 1. Print Report Repository (Header) ===== #
class OrderPrintReportRepository(BaseRepository[OrderPrintReport]):
    """ مدیریت دسترسی به هدر گزارشات چاپ """
    def __init__(self):
        super().__init__(OrderPrintReport)

    def get_reports_by_order(self, order_id: int) -> QuerySet[OrderPrintReport]:
        """ دریافت تمام گزارشات مصرف یک سفارش خاص """
        return self.model.objects.filter(order_id=order_id)\
            .select_related('created_by')\
            .prefetch_related('items', 'attachments')\
            .order_by('-created_at')

# ===== 2. Print Item Repository (Details) ===== #
class OrderPrintItemRepository(BaseRepository[OrderPrintItem]):
    """ مدیریت اقلام مصرفی (کاغذ، مرکب و...) """
    def __init__(self):
        super().__init__(OrderPrintItem)
        
    def bulk_create_items(self, items: List[OrderPrintItem]):
        """ ثبت گروهی اقلام """
        return self.model.objects.bulk_create(items)

# ===== 3. Print Attachment Repository (Files) ===== #
class OrderPrintAttachmentRepository(BaseRepository[OrderPrintAttachment]):
    """ مدیریت فایل‌های پیوست چاپ """
    def __init__(self):
        super().__init__(OrderPrintAttachment)

    def bulk_create_attachments(self, attachments: List[OrderPrintAttachment]):
        return self.model.objects.bulk_create(attachments)