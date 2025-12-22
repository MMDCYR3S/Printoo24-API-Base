from typing import Optional
from django.db import models
from .base import BaseQuerySet

# ========== INVOICE QUERYSET ========== #
class InvoiceQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به فاکتور"""
    
    def get_invoice_by_order(self, order_id: int):
        """ دریافت فاکتور مرتبط با یک سفارش خاص """
        return self.select_related('order__user').filter(order_id=order_id).first()

    def get_invoices_with_details(self):
        """ لیست فاکتورها برای پنل مدیریت (همراه با سفارش و کاربر) """
        return self.select_related(
            'order__user__customer_profile'
        ).prefetch_related('transactions').order_by('-issued_at')
        
    def get_invoice_detail(self, invoice_id: int):
        """ دریافت جزئیات کامل یک فاکتور """
        return self.select_related(
            'order__user', 'order__address'
        ).prefetch_related(
            'transactions', 
        ).filter(id=invoice_id).first()
    
    def get_by_invoice_number(self, number: str):
        return self.filter(invoice_number=number).first()

# ========== INVOICE MANAGER ========== #
class InvoiceManager(models.Manager):
    def get_queryset(self):
        return InvoiceQuerySet(self.model, using=self._db)

    def get_invoice_by_order(self, order_id: int):
        return self.get_queryset().get_invoice_by_order(order_id)

    def get_invoices_with_details(self):
        return self.get_queryset().get_invoices_with_details()

    def get_invoice_detail(self, invoice_id: int):
        return self.get_queryset().get_invoice_detail(invoice_id)
    
    def get_by_invoice_number(self, number: str):
        return self.get_queryset().get_by_invoice_number(number)
    
    def create_invoice(self, data):
        return self.create(**data)