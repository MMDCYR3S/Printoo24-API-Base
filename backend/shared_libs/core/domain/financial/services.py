from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import Invoice, Transaction, User, InvoiceStatus, InvoiceStateLog, Order
from .repositories import InvoiceRepository, TransactionRepository, InvoiceStatusRepository

class FinancialDomainService:
    """
    سرویس دامنه برای مدیریت منطق کسب‌وکارهای مالی.
    شامل: صدور فاکتور، ثبت تراکنش، مغایرت‌گیری و تغییر وضعیت‌ها.
    """
    def __init__(self):
        self.invoice_repo = InvoiceRepository()
        self.transaction_repo = TransactionRepository()
        self.status_repo = InvoiceStatusRepository()
    
    @transaction.atomic
    def force_create_invoice(self, order: Order, user: User) -> Invoice:
        """
        صدور دستی فاکتور برای یک سفارش (اگر قبلاً نداشته باشد).
        """
        # ===== اگر فاکتور وجود داشته باشد ===== #
        if hasattr(order, 'invoice'):
            raise ValidationError("برای این سفارش قبلاً فاکتور صادر شده است.")
        # ===== در صورت نبود، ایجاد فاکتور ===== #
        invoice = self.issue_invoice_from_order(order)
        # ===== ایجاد لاگ ===== #
        self._log_status_change(invoice, invoice.status, user, "صدور دستی فاکتور توسط مدیر")
        return invoice
    
    # ===== صدور فاکتور برای سفارش ===== #
    @transaction.atomic
    def issue_invoice_from_order(self, order) -> Invoice:
        """
        صدور خودکار فاکتور (معمولاً پیش‌فاکتور) هنگام ثبت سفارش.
        این متد توسط OrderDomainService صدا زده می‌شود.
        """
        
        # ===== دریافت وضعیت اولیه فاکتور ===== #
        initial_status = self.status_repo.get_by_code('PENDING_PAYMENT')
        if not initial_status:
            initial_status, _ = InvoiceStatus.objects.get_or_create(
                name="در انتظار پرداخت", internal_code='PENDING_PAYMENT', color='warning'
            )
        
        # ===== محاسبه مجموعه هزینه ها و مبلغ نهایی ===== #
        items_total = order.base_products_price
        services_total = Decimal(0)
        # ===== محاسبه مالیات + ایجاد قیمت کل ===== #
        tax_amount = (items_total + services_total) * Decimal('0.09')
        final_amount = items_total + services_total + tax_amount
        
        # ===== ایجاد فاکتور ===== #
        invoice_data = {
            "order": order,
            "invoice_type": 'proforma',
            "invoice_number": f"INV-{order.order_code}",
            "items_amount": items_total,
            "services_amount": services_total,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "paid_amount": 0,
            "status": initial_status
        }
        
        return self.invoice_repo.create(invoice_data)
    
    @transaction.atomic
    def confirm_invoice_final(self, invoice_id: int, user: User) -> Invoice:
        """
        تبدیل پیش‌فاکتور به فاکتور نهایی (Finalize).
        بعد از این مرحله، اقلام فاکتور نباید تغییر کنند.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        # ===== چک کردن اینکه آیا فاکتور نهایی شده است ===== #
        if invoice.invoice_type == 'final':
            raise ValidationError("این فاکتور قبلاً نهایی شده است.")
        # ===== تبدیل به فاکتور نهایی ===== #
        invoice.convert_to_final()
        
        self._log_status_change(invoice, invoice.status, user, "تبدیل به فاکتور رسمی و قطعی")
        return invoice
    
    @transaction.atomic
    def delete_invoice(self, invoice_id: int, user: User):
        """
        حذف فاکتور.
        قانون: فاکتوری که تراکنش تایید شده دارد یا نهایی شده است، نباید حذف شود.
        """
        invoice = self.invoice_repo.get_invoice_detail(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        # ===== چک کردن تراکنش‌های تایید شده ===== #
        if invoice.transactions.filter(status='confirmed').exists():
            raise ValidationError("این فاکتور دارای تراکنش‌های مالی تایید شده است و قابل حذف نیست.")
        
        # ===== چک کردن وضعیت فاکتور ===== #
        if invoice.status.is_considered_paid:
             raise ValidationError("فاکتور تسویه شده قابل حذف نیست.")
        invoice.delete()
        
    @transaction.atomic
    def update_invoice_metadata(self, invoice_id: int, data: dict, user: User) -> Invoice:
        """
        ویرایش اطلاعات غیر مالی فاکتور (توضیحات، تاریخ سررسید).
        مبالغ فقط از طریق recalculate آپدیت می‌شوند.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice: raise ValidationError("فاکتور یافت نشد.")
        
        if 'due_date' in data: invoice.due_date = data['due_date']
        if 'description' in data: invoice.description = data['description']
        
        invoice.save()
        return invoice
    
    # ===== محاسبه مجدد فاکتور ===== #
    @transaction.atomic
    def recalculate_invoice(self, invoice: Invoice):
        """
        محاسبه مجدد فاکتور (زمانی که هزینه‌های لجستیک یا خدمات تغییر می‌کند).
        """
        approved_costs = invoice.order.cost_reports.filter(is_approved_by_finance=True)
        new_services_total = sum(report.total_amount for report in approved_costs)
        
        invoice.services_amount = new_services_total
        invoice.tax_amount = (invoice.items_amount + invoice.services_amount) * Decimal('0.09')
        invoice.final_amount = invoice.items_amount + invoice.services_amount + invoice.tax_amount - invoice.discount_amount
        
        invoice.save()
        
        self._update_invoice_payment_status(invoice)
        return invoice
    
    # ========== مدیریت تراکنش‌ها ========== #
    @transaction.atomic
    def register_manual_transaction(self, invoice_id: int, user: User, data: dict) -> Transaction:
        """ ثبت فیش بانکی یا تراکنش دستی توسط مشتری یا ادمین """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise ValidationError("فاکتور یافت نشد.")
        
        transaction = self.transaction_repo.create({
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
        
        return transaction
        
    @transaction.atomic
    def verify_transaction(self, transaction_id: int, admin_user: User, is_approved: bool, rejection_reason: str = None):
        """ تایید یا رد تراکنش توسط واحد مالی """
        trx = self.transaction_repo.get_by_id(transaction_id)
        if not trx:
            raise ValidationError("تراکنش یافت نشد.")
            
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

        # ===== ثابت ماندن تراکنش تاییده شده/رد شده ===== #
        if trx.status != 'pending':
            raise ValidationError("این تراکنش تعیین تکلیف شده و قابل ویرایش نیست.")

        # ===== آپدیت فیلدها ===== #
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
    
    def _apply_payment_to_invoice(self, invoice: Invoice, amount: Decimal):
        """ افزودن مبلغ به پرداختی‌های فاکتور و چک کردن وضعیت تسویه """
        invoice.paid_amount += amount
        invoice.save()
        self._update_invoice_payment_status(invoice)

    def _update_invoice_payment_status(self, invoice: Invoice):
        """ ماشین وضعیت هوشمند پرداخت """
        remaining = invoice.remaining_amount
        
        new_status_code = None
        
        if remaining <= 0:
            new_status_code = 'PAID_FULL'
        elif invoice.paid_amount > 0:
            new_status_code = 'PAID_PARTIAL'
        else:
            return

        new_status = self.status_repo.get_by_code(new_status_code)
        
        if new_status and invoice.status != new_status:
            self._change_invoice_status_with_log(
                invoice, new_status, user=None, description="تغییر اتوماتیک بر اساس تایید تراکنش"
            )
    
    def _change_invoice_status_with_log(self, invoice, new_status, user=None, description=""):
        """ تغییر وضعیت اتمیک همراه با لاگ """
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
            
    def _log_status_change(self, invoice, new_status, user=None, description=""):
        """ 
        تغییر وضعیت اتمیک همراه با لاگ.
        نام قبلی _change_invoice_status_with_log بود که باعث خطا می‌شد.
        """
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