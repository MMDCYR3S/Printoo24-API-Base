import uuid
from decimal import Decimal
from typing import List, Dict, Any

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from core.models import User, Invoice, Order, OrderStatus, Product, OrderItem, Address
from ..exceptions import OrderNotFoundException

# ========== ORDER SERVICE ========== #
class OrderService:
    """
    سرویس دامنه مدیریت سفارشات (Checkout, Operations)
    """

    def _generate_order_code(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    def get_order_by_id(self, order_id: int):
        return Order.objects.get_order_by_id(order_id)

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد")
        return order

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        user = User.objects.get(id=user_id)
        return Order.objects.get_user_orders_summary(user)

    # ===== CUSTOM ORDER CREATION ===== #
    @transaction.atomic
    def create_order_direct(self,
                            items_data: List[Dict[str, Any]],
                            user_id: int = None,
                            address_id: int = None,
                            recipient_name: str = None,
                            recipient_phone: str = None,
                            company_name: str = None,
                            full_address: str = None,
                            total_price_override: float = None,
                            type: str = "2"
                            ) -> Order:
        """
        ایجاد مستقیم سفارش (توسط ادمین) بدون استفاده از سبد خرید.
        برای آیتم‌های با محصول، از CartProcessor استفاده می‌شود
        تا قیمت و items دقیقاً مثل سبد خرید محاسبه شوند.
        """
        # ===== دریافت مشتری ===== #
        if user_id:
            user = User.objects.get(pk=user_id)
        else:
            user = None

        # ===== اعتبارسنجی آدرس ===== #
        if address_id:
            address = Address.objects.get(pk=address_id)
        else:
            address = None

        # ===== دریافت وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        if not initial_status:
            initial_status = OrderStatus.objects.first() or OrderStatus.objects.create(
                name="ثبت اولیه",
                internal_code="INITIAL_DRAFT",
                status_type='initial'
            )

        calculated_total = Decimal(0)
        prepared_items = []

        for item_data in items_data:
            product_slug = item_data.get('product_slug')
            selections = item_data.get('selections') or {}
            quantity = int(selections.get('quantity', 1))

            product = None
            item_name = item_data.get('name') or selections.get('name')
            item_description = item_data.get('description') or selections.get('description')

            if product_slug:
                try:
                    product = Product.objects.get(slug=product_slug)
                except ObjectDoesNotExist:
                    raise ValidationError(f"محصولی با شناسه '{product_slug}' یافت نشد.")

                if not item_name:
                    item_name = product.name
            else:
                if not item_name:
                    raise ValidationError("برای آیتم‌های بدون محصول، وارد کردن 'name' الزامی است.")

            # ===== محاسبه قیمت و items ===== #
            if product:
                # ===== آیتم با محصول: از CartProcessor استفاده می‌کنیم ===== #
                # دقیقاً مثل AddToCartService
                processor = CartProcessor(product, selections).process()
                specs_json = processor.result_item_data

                if not item_name:
                    item_name = processor.result_name or product.name
                if not item_description:
                    item_description = processor.result_description

                # ===== قیمت دستی ادمین override می‌کند، وگرنه از processor ===== #
                if 'item_price' in item_data and item_data['item_price'] is not None:
                    line_price = Decimal(str(item_data['item_price']))
                elif 'price' in item_data and item_data['price'] is not None:
                    line_price = Decimal(str(item_data['price']))
                else:
                    line_price = processor.result_price * quantity

            else:
                # ===== آیتم دستی بدون محصول ===== #
                if 'item_price' in item_data and item_data['item_price'] is not None:
                    line_price = Decimal(str(item_data['item_price']))
                elif 'price' in item_data and item_data['price'] is not None:
                    line_price = Decimal(str(item_data['price']))
                else:
                    raise ValidationError(f"برای آیتم '{item_name}' قیمت مشخص نشده است.")

                safe_selections = {k: v for k, v in selections.items()
                                   if k not in ('quantity', 'name', 'description', 'item_price')}
                specs_json = safe_selections

            calculated_total += line_price

            prepared_items.append({
                'product': product,
                'quantity': quantity,
                'price': line_price,
                'items': specs_json,
                'name': item_name,
                'description': item_description
            })

        final_total = Decimal(str(total_price_override)) if total_price_override is not None else calculated_total

        order = Order.objects.create(
            user=user,
            address_id=address_id,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name,
            full_address=full_address,
            current_status=initial_status,
            total_price=final_total,
            base_products_price=calculated_total,
            type=type,
            order_code=self._generate_order_code()
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
                items=item['items'],
                name=item['name'],
                description=item['description'],
                status='approved'
            )
            for item in prepared_items
        ])

        order._created_by_admin = True
        order.save()

        return order

    ###################################

    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی هوشمند سفارشات.
        قانون 1: فقط سفارشاتی که وضعیتشان اجازه حذف می‌دهد.
        قانون 2: سفارشاتی که فاکتور نهایی شده یا پرداخت کامل دارند، حذف نمی‌شوند.
        """
        deletable_types = ['initial', 'cancel', 'pending']

        orders_to_delete = Order.objects.filter(
            id__in=order_ids,
            current_status__status_type__in=deletable_types
        )

        orders_to_delete = orders_to_delete.exclude(
            Q(invoice__status='finalize') |
            Q(invoice__status='paid_full') |
            Q(invoice__status='paid_partial')
        )

        count_to_delete = orders_to_delete.count()
        deleted_ids = list(orders_to_delete.values_list('id', flat=True))

        if 'Invoice' in globals() or 'Invoice' in locals():
            Invoice.objects.filter(order__in=orders_to_delete).delete()

        orders_to_delete.delete()

        return {
            "requested_count": len(order_ids),
            "deleted_count": count_to_delete,
            "skipped_count": len(order_ids) - count_to_delete,
            "deleted_ids": deleted_ids,
            "message": f"{count_to_delete} سفارش با موفقیت حذف شدند."
        }
