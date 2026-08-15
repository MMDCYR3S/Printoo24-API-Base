import uuid
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from core.models import Order
from core.financial.models import Invoice, FinancialLog


class InvoiceService:
    # ===== تولید شماره فاکتور ===== #
    def _generate_invoice_number(self, order_code: str) -> str:
        return f"INV-{order_code}" if order_code else f"INV-{uuid.uuid4().hex[:8].upper()}"

    # ===== تعیین وضعیت خودکار ===== #
    def _determine_status(self, paid_amount: Decimal, final_amount: Decimal):
        if paid_amount >= final_amount:
            return Invoice.Status.PAID_FULL
        elif paid_amount > 0:
            return Invoice.Status.PAID_PARTIAL
        return Invoice.Status.PENDING

    # ===== لیست فاکتورها ===== #
    def list_invoices(self):
        return Invoice.objects.select_related('order').all().order_by('-issued_at')

    # ===== دریافت فاکتور ===== #
    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            raise NotFound("فاکتور مورد نظر یافت نشد.")
        return invoice

    # ===== دریافت بر اساس سفارش ===== #
    def get_by_order(self, order_id: int) -> Invoice:
        invoice = Invoice.objects.filter(order_id=order_id).first()
        if not invoice:
            raise NotFound("هیچ فاکتوری برای این سفارش یافت نشد.")
        return invoice

    # ===== ایجاد فاکتور ===== #
    @transaction.atomic
    def create_invoice(self, data: dict, actor) -> Invoice:
        order_id = data.get('order')
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise ValidationError("سفارش معتبر نیست.")

        if Invoice.objects.filter(order=order).exists():
            raise ValidationError("برای این سفارش قبلاً فاکتور صادر شده است.")

        # تعیین مبلغ نهایی در صورت عدم ارسال
        final_amount = data.get('final_amount', order.final_price)
        paid_amount = data.get('paid_amount', 0)

        invoice = Invoice.objects.create(
            order=order,
            invoice_number=self._generate_invoice_number(order.order_code),
            paid_amount=paid_amount,
            items_amount=data.get('items_amount', order.base_products_price),
            services_amount=data.get('services_amount', 0),
            tax_amount=data.get('tax_amount', 0),
            discount_amount=data.get('discount_amount', 0),
            final_amount=final_amount,
            description=data.get('description', ''),
            status=self._determine_status(paid_amount, final_amount),
            due_date=data.get('due_date'),
        )

        # ثبت لاگ
        FinancialLog.log(
            action_type=FinancialLog.ActionType.INVOICE_CREATED,
            order=order,
            user=order.user,
            invoice=invoice,
            description=f"ایجاد فاکتور {invoice.invoice_number}",
            created_by=actor,
        )
        return invoice

    # ===== ویرایش فاکتور ===== #
    @transaction.atomic
    def update_invoice(self, invoice_id: int, data: dict, actor) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        if invoice.status == Invoice.Status.FINALIZE:
            raise ValidationError("فاکتور نهایی شده و قابل ویرایش نیست.")

        old_values = {
            'paid_amount': str(invoice.paid_amount),
            'final_amount': str(invoice.final_amount),
            'status': invoice.status,
        }

        for field, value in data.items():
            if field in ['paid_amount', 'items_amount', 'services_amount',
                         'tax_amount', 'discount_amount', 'final_amount',
                         'description', 'due_date']:
                setattr(invoice, field, value)

        # به‌روزرسانی خودکار وضعیت
        invoice.status = self._determine_status(invoice.paid_amount, invoice.final_amount)
        invoice.save()

        new_values = {
            'paid_amount': str(invoice.paid_amount),
            'final_amount': str(invoice.final_amount),
            'status': invoice.status,
        }

        FinancialLog.log(
            action_type=FinancialLog.ActionType.INVOICE_UPDATED,
            order=invoice.order,
            user=invoice.order.user,
            invoice=invoice,
            field_name='invoice_fields',
            old_value=old_values,
            new_value=new_values,
            description=f"ویرایش فاکتور {invoice.invoice_number}",
            created_by=actor,
        )
        return invoice

    # ===== حذف فاکتور ===== #
    @transaction.atomic
    def delete_invoice(self, invoice_id: int, actor):
        invoice = self.get_invoice(invoice_id)
        if invoice.status == Invoice.Status.FINALIZE:
            raise ValidationError("فاکتور نهایی شده و قابل حذف نیست.")
        order = invoice.order
        invoice.delete()
        FinancialLog.log(
            action_type=FinancialLog.ActionType.INVOICE_UPDATED,  # یا نوع دیگر
            order=order,
            user=order.user,
            description=f"حذف فاکتور {invoice.invoice_number}",
            created_by=actor,
        )

    # ===== نهایی‌سازی فاکتور ===== #
    @transaction.atomic
    def finalize_invoice(self, invoice_id: int, actor) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        if invoice.status == Invoice.Status.FINALIZE:
            return invoice
        invoice.status = Invoice.Status.FINALIZE
        invoice.finalized_at = timezone.now()
        invoice.save()
        FinancialLog.log(
            action_type=FinancialLog.ActionType.INVOICE_UPDATED,
            order=invoice.order,
            user=invoice.order.user,
            invoice=invoice,
            description=f"نهایی‌سازی فاکتور {invoice.invoice_number}",
            created_by=actor,
        )
        return invoice

    # ===== تغییر وضعیت دستی ===== #
    @transaction.atomic
    def change_status(self, invoice_id: int, new_status: str, actor) -> Invoice:
        invoice = self.get_invoice(invoice_id)
        valid_statuses = [choice[0] for choice in Invoice.Status.choices]
        if new_status not in valid_statuses:
            raise ValidationError("وضعیت نامعتبر است.")

        if new_status == Invoice.Status.FINALIZE and not invoice.finalized_at:
            invoice.finalized_at = timezone.now()

        invoice.status = new_status
        invoice.save()

        FinancialLog.log(
            action_type=FinancialLog.ActionType.INVOICE_UPDATED,
            order=invoice.order,
            user=invoice.order.user,
            invoice=invoice,
            description=f"تغییر وضعیت فاکتور {invoice.invoice_number} به {new_status}",
            created_by=actor,
        )
        return invoice