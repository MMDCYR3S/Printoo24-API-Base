import uuid
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from core.models import Order
from core.financial.models import Quotation

class QuotationService:
    # ===== ایجاد پیش‌فاکتور جدید ===== #
    @transaction.atomic
    def create_quotation(self, order_id: int, data: dict, user) -> Quotation:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise NotFound("داواکاریی دیاریکراو نەدۆزرایەوە.")
            
        if Quotation.objects.filter(converted_order=order).exists():
            raise ValidationError("برای این سفارش قبلاً پیش‌فاکتور صادر شده است.")

        q_number = f"QTE-{order.order_code if order.order_code else uuid.uuid4().hex[:8].upper()}"
        
        quotation = Quotation.objects.create(
            quotation_number=q_number,
            created_by=user,
            converted_order=order,
            customer_name=data.get('customer_name', order.recipient_name),
            total_price=data.get('total_price', order.total_price),
            **{k: v for k, v in data.items() if k not in ['customer_name', 'total_price']}
        )
        return quotation

    # ===== دریافت پیش‌فاکتور براساس سفارش ===== #
    def get_by_order(self, order_id: int) -> Quotation:
        quotation = Quotation.objects.filter(converted_order_id=order_id).first()
        if not quotation:
            raise NotFound("هیچ پێشفاکتۆرێک بۆ ئەم داواکارییە نەدۆزرایەوە.")
        return quotation

    # ===== ویرایش پیش‌فاکتور ===== #
    @transaction.atomic
    def update_quotation(self, quotation_id: int, data: dict) -> Quotation:
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پێشفاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        for field, value in data.items():
            if hasattr(quotation, field) and field not in ['id', 'quotation_number', 'converted_order']:
                setattr(quotation, field, value)
        quotation.save()
        return quotation

    # ===== حذف پیش‌فاکتور ===== #
    @transaction.atomic
    def delete_quotation(self, quotation_id: int):
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پێشفاکتۆری دیاریکراو نەدۆزرایەوە.")
        quotation.delete()

    # ===== تایید پیش‌فاکتور ===== #
    @transaction.atomic
    def approve_quotation(self, quotation_id: int) -> Quotation:
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پێشفاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        quotation.status = Quotation.Status.ACCEPTED
        quotation.save(update_fields=['status', 'updated_at'])
        return quotation

    # ===== تغییر وضعیت پیش‌فاکتور ===== #
    @transaction.atomic
    def change_status(self, quotation_id: int, new_status: str) -> Quotation:
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پێشفاکتۆری دیاریکراو نەدۆزرایەوە.")
            
        valid_statuses = [choice[0] for choice in Quotation.Status.choices]
        if new_status not in valid_statuses:
            raise ValidationError(f"دۆخەکە نادروستە. ڕێگەپێدراو: {valid_statuses}")

        quotation.status = new_status
        quotation.save(update_fields=['status', 'updated_at'])
        return quotation