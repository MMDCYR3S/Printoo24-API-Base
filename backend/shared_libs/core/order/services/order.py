import uuid
from decimal import Decimal
from typing import List, Dict, Any

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from core.models import User, Invoice, Order, OrderStatus, Product, OrderItem, ProductSize, ProductOptionValue, Address
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
        """
        # ===== دریافت مشتری ===== #
        if user_id:
            user = User.objects.get(pk=user_id)
        else:
            user = None
        
        # ===== اعتبارسنجی ===== #
        if address_id:
            address = Address.objects.get(pk=address_id)
        else: 
            address = None
            
        # ===== دریافت و اعتبارسنجی وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        if not initial_status:
            initial_status = OrderStatus.objects.first() or OrderStatus.objects.create(
                name="ثبت اولیه", 
                internal_code="INITIAL_DRAFT",
                status_type='initial'
            )
            
        # ===== محاسبه قیمت کل ===== #
        calculated_total = Decimal(0)
        prepared_items = []
        # ===== استخراج و ایجاد آیتم ها ===== #
        for item_data in items_data:
            product_slug = item_data.get('product_slug')
            selections = item_data.get('selections', {}) 
            quantity = int(selections.get('quantity', 1))
            
            # ===== دریافت نام آیتم ===== #
            product = None
            item_name = selections.get('name', item_data.get('name'))
            item_description = selections.get('description', item_data.get('description'))
            # ===== دریافت محصول ===== #
            if product_slug:
                try:
                    product = Product.objects.get(slug=product_slug)
                except ObjectDoesNotExist:
                    raise ValidationError(f"محصولی با شناسه {product_slug} یافت نشد.")
                
                if not item_name:
                        item_name = product.name
                unit_price = product.price
            else:
                if not item_name:
                    raise ValidationError("برای آیتم‌های بدون محصول، وارد کردن `name` الزامی است")
                pass
            # ===== آماده سازی اطلاعات سفارش ===== #
            specs_json = {}
            
            if product:
                 specs_json = self._prepare_item_specs_json(product, selections)
            elif isinstance(selections, dict):
                safe_selections = selections.copy() if isinstance(selections, dict) else {}
                # ===== فیلدهای ثابت ===== #
                safe_selections.pop('quantity', None)
                safe_selections.pop('name', None)
                safe_selections.pop('description', None)
                safe_selections.pop('item_price', None)
                
                specs_json = safe_selections

            line_price = None

            # ===== محاسبه قیمت آیتم ===== #
            if 'item_price' in item_data and item_data['item_price'] is not None:
                line_price = Decimal(str(item_data['item_price']))
            elif 'price' in item_data and item_data['price'] is not None:
                # ===== قیمت دستی آیتم ===== #
                line_price = Decimal(str(item_data['price']))
            elif product:
                # ===== در صورت بودن محصول و قیمت ===== #
                line_price = product.price * quantity
            else:
                # ===== نبود محصول و قیمت ===== #
                raise ValidationError(f"برای آیتم '{item_name}' قیمت مشخص نشده است.")
            
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
        # ===== ایجاد آیتم ===== #
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
