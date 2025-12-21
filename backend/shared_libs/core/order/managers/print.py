from typing import List
from django.db import models
from .base import BaseQuerySet

# ========== PRINT QUERYSET ========== #
class OrderPrintReportQuerySet(BaseQuerySet):
    """کوئری‌های هدر گزارشات چاپ"""
    
    def get_reports_by_order(self, order_id: int):
        """ دریافت تمام گزارشات مصرف یک سفارش خاص """
        return self.filter(order_id=order_id)\
            .select_related('created_by')\
            .prefetch_related('items', 'attachments')\
            .order_by('-created_at')
    
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== PRINT MANAGERS ========== #
class OrderPrintReportManager(models.Manager):
    def get_queryset(self):
        return OrderPrintReportQuerySet(self.model, using=self._db)

    def get_reports_by_order(self, order_id: int):
        return self.get_queryset().get_reports_by_order(order_id)
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)


# ========== PRINT ITEM MANAGERS ========== #
class OrderPrintItemManager(models.Manager):
    """ مدیریت اقلام مصرفی (کاغذ، مرکب و...) """
    
    def bulk_create_items(self, items: List):
        """ ثبت گروهی اقلام """
        return self.bulk_create(items)


# ========== PRINT ATTACHMENT MANAGERS ========== #
class OrderPrintAttachmentManager(models.Manager):
    """ مدیریت فایل‌های پیوست چاپ """
    
    def bulk_create_attachments(self, attachments: List):
        return self.bulk_create(attachments)