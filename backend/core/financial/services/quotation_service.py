import uuid
from decimal import Decimal
from django.utils import timezone

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from core.models import Order, OrderStatus, FinancialStatus
from core.order.models import OrderItem
from core.financial.models import Quotation, FinancialLog

class QuotationService:

    def _sync_order_from_quotation(self, order, quotation):
        """
        قانون دامنه: پیش‌فاکتور صاحبِ قیمت اصلی سفارش است.
        بنابراین هر تغییری در total_price پیش‌فاکتور باید مستقیماً روی
        subtotal/base_products_price/total_price سفارش اعمال شود.
        """
        if not order:
            return
        order.subtotal = quotation.total_price
        order.base_products_price = quotation.total_price
        order.total_price = quotation.total_price
        order.save()


    # ===== ایجاد پیش‌فاکتور جدید ===== #
    @transaction.atomic
    def create_quotation(self, order_id: int, data: dict, user) -> Quotation:
        order = Order.objects.filter(id=order_id).first()
        if not order:
            raise NotFound("داواکاریی دیاریکراو نەدۆزرایەوە.")

        if Quotation.objects.filter(converted_order=order).exists():
            raise ValidationError("برای این سفارش قبلاً پیش‌فاکتور صادر شده است.")

        q_number = f"QTE-{order.order_code if order.order_code else uuid.uuid4().hex[:8].upper()}"

        total_price = data.get('total_price', order.total_price)

        quotation = Quotation.objects.create(
            quotation_number=q_number,
            created_by=user,
            converted_order=order,
            customer_name=data.get('customer_name', order.recipient_name),
            product_name=data.get('product_name', ''),
            product_snapshot=data.get('product_snapshot', {}),
            quantity=data.get('quantity', 1),
            estimated_delivery_date=data.get('estimated_delivery_date'),
            total_price=total_price,
            valid_until=data.get('valid_until'),
        )

        self._sync_order_from_quotation(order, quotation)

        FinancialLog.log(
            action_type=FinancialLog.ActionType.QUOTATION_CREATED,
            order=order,
            user=order.user,
            description=f"ایجاد پیش‌فاکتور {quotation.quotation_number}",
            created_by=user,
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
        quotation = Quotation.objects.select_related('converted_order').filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پیش‌فاکتور مورد نظر یافت نشد.")

        old_values = {
            'total_price': str(quotation.total_price),
            'status': quotation.status,
        }

        # فقط فیلدهای مجاز
        editable_fields = [
            'customer_name', 'product_name', 'product_image',
            'product_snapshot', 'quantity',
            'estimated_delivery_date', 'total_price', 'valid_until'
        ]
        changed = False
        for field in editable_fields:
            if field in data:
                setattr(quotation, field, data[field])
                changed = True

        if not changed:
            return quotation

        quotation.save()

        # اگر پیش‌فاکتور به سفارش تبدیل شده، قیمت سفارش باید همگام شود
        if quotation.converted_order:
            self._sync_order_from_quotation(quotation.converted_order, quotation)

        FinancialLog.log(
            action_type=FinancialLog.ActionType.PRICE_UPDATED,
            order=quotation.converted_order,
            user=quotation.converted_order.user if quotation.converted_order else None,
            field_name='quotation_price',
            old_value=old_values,
            new_value={'total_price': str(quotation.total_price), 'status': quotation.status},
            description=f"ویرایش پیش‌فاکتور {quotation.quotation_number}",
            created_by=quotation.created_by,
        )

        return quotation

    def _sync_price_to_order(self, quotation: Quotation):
        """اعمال قیمت پیش‌فاکتور روی سفارشِ متصل (قیمت اصلی + قیمت آیتم)."""
        order = quotation.converted_order
        if not order:
            return

        quantity = quotation.quantity or 1
        total = quotation.total_price or 0
        unit_price = (total / Decimal(quantity)) if quantity else total

        order.subtotal = total
        order.total_price = total
        order.base_products_price = total
        # final_price و remaining_amount به‌صورت خودکار محاسبه می‌شوند
        order.save()

        # ===== همگام‌سازی قیمت واحدِ آیتم‌های سفارش ===== #
        OrderItem.objects.filter(order=order).update(price=unit_price)

        FinancialLog.log(
            action_type=FinancialLog.ActionType.PRICE_UPDATED,
            order=order,
            user=order.user,
            description=f"تغییر قیمت سفارش {order.order_code} بر اساس پیش‌فاکتور {quotation.quotation_number} به {total:,} IQD",
            new_value={'total_price': str(total), 'quantity': quantity},
            created_by=quotation.created_by,
        )

    # ===== حذف پیش‌فاکتور ===== #
    @transaction.atomic
    def delete_quotation(self, quotation_id: int):
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پێشفاکتۆری دیاریکراو نەدۆزرایەوە.")
        quotation.delete()

    # ===== تایید پیش‌فاکتور ===== #
    # ===== تأیید پیش‌فاکتور توسط مشتری ===== #
    @transaction.atomic
    def approve_quotation(self, quotation_id: int, user=None) -> Quotation:
        quotation = Quotation.objects.select_related('converted_order__user').filter(id=quotation_id).first()
        if not quotation:
            raise NotFound("پیش‌فاکتور مورد نظر یافت نشد.")

        if quotation.status == Quotation.Status.ACCEPTED:
            return quotation

        # ===== بررسی مالکیت ===== #
        order = quotation.converted_order
        if not order:
            raise ValidationError("سفارش مرتبط یافت نشد.")
        if user and order.user and order.user != user:
            raise ValidationError("شما مجاز به تأیید این پیش‌فاکتور نیستید.")

        # ===== تغییر وضعیت پیش‌فاکتور ===== #
        quotation.status = Quotation.Status.ACCEPTED
        quotation.save(update_fields=['status', 'updated_at'])

        # ===== به‌روزرسانی وضعیت سفارش ===== #
        customer_approved_status = OrderStatus.objects.filter(
            internal_code__iexact='customer_approved'
        ).first()
        if not customer_approved_status:
            # اگر وضعیت سیستمی یافت نشد، از اولین وضعیت تأیید استفاده می‌کنیم
            customer_approved_status = OrderStatus.objects.filter(
                status_type='approve'
            ).order_by('sort_order').first()
        if not customer_approved_status:
            raise ValidationError("وضعیت تأیید مشتری یافت نشد.")

        order.current_status = customer_approved_status
        order.financial_status = FinancialStatus.AWAITING_DEPOSIT

        # ===== تعیین مهلت پرداخت (مثلاً ۳ روز) ===== #
        order.payment_deadline = timezone.now() + timezone.timedelta(days=3)

        # ===== تعیین مبلغ پیش‌پرداخت (۳۰٪ از مبلغ نهایی) ===== #
        if order.deposit_required <= 0:
            order.deposit_required = int(order.final_price * Decimal('0.3'))

        # ===== ذخیره بدون تغییر خودکار وضعیت مالی ===== #
        order.save(skip_financial_status=True)

        # ===== ثبت لاگ مالی ===== #
        FinancialLog.log(
            action_type=FinancialLog.ActionType.QUOTATION_APPROVED,
            order=order,
            user=order.user,
            description=f"تأیید پیش‌فاکتور {quotation.quotation_number} توسط مشتری",
            new_value={
                'quotation_id': quotation.id,
                'quotation_status': quotation.status,
                'order_financial_status': order.financial_status,
            },
            created_by=user or order.user,
        )

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