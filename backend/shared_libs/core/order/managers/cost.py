from typing import List
from django.db import models
from .base import BaseQuerySet

# ========== COST SHEET QUERYSET ========== #
class OrderCostSheetQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به سند هزینه مادر"""
    
    def get_by_order_id(self, order_id: int):
        """ دریافت شیت (فقط اعداد نهایی) """
        return self.filter(order_id=order_id).first()

# ========== COST SHEET MANAGERS ========== #
class OrderCostSheetManager(models.Manager):
    def get_queryset(self):
        return OrderCostSheetQuerySet(self.model, using=self._db)

    def get_by_order_id(self, order_id: int):
        return self.get_queryset().get_by_order_id(order_id)

# ========== COST REPORT QUERYSET ========== #
class OrderCostReportQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به گزارشات هزینه"""
    
    def get_reports_by_sheet(self, sheet_id: int):
        return self.filter(sheet_id=sheet_id)\
            .select_related('submitter')\
            .order_by('-created_at')
            
    def get_report_detail(self, report_id: int):
        return self.filter(id=report_id)\
            .select_related('sheet__order', 'submitter')\
            .prefetch_related('items__catalog_item', 'attachments')\
            .first()
            
    def get_by_id(self, pk: int):
        return self.filter(pk=pk).first()

# ========== COST REPORT MANAGERS ========== #
class OrderCostReportManager(models.Manager):
    def get_queryset(self):
        return OrderCostReportQuerySet(self.model, using=self._db)

    def get_reports_by_sheet(self, sheet_id: int):
        return self.get_queryset().get_reports_by_sheet(sheet_id)

    def get_report_detail(self, report_id: int):
        return self.get_queryset().get_report_detail(report_id)
    
    def get_by_id(self, pk: int):
        return self.get_queryset().get_by_id(pk)

# ========== COST ITEM MANAGERS ========== #
class OrderCostItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def bulk_create_items(self, items: List):
        return self.bulk_create(items)
        
    def get_items_by_report(self, report_id: int):
        return self.filter(report_id=report_id)

# ========== COST ATTACHMENT MANAGERS ========== #
class OrderCostAttachmentManager(models.Manager):
    def model(self, **kwargs):
        return self.model(**kwargs)
    
    def bulk_create_attachments(self, attachments: List):
        return self.bulk_create(attachments)

# ========== COST CATEGORY QUERYSET ========== #
class OrderCostCategoryQuerySet(BaseQuerySet):
    
    def get_all_active(self):
        return self.order_by('title')
        
    def get_by_slug(self, slug: str):
        return self.filter(slug=slug).first()

# ========== COST CATEGORY MANAGERS ========== #
class OrderCostCategoryManager(models.Manager):
    def get_queryset(self):
        return OrderCostCategoryQuerySet(self.model, using=self._db)

    def get_all_active(self):
        return self.get_queryset().get_all_active()

    def get_by_slug(self, slug: str):
        return self.get_queryset().get_by_slug(slug)
