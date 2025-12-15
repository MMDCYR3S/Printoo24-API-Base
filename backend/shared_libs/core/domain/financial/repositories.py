from typing import Optional
from django.db.models import QuerySet
from core.utils.base_repository import BaseRepository
from core.models import Invoice, Transaction, Quotation

# ===== Invoice Repository ===== #
class InvoiceRepository(BaseRepository[Invoice]):
    """ مدیریت دسترسی به داده‌های فاکتور """
    def __init__(self):
        super().__init__(Invoice)
        
    def get_invoice_by_order(self, order_id: int) -> Optional[Invoice]:
        """ دریافت فاکتور مرتبط با یک سفارش خاص """
        return self.model.objects.select_related('order__user').filter(order_id=order_id).first()

    def get_invoices_with_details(self) -> QuerySet[Invoice]:
        """ لیست فاکتورها برای پنل مدیریت (همراه با سفارش و کاربر) """
        return self.model.objects.select_related(
            'order__user__customer_profile'
        ).prefetch_related('transactions').order_by('-issued_at')
        
    def get_invoice_detail(self, invoice_id: int) -> Optional[Invoice]:
        """ دریافت جزئیات کامل یک فاکتور """
        return self.model.objects.select_related(
            'order__user', 'order__address'
        ).prefetch_related(
            'transactions', 
            'logs__user',
        ).filter(id=invoice_id).first()
        
# ===== Transaction Repository ===== #
class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_pending_transactions(self) -> QuerySet[Transaction]:
        return self.model.objects.select_related('invoice', 'user').filter(status='pending')

# ===== Quotation Repository (NEW) ===== #
class QuotationRepository(BaseRepository[Quotation]):
    """ مدیریت استعلام قیمت / پیش‌فاکتور رسمی """
    def __init__(self):
        super().__init__(Quotation)

    def get_quotation_detail(self, quotation_id: int) -> Optional[Quotation]:
        return self.model.objects.select_related('user', 'converted_order').filter(id=quotation_id).first()

