import uuid
from decimal import Decimal
from typing import List, Dict

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

from core.models import User, Invoice, Order, OrderStatus, Product, OrderItem, ProductSize, ProductOptionValue
from ..exceptions import OrderNotFoundException

# ========== ORDER SERVICE ========== #
class OrderService:
    """
    سرویس دامنه مدیریت سفارشات (Checkout, Operations)
    """

    def _generate_order_code(self) -> str:
        return uuid.uuid4().hex[:8].upper()

    def get_order_by_id(self, order_id: int):
        return Order.objects.get_order_by_id(order_id)

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        """
        دریافت جزئیات سفارش برای کاربر.
        """
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد") 
        return order

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        user = User.objects.get(id=user_id) 
        return Order.objects.get_user_orders_summary(user)
    
    @transaction.atomic
    def create_order_direct(self, user_id: int, address_id: int, items_data: List[Dict], total_price_override: float = None) -> Order:
        """
        ایجاد مستقیم سفارش (توسط ادمین) بدون استفاده از سبد خرید.
        """
        # ===== دریافت مشتری ===== #
        user = get_object_or_404(User, pk=user_id)
        # ===== دریافت و اعتبارسنجی وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        if not initial_status:
            initial_status = OrderStatus.objects.first() or OrderStatus.objects.create(name="ثبت اولیه", internal_code="INITIAL_DRAFT")

        # ===== محاسبه قیمت کل ===== #
        calculated_total = Decimal(0)
        prepared_items = []
        # ===== استخراج و ایجاد آیتم ها ===== #
        for item_data in items_data:
            product_slug = item_data.get('product_slug')
            selections = item_data.get('selections', item_data)
            quantity = int(selections.get('quantity', 1))
            # ===== دریافت نام آیتم ===== #
            item_name = selections.get('name', item_data.get('name', None))
            item_description = selections.get('description', item_data.get('description', None))
            # ===== دریافت محصول ===== #
            product = get_object_or_404(Product, slug=product_slug)
            # ===== آماده سازی اطلاعات سفارش ===== #
            specs_json = self._prepare_item_specs_json(product, selections)        
    
            # ===== محاسبه قیمت آیتم ===== #
            if 'item_price' in item_data and item_data['item_price'] is not None:
                line_price = Decimal(str(item_data['item_price']))
            else:
                line_price = product.price * quantity
            
            calculated_total += line_price
            # ===== ایجاد آیتم در یک لیست ===== #
            prepared_items.append({
                'product': product,
                'quantity': quantity,
                'price': line_price,
                'items': specs_json,
                'name': item_name,
                'description': item_description
            })
            # ===== به دست آوردن مبلغ کل ===== #
            final_total = Decimal(str(total_price_override)) if total_price_override is not None else calculated_total
            # ===== ایجاد سفارش ===== #
            order = Order.objects.create(
                user=user,
                address_id=address_id,
                current_status=initial_status,
                total_price=final_total,
                base_products_price=calculated_total,
                type="2",
                order_code=self._generate_order_code()
            )

            # ===== ایجاد آیتم ===== #
            for p_item in prepared_items:
                OrderItem.objects.create(
                    order=order,
                    product=p_item['product'],
                    quantity=p_item['quantity'],
                    price=p_item['price'],
                    items=p_item['items'],
                    status='approved'
                )
                
            return order
        
    def _prepare_item_specs_json(self, product, selections) -> Dict:
        """
        تبدیل ورودی‌های خام (IDها) به ساختار استاندارد JSON برای فیلد items.
        """
        size_id = selections.get('size_id')
        width = selections.get('custom_width', 0)
        height = selections.get('custom_height', 0)
        # ===== دریافت اطلاعات سایز ===== #
        size_name = "Custom"
        if size_id:
            try:
                ps = ProductSize.objects.get(product=product, id=size_id)
                width = float(ps.size.width)
                height = float(ps.size.height)
                size_name = ps.size.name
            except ProductSize.DoesNotExist:
                pass
        # ===== دریافت اطلاعات گزینه ===== #
        option_ids = selections.get('option_value_ids', [])
        options_list = []
        # ===== ایجاد آیتم ===== #
        if option_ids:
            values = ProductOptionValue.objects.filter(id__in=option_ids).select_related('product_option__option')
            for val in values:
                opt_name = val.product_option.label
                if not opt_name and val.product_option.option:
                    opt_name = val.product_option.option.label
                # ===== ایجاد لیست ویژگی ها ===== #
                options_list.append({
                    'option_id': val.product_option.id,
                    'option_label': opt_name or "Unknown Option",
                    'type': 'selection',
                    'value': {
                        'id': val.id,
                        'label': val.label,
                        'price': float(val.price_impact)
                    }
                })
        # ===== بازگشت ===== #
        return {
            "options": options_list,
            "meta": {
                "width": float(width),
                "height": float(height),
                "size_id": size_id,
                "has_design": selections.get('has_design', True)
            }
        }
        
    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی هوشمند سفارشات.
        قانون 1: فقط سفارشاتی که وضعیتشان اجازه حذف می‌دهد.
        قانون 2: سفارشاتی که فاکتور نهایی شده یا پرداخت کامل دارند، حذف نمی‌شوند.
        """
        deletable_types = ['initial', 'cancel', 'pending']
        
        # فیلتر اولیه بر اساس وضعیت
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
