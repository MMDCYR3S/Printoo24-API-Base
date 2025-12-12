from typing import List, Optional
from django.db.models import QuerySet, Prefetch
from core.utils.base_repository import BaseRepository
from core.models import Invoice, Transaction, InvoiceStatus, Order

# ===== Invoice Repository ===== #
class InvoiceRepository(BaseRepository[Invoice]):
    """ مدیریت دسترسی به داده‌های فاکتور """
    def __init__(self):
        super().__init__(Invoice)
        
    def get_invoice_by_order(self, order_id: int) -> Optional[Invoice]:
        """ دریافت فاکتور مرتبط با یک سفارش خاص """
        return self.model.objects.select_related('status', 'order__user').filter(order_id=order_id).first()

    def get_invoices_with_details(self) -> QuerySet[Invoice]:
        """ لیست فاکتورها برای پنل مدیریت (همراه با سفارش و کاربر) """
        return self.model.objects.select_related(
            'status', 'order__user__customer_profile'
        ).prefetch_related('transactions').order_by('-issued_at')
        
    def get_invoice_detail(self, invoice_id: int) -> Optional[Invoice]:
        """ دریافت جزئیات کامل یک فاکتور """
        return self.model.objects.select_related(
            'status', 'order__user', 'order__address'
        ).prefetch_related(
            'transactions', 
            'logs__user', 'logs__from_status', 'logs__to_status'
        ).filter(id=invoice_id).first()
        
# ===== Transaction Repository ===== #
class TransactionRepository(BaseRepository[Transaction]):
    """ مدیریت دسترسی به داده‌های تراکنش """
    def __init__(self):
        super().__init__(Transaction)

    def get_pending_transactions(self) -> QuerySet[Transaction]:
        """ لیست تراکنش‌های منتظر تایید (برای داشبورد مالی) """
        return self.model.objects.select_related('invoice', 'user').filter(status='pending')
    
# ===== Invoice Status Repository ===== #
class InvoiceStatusRepository(BaseRepository[InvoiceStatus]):
    def __init__(self):
        super().__init__(InvoiceStatus)
        
    def get_by_code(self, code: str) -> Optional[InvoiceStatus]:
        return self.model.objects.filter(internal_code=code).first()
        