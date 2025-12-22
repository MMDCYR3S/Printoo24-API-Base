from django.db import models
from .base import BaseQuerySet

# ========== QUOTATION QUERYSET ========== #
class QuotationQuerySet(BaseQuerySet):
    def get_quotation_detail(self, quotation_id: int):
        return self.select_related('created_by', 'converted_order').filter(id=quotation_id).first()

    def get_quotation_by_order(self, order_id: int):
        return self.select_related(
            'converted_order', 
            'converted_order__user'
        ).filter(converted_order_id=order_id).first()

# ========== QUOTATION MANAGER ========== #
class QuotationManager(models.Manager):
    def get_queryset(self):
        return QuotationQuerySet(self.model, using=self._db)

    def get_quotation_detail(self, quotation_id: int):
        return self.get_queryset().get_quotation_detail(quotation_id)

    def get_quotation_by_order(self, order_id: int):
        return self.get_queryset().get_quotation_by_order(order_id)
