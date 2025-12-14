from decimal import Decimal
from typing import List, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import (
    Invoice, Transaction, User, InvoiceStatus, InvoiceStateLog, Order, 
    Quotation, QuotationItem, OrderStatus, Address
)
from core.domain.commerce.order import OrderRepository # برای تبدیل استعلام به سفارش
from .repositories import (
    InvoiceRepository, TransactionRepository, InvoiceStatusRepository, 
    QuotationRepository, QuotationItemRepository
)

# ========== FINANCIAL DOMAIN SERVICE ========== #
class FinancialDomainService:
    """
    سرویس دامنه جامع مالی:
    ۱. مدیریت فاکتورها (Invoice)
    ۲. مدیریت تراکنش‌ها (Transaction)
    ۳. مدیریت استعلام قیمت (Quotation)
    """
    def __init__(self):
        self.invoice_repo = InvoiceRepository()
        self.transaction_repo = TransactionRepository()
        self.status_repo = InvoiceStatusRepository()
        self.quotation_repo = QuotationRepository()
        self.quotation_item_repo = QuotationItemRepository()
        self.order_repo = OrderRepository() # جهت ایجاد سفارش از روی استعلام
    
    # ========================================== #
    # ============ INVOICE MANAGEMENT ========== #
    # ========================================== #

    @transaction.atomic
    def force_create_invoice(self, order: Order, user: User) -> Invoice:
        """ صدور دستی فاکتور (اگر سیستم خودکار صادر نکرده باشد) """
        if hasattr(order, 'related_invoice'):
            raise ValidationError("برای این سفارش قبلاً فاکتور صادر شده است.")
            
        invoice = self.issue_invoice_from_order(order)
        self._log_status_change(invoice, invoice.status, user, "صدور دستی فاکتور توسط مدیر")
        return invoice
    
    @transaction.atomic
    def issue_invoice_from_order(self, order: Order) -> Invoice:
        """
        صدور سیستماتیک فاکتور بر اساس مبالغ سفارش.
        """
        # ===== دریافت وضعیت اولیه ===== #
        initial_status = self.status_repo.get_by_code('PENDING_PAYMENT')
        if not initial_status:
            initial_status, _ = InvoiceStatus.objects.get_or_create(
                internal_code='PENDING_PAYMENT',
                defaults={'name': "در انتظار پرداخت", 'color': 'warning'}
            )
        
        # ===== محاسبه مبالغ ===== #
        items_total = order.base_products_price
        services_total = Decimal(0)
        tax_amount = (items_total + services_total) * Decimal('0.09')
        final_amount = items_total + services_total + tax_amount
        
        invoice_data = {
            "order": order,
            "invoice_number": f"INV-{order.order_code}",
            "items_amount": items_total,
            "services_amount": services_total,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "paid_amount": 0,
            "discount_amount": 0,
            "status": initial_status,
            "description": "صدور خودکار سیستم"
        }
        
        return self.invoice_repo.create(invoice_data)
    
    @transaction.atomic
    def confirm_invoice_final(self, invoice_id: int, user: User) -> Invoice:
        """ تبدیل به فاکتور نهایی (Finalize) """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        if invoice.status.internal_code == 'FINALIZE':
             raise ValidationError("این فاکتور قبلاً نهایی شده است.")

        invoice.convert_to_final()
        self._log_status_change(invoice, invoice.status, user, "تبدیل به فاکتور رسمی و قطعی")
        return invoice
    
    @transaction.atomic
    def recalculate_invoice(self, invoice_id: int) -> Invoice:
        """
        محاسبه مجدد مبالغ فاکتور.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")

        invoice.tax_amount = (invoice.items_amount + invoice.services_amount) * Decimal('0.09')
        invoice.final_amount = invoice.items_amount + invoice.services_amount + invoice.tax_amount - invoice.discount_amount
        
        invoice.save()
        self._update_invoice_payment_status(invoice)
        return invoice

    @transaction.atomic
    def update_invoice_metadata(self, invoice_id: int, data: dict, user: User) -> Invoice:
        """
        ویرایش اطلاعات غیر مالی فاکتور (توضیحات، تاریخ سررسید).
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        if 'due_date' in data: invoice.due_date = data['due_date']
        if 'description' in data: invoice.description = data['description']
        
        invoice.save()
        return invoice

    @transaction.atomic
    def delete_invoice(self, invoice_id: int, user: User):
        """
        حذف فاکتور.
        قانون: فاکتوری که تراکنش تایید شده دارد یا تسویه شده است، نباید حذف شود.
        """
        invoice = self.invoice_repo.get_invoice_detail(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        # ===== چک کردن تراکنش‌های تایید شده ===== #
        if invoice.transactions.filter(status='confirmed').exists():
            raise ValidationError("این فاکتور دارای تراکنش‌های مالی تایید شده است و قابل حذف نیست.")
        
        # ===== چک کردن وضعیت پرداخت ===== #
        if invoice.status.is_considered_paid:
             raise ValidationError("فاکتور تسویه شده قابل حذف نیست.")
            
        invoice.delete()

    # ============ TRANSACTION MANAGEMENT ============ #
    @transaction.atomic
    def register_manual_transaction(self, invoice_id: int, user: User, data: dict) -> Transaction:
        """ ثبت فیش واریزی """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        return self.transaction_repo.create({
            "invoice": invoice,
            "user": user,
            "amount": data['amount'],
            "method": data['method'],
            "tracking_code": data.get('tracking_code'),
            "payment_date": data.get('payment_date', timezone.now()),
            "receipt_image": data.get('receipt_image'),
            "dest_account": data.get('dest_account'),
            "status": 'pending'
        })
        
    @transaction.atomic
    def verify_transaction(self, transaction_id: int, admin_user: User, is_approved: bool, rejection_reason: str = None):
        """ تایید/رد تراکنش """
        trx = self.transaction_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
            
        if trx.status != 'pending':
            raise ValidationError("این تراکنش قبلاً تعیین تکلیف شده است.")

        if is_approved:
            trx.status = 'confirmed'
            trx.confirmed_by = admin_user
            trx.save()
            self._apply_payment_to_invoice(trx.invoice, trx.amount)
        else:
            trx.status = 'rejected'
            trx.rejection_reason = rejection_reason
            trx.confirmed_by = admin_user
            trx.save()
            
        return trx

    @transaction.atomic
    def update_transaction_details(self, transaction_id: int, data: dict, user: User) -> Transaction:
        """ 
        ویرایش جزئیات تراکنش (فقط در صورتی که Pending باشد).
        """
        trx = self.transaction_repo.get_by_id(transaction_id)
        if not trx:
            raise ValidationError("تراکنش یافت نشد.")

        if trx.status != 'pending':
            raise ValidationError("این تراکنش تعیین تکلیف شده و قابل ویرایش نیست.")

        if 'amount' in data: trx.amount = data['amount']
        if 'method' in data: trx.method = data['method']
        if 'tracking_code' in data: trx.tracking_code = data['tracking_code']
        if 'payment_date' in data: trx.payment_date = data['payment_date']
        if 'receipt_image' in data: trx.receipt_image = data['receipt_image']
        if 'dest_account' in data: trx.dest_account = data['dest_account']
        
        trx.save()
        return trx
    
    @transaction.atomic
    def delete_transaction(self, transaction_id: int, user: User):
        """ 
        حذف تراکنش (فقط در صورتی که Pending باشد).
        """
        trx = self.transaction_repo.get_by_id(transaction_id)
        if not trx:
            raise ValidationError("تراکنش یافت نشد.")

        if trx.status == 'confirmed':
            raise ValidationError("تراکنش تایید شده است و سند حسابداری خورده. قابل حذف نیست.")

        trx.delete()

    # ========================================== #
    # ============ QUOTATION MANAGEMENT ======== #
    # ========================================== #

    @transaction.atomic
    def create_quotation(self, user: User, data: dict, items_data: List[dict]) -> Quotation:
        """ ایجاد استعلام قیمت جدید """
        # ===== محاسبه مبالغ ===== #
        total_amount = sum(Decimal(str(item['unit_price'])) * int(item['quantity']) for item in items_data)
        tax_amount = total_amount * Decimal('0.09')
        discount_amount = Decimal(str(data.get('discount_amount', 0)))
        final_amount = total_amount + tax_amount - discount_amount

        # ===== ایجاد هدر ===== #
        quotation = self.quotation_repo.create({
            "user": user,
            "title": data['title'],
            "quotation_number": f"QUO-{timezone.now().strftime('%Y%m%d')}-{user.id}", # لاجیک ساده شماره‌گذاری
            "valid_until": data['valid_until'],
            "status": 'draft',
            "total_amount": total_amount,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "description": data.get('description', '')
        })

        # ===== ایجاد اقلام ===== #
        items = [
            QuotationItem(
                quotation=quotation,
                product_name=item['product_name'],
                description=item.get('description', ''),
                quantity=item['quantity'],
                unit_price=item['unit_price']
            ) for item in items_data
        ]
        self.quotation_item_repo.bulk_create_items(items)
        
        return quotation

    @transaction.atomic
    def update_quotation_status(self, quotation_id: int, status: str, user: User) -> Quotation:
        """ تغییر وضعیت استعلام (تایید مشتری، رد شدن، ارسال شده) """
        quotation = self.quotation_repo.get_by_id(quotation_id)
        if not quotation: raise ValidationError("استعلام یافت نشد.")
        
        if quotation.status == 'converted':
            raise ValidationError("این استعلام قبلاً به سفارش تبدیل شده است.")
            
        quotation.status = status
        quotation.save()
        return quotation

    @transaction.atomic
    def convert_quotation_to_order(self, quotation_id: int, user: User, address_id: int) -> Order:
        """
        تبدیل استعلام تایید شده به سفارش واقعی و صدور فاکتور.
        نکته: چون QuotationItem محصول واقعی ندارد (فقط تکست است)،
        در اینجا یک سفارش "اختصاصی" (Type 2) ایجاد می‌کنیم.
        """
        quotation = self.quotation_repo.get_quotation_detail(quotation_id)
        if not quotation: raise ValidationError("استعلام یافت نشد.")
        
        if quotation.status != 'accepted':
            raise ValidationError("فقط استعلام‌های 'تایید شده توسط مشتری' قابل تبدیل هستند.")
            
        if quotation.converted_order:
            raise ValidationError("این استعلام قبلاً تبدیل شده است.")

        # ===== 1. ایجاد سفارش ===== #
        address = Address.objects.get(id=address_id)

        initial_status, _ = OrderStatus.objects.get_or_create(internal_code='PENDING', defaults={'name': 'در انتظار بررسی'})

        order = self.order_repo.create({
            "user": quotation.user,
            "order_code": f"ORD-{quotation.quotation_number.split('-')[1]}",
            "type": "2",
            "current_status": initial_status,
            "address": address,
            "base_products_price": quotation.total_amount,
            "total_price": quotation.final_amount,
            "description": f"تبدیل شده از استعلام {quotation.quotation_number}. \n {quotation.description}"
        })

        # ===== 2. لینک کردن ===== #
        quotation.converted_order = order
        quotation.status = 'converted'
        quotation.save()

        # ===== 3. صدور فاکتور ===== #
        invoice = self.issue_invoice_from_order(order)
        
        invoice.discount_amount = quotation.discount_amount
        invoice.final_amount = quotation.final_amount
        invoice.save()

        return order

    # ============ INTERNAL HELPERS ============ #
    def _apply_payment_to_invoice(self, invoice: Invoice, amount: Decimal):
        """ افزایش مبلغ پرداختی و بررسی وضعیت تسویه """
        invoice.paid_amount += amount
        invoice.save()
        self._update_invoice_payment_status(invoice)

    def _update_invoice_payment_status(self, invoice: Invoice):
        """ ماشین وضعیت خودکار پرداخت """
        remaining = invoice.remaining_amount
        
        new_status_code = None
        if remaining <= 0:
            new_status_code = 'PAID_FULL'
        elif invoice.paid_amount > 0:
            new_status_code = 'PAID_PARTIAL'
        else:
            return

        if invoice.status.internal_code != new_status_code:
            new_status = self.status_repo.get_by_code(new_status_code)
            if new_status:
                self._log_status_change(
                    invoice, new_status, user=None, 
                    description="تغییر اتوماتیک وضعیت بر اساس تایید تراکنش"
                )

    def _log_status_change(self, invoice, new_status, user=None, description=""):
        """ لاگ کردن تغییر وضعیت فاکتور """
        old_status = invoice.status
        invoice.status = new_status
        invoice.save()
        
        InvoiceStateLog.objects.create(
            invoice=invoice,
            from_status=old_status,
            to_status=new_status,
            user=user,
            description=description
        )
