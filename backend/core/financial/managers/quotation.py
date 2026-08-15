from datetime import datetime, time

from django.db import models
from django.db.models import Sum, Count, Avg
from django.utils import timezone

from .base import BaseQuerySet


# ========== QUOTATION QUERYSET ========== #
class QuotationQuerySet(BaseQuerySet):
    def get_quotation_detail(self, quotation_id: int):
        return self.select_related('created_by', 'converted_order', 'cart_item').filter(id=quotation_id).first()

    def get_quotation_by_order(self, order_id: int):
        return self.select_related(
            'converted_order',
            'converted_order__user',
            'cart_item'
        ).filter(converted_order_id=order_id).first()

    def get_quotation_by_cart_item(self, cart_item_id: int):
        """ دریافت پیش‌فاکتور از آیتم سبد خرید """
        return self.select_related('created_by', 'converted_order', 'cart_item').filter(cart_item_id=cart_item_id).first()

    def get_active_quotations(self):
        """ دریافت پیش‌فاکتورات فعال (در حال انتظار) """
        return self.filter(status='draft')


# ========== QUOTATION MANAGER ========== #
class QuotationManager(models.Manager):
    def get_queryset(self):
        return QuotationQuerySet(self.model, using=self._db)

    def get_quotation_detail(self, quotation_id: int):
        return self.get_queryset().get_quotation_detail(quotation_id)

    def get_quotation_by_order(self, order_id: int):
        return self.get_queryset().get_quotation_by_order(order_id)

    def get_quotation_by_cart_item(self, cart_item_id: int):
        return self.get_queryset().get_quotation_by_cart_item(cart_item_id)

    def get_active_quotations(self):
        return self.get_queryset().get_active_quotations()