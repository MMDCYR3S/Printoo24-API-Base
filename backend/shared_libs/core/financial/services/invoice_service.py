import uuid
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from core.models import Order
from core.financial.models import Invoice

class InvoiceService:
    # ===== تولید شماره فاکتور ===== #
    def _generate_invoice_number(self, order_code: str) -> str:
        return f"INV-{order_code}" if order_code else f"INV-{uuid.uuid4().hex[:8].upper()}"

    # ===== ایجاد فاکتور جدید ===== #
    @transaction.atomic
    def create_invoice(self, order_id: int, data: dict) -> Invoice:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise NotFound("داواکاریی دیاریکراو نەدۆزرایەوە.")
            
        if Invoice.objects.filter(order=order).exists():
            raise ValidationError("برای این سفارش قبلاً فاکتور صادر شده است.")

        invoice = Invoice.objects.create(
            order=order,
            invoice_number=self._generate_invoice_number(order.order_code),
            items_amount=data.get('items_amount', order.base_products_price),
            final_amount=data.get('final_amount', order.total_price),
            **{k: v for k, v in data.items() if k not in ['items_amount', 'final_amount']}
        )
        return invoice

    # ===== دریافت فاکتور براساس سفارش ===== #
    def get_by_order(self, order_id: int) -> Invoice:
        invoice = Invoice.objects.filter(order_id=order_id).first()
        if not invoice:
            raise NotFound("هیچ فاکتۆرێک بۆ ئەم داواکارییە نەدۆزرایەوە.")
        return invoice

    # ===== ویرایش فاکتور ===== #
    @transaction.atomic
    def update_invoice(self, invoice_id: int, data: dict) -> Invoice:
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            raise NotFound("فاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        for field, value in data.items():
            if hasattr(invoice, field) and field not in ['id', 'invoice_number', 'order']:
                setattr(invoice, field, value)
        invoice.save()
        return invoice

    # ===== حذف فاکتور ===== #
    @transaction.atomic
    def delete_invoice(self, invoice_id: int):
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            raise NotFound("فاکتۆری دیاریکراو نەدۆزرایەوە.")
        invoice.delete()

    # ===== تایید و نهایی‌سازی فاکتور ===== #
    @transaction.atomic
    def approve_invoice(self, invoice_id: int) -> Invoice:
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            raise NotFound("فاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        invoice.status = Invoice.Status.FINALIZE
        invoice.finalized_at = timezone.now()
        invoice.save(update_fields=['status', 'finalized_at', 'updated_at'])
        return invoice

    # ===== تغییر وضعیت فاکتور ===== #
    @transaction.atomic
    def change_status(self, invoice_id: int, new_status: str) -> Invoice:
        invoice = Invoice.objects.filter(id=invoice_id).first()
        if not invoice:
            raise NotFound("فاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        valid_statuses = [choice[0] for choice in Invoice.Status.choices]
        if new_status not in valid_statuses:
            raise ValidationError(f"دۆخەکە نادروستە. ڕێگەپێدراو: {valid_statuses}")

        invoice.status = new_status
        if new_status == Invoice.Status.FINALIZE and not invoice.finalized_at:
            invoice.finalized_at = timezone.now()
            invoice.save(update_fields=['status', 'finalized_at', 'updated_at'])
        else:
            invoice.save(update_fields=['status', 'updated_at'])
        return invoice