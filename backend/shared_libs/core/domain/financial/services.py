from random import randint
from decimal import Decimal

from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import (
    Invoice, User, Order, Quotation
)
from core.domain.commerce.order import OrderRepository
from .repositories import (
    InvoiceRepository, TransactionRepository, 
    QuotationRepository
)
from core.domain.infrastructure.logger import AuditLogDomainService

# ========== Financial Domain Service ========== #
class FinancialDomainService:
    """
    سرویس دامنه متمرکز بر قوانین بیزنس (Business Rules Only).
    عملیات CRUD خام (Create, Update, Delete) به لایه Application منتقل شده‌اند.
    """
    def __init__(self):
        self.invoice_repo = InvoiceRepository()
        self.transaction_repo = TransactionRepository()
        self.quotation_repo = QuotationRepository()
        self.order_repo = OrderRepository()
        self.audit_service = AuditLogDomainService()
    
    # ========================================== #
    # ============ INVOICE LOGIC =============== #
    # ========================================== #

    @transaction.atomic
    def issue_invoice_from_order(self, order: Order, user: User = None) -> Invoice:
        """
        صدور فاکتور بر اساس سفارش و ثبت لاگ ایجاد.
        """
        invoice_num = f"INV-{order.order_code}"

        # ===== بررسی وجود فاکتور ===== #
        existing_invoice = self.invoice_repo.filter(invoice_number=invoice_num).first()
        
        if existing_invoice:
            raise ValidationError(f"فاکتور برای این سفارش قبلاً صادر شده است (شماره: {invoice_num}).")

        # ===== بررسی وجود فاکتور برای سفارش ===== #
        if hasattr(order, 'invoice'):
             raise ValidationError("برای این سفارش قبلاً فاکتور صادر شده است.")

        # ===== محاسبه مالیات ===== #
        items_total = order.base_products_price
        services_total = Decimal(0)
        tax_amount = (items_total + services_total) * Decimal('0.09')
        final_amount = items_total + services_total + tax_amount
        
        # ===== دریافت اسلاگ محصول از طریق آیتم سفارش و محصول آن ===== #
        
        invoice_data = {
            "order": order,
            "invoice_number": invoice_num,
            "items_amount": items_total,
            "services_amount": services_total,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "paid_amount": 0,
            "discount_amount": 0,
            "status": Invoice.Status.PENDING,
            "description": "صدور خودکار سیستم"
        }
        
        try:
            invoice = self.invoice_repo.create(invoice_data)
            
        except IntegrityError as e:
            if 'unique constraint' in str(e):
                 raise ValidationError(f"فاکتور با شماره {invoice_num} هم‌اکنون توسط درخواست دیگری صادر شد.")
            raise e
        
        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=invoice,
            action='CREATE_INVOICE',
            changes={
                'invoice_number': invoice.invoice_number,
                'final_amount': str(final_amount),
                'order_code': order.order_code
            },
            description=_("صدور اولیه فاکتور سفارش")
        )
        
        return invoice
    
    @transaction.atomic
    def confirm_invoice_final(self, invoice: Invoice, user: User) -> Invoice:
        """ 
        قانون بیزنس: تبدیل وضعیت به نهایی (Finalize).
        شامل لاگ‌اندازی و تغییر وضعیت غیرقابل بازگشت.
        """
        if invoice.status == Invoice.Status.FINALIZE:
             raise ValidationError("این فاکتور قبلاً نهایی شده است.")
         
        old_status = invoice.status
        invoice.status = Invoice.Status.FINALIZE 
        invoice.finalized_at = timezone.now()
        invoice.save()
        
        self.audit_service.record_log(
            user=user,
            obj=invoice,
            action='INVOICE_STATUS_CHANGE',
            changes={
                'from': old_status,
                'to': Invoice.Status.FINALIZE,
                'finalized_at': str(invoice.finalized_at)
            },
            description=_("نهایی‌سازی فاکتور (قطعی)")
        )
        
        return invoice
    
    @transaction.atomic
    def recalculate_invoice_totals(self, invoice: Invoice, user: User = None) -> Invoice:
        """
        قانون بیزنس: محاسبه مجدد مبالغ.
        App Service بعد از اینکه داده‌های خام (مبلغ آیتم و...) را آپدیت کرد، 
        این متد را صدا می‌زند تا مالیات و مبلغ نهایی را استانداردسازی کند.
        """
        if not invoice.allows_editing:
             raise ValidationError("فاکتور جهت محاسبه مجدد قفل است.")

        old_final_amount = invoice.final_amount

        invoice.tax_amount = (invoice.items_amount + invoice.services_amount) * Decimal('0.09')
        invoice.final_amount = (
            invoice.items_amount + 
            invoice.services_amount + 
            invoice.tax_amount - 
            invoice.discount_amount
        )
        
        invoice.save()
        if old_final_amount != invoice.final_amount:
            self.audit_service.record_log(
                user=user,
                obj=invoice,
                action='INVOICE_RECALCULATION',
                changes={
                    'field': 'final_amount',
                    'from': str(old_final_amount),
                    'to': str(invoice.final_amount)
                },
                description=_("بروزرسانی مبالغ فاکتور")
            )
        self._update_invoice_payment_status(invoice, user)
        return invoice

    # ============ TRANSACTION LOGIC ============ #

    @transaction.atomic
    def verify_transaction(self, transaction_id: int, admin_user: User, is_approved: bool, rejection_reason: str = None):
        """ 
        قانون بیزنس: تایید تراکنش و اعمال اثر مالی (Side Effect) روی فاکتور.
        """
        trx = self.transaction_repo.get_by_id(transaction_id)
        if not trx: raise ValidationError("تراکنش یافت نشد.")
            
        if trx.status != 'pending':
            raise ValidationError("این تراکنش قبلاً تعیین تکلیف شده است.")

        action_type = 'APPROVE_TRANSACTION' if is_approved else 'REJECT_TRANSACTION'

        if is_approved:
            trx.status = 'confirmed'
            trx.confirmed_by = admin_user
            trx.save()
            
            self.audit_service.record_log(
                user=admin_user,
                obj=trx,
                action=action_type,
                changes={'status': 'confirmed', 'amount': str(trx.amount)},
                description=_("تایید تراکنش مالی")
            )
            
            self._apply_payment_to_invoice(trx.invoice, trx.amount, admin_user)
            
        else:
            trx.status = 'rejected'
            trx.rejection_reason = rejection_reason
            trx.confirmed_by = admin_user
            trx.save()
            
            self.audit_service.record_log(
                user=admin_user,
                obj=trx,
                action=action_type,
                changes={'status': 'rejected', 'reason': rejection_reason},
                description=_("رد تراکنش مالی")
            )
            
        return trx

    # ============ QUOTATION LOGIC ============ #

    @transaction.atomic
    def convert_quotation_to_invoice(self, quotation_id: int, user: User, order_id: int) -> Invoice:
        """
        قانون بیزنس پیچیده: تبدیل موجودیت A به B.
        """
        # ===== اطلاعات ورودی ===== #
        quotation = self.quotation_repo.get_quotation_detail(quotation_id)
        order = self.order_repo.get_by_id(order_id)
        
        if not quotation or not order:
            raise ValidationError("اطلاعات ورودی ناقص است.")

        # ===== اعتبارسنجی ===== #
        if quotation.converted_order:
            raise ValidationError("این استعلام قبلاً تبدیل شده است.")
        if hasattr(order, 'invoice'):
            raise ValidationError("سفارش مقصد قبلاً فاکتور دارد.")

        # ===== ایجاد فاکتور ===== #
        invoice = self.invoice_repo.create({
            "order": order,
            "invoice_number": f"INV-{order.order_code}-{randint(0000, 9999)}",
            "items_amount": quotation.total_price,
            "services_amount": 0,
            "tax_amount": 0,
            "discount_amount": 0,
            "final_amount": quotation.total_price,
            "status": Invoice.Status.PENDING,
            "description": f"تبدیل از پیش‌فاکتور {quotation.quotation_number}"
        })

        # ===== بروز کردن وضعیت ===== #
        quotation.converted_order = order
        quotation.status = Quotation.Status.CONVERTED
        quotation.save()
        
        # ===== ثبت لاگ تبدیل ===== #
        self.audit_service.record_log(
            user=user,
            obj=quotation,
            action='CONVERT_TO_INVOICE',
            changes={'converted_to_invoice_id': invoice.id},
            description=_("تبدیل موفق به فاکتور")
        )
        
        # ===== لاگ ایجاد فاکتور ===== #
        self.audit_service.record_log(
            user=user,
            obj=invoice,
            action='CREATE_FROM_QUOTATION',
            changes={'source_quotation_id': quotation.id},
            description=_("ایجاد اتوماتیک از پیش‌فاکتور")
        )

        self._log_status_change(invoice, None, invoice.status, user, "ایجاد خودکار از پیش‌فاکتور")
        return invoice

    # ============ INTERNAL HELPERS ============ #
    
    def _apply_payment_to_invoice(self, invoice: Invoice, amount: Decimal, user: User = None):
        """ منطق داخلی: افزایش مبلغ پرداختی و تریگر کردن وضعیت """
        invoice.paid_amount += amount
        invoice.save()
        
        self.audit_service.record_log(
            user=user,
            obj=invoice,
            action='PAYMENT_RECEIVED',
            changes={'amount_added': str(amount), 'new_paid_total': str(invoice.paid_amount)},
            description=_("ثبت پرداخت روی فاکتور")
        )
        
        self._update_invoice_payment_status(invoice, user)

    def _update_invoice_payment_status(self, invoice: Invoice, user: User = None):
        """ ماشین وضعیت (State Machine) پرداخت """
        remaining = invoice.remaining_amount
        old_status = invoice.status
        new_status = old_status

        if remaining <= 0:
            new_status = Invoice.Status.PAID_FULL
        elif invoice.paid_amount > 0:
            new_status = Invoice.Status.PAID_PARTIAL

        if old_status != new_status:
            invoice.status = new_status
            invoice.save()
            self._log_status_change(
                invoice, old_status, new_status, user=None, 
                description="تغییر اتوماتیک وضعیت بر اساس تراکنش"
            )
            
            self.audit_service.record_log(
                user=user,
                obj=invoice,
                action='INVOICE_STATUS_CHANGE',
                changes={
                    'from': old_status,
                    'to': new_status,
                    'reason': 'Automatic payment calculation'
                },
                description=_("تغییر وضعیت خودکار بر اساس پرداخت")
            )
