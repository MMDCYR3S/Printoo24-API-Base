import uuid
from decimal import Decimal
from typing import List, Dict

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError

from core.models import User, Invoice, Order, OrderStatus, Product, OrderItem, ProductSize, ProductOptionValue, Address
from ..exceptions import OrderNotFoundException

# ========== ORDER SERVICE ========== #
class OrderService:
    """
    سرویس دامنه مدیریت سفارشات (Checkout, Operations)
    """

    def _resolve_address_data(self, address_id: int = None, manual_full_address: str = None):
        """
        منطق تصمیم‌گیری آدرس:
        ۱. اگر ID باشد: آبجکت آدرس را می‌گیرد و متن آن را هم استخراج می‌کند (Snapshot).
        ۲. اگر ID نباشد: آبجکت آدرس None می‌شود و متن دستی استفاده می‌شود.
        """
        final_address_obj = None
        final_address_text = manual_full_address
        
        if address_id:
            # ===== دریافت آدرس و ذخیره آن در آدرس کل ===== #
            address_obj = get_object_or_404(Address, pk=address_id)
            final_address_obj = address_obj
            final_address_text = f"{address_obj.province.name}، {address_obj.city.name}، {address_obj.address} - کدپستی: {address_obj.postal_code}"
        
        return final_address_obj, final_address_text

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
    
    # ========== CREATE ORDER DIRECT ========== #
    @transaction.atomic
    def create_order_direct(self, items_data: List[Dict], user_id: int = None ,
                            address_id: int = None, full_address: str = None, 
                            total_price_override: float = None,
                            recipient_name: str = None,
                            recipient_phone: str = None,
                            company_name: str = None) -> Order:
        """ ساخت سفارش """

        # ===== دریافت مشتری ===== #
        user = None
        if user_id:
            user = get_object_or_404(User, pk=user_id)

        # ===== حل و فصل آدرس ===== #
        addr_obj, addr_text = self._resolve_address_data(address_id, full_address)

        # ===== دریافت و اعتبارسنجی وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.filter(status_type='progress').first()
        if not initial_status:
            initial_status = OrderStatus.objects.first()

        # ===== ایجاد هدر سفارش ===== #
        order = Order.objects.create(
            user=user,
            order_code=self._generate_order_code(),
            current_status=initial_status,
            type="2",
            # ===== آدرس ===== #
            address=addr_obj,
            full_address=addr_text,
            # ===== اطلاعات دریافت کننده ===== #
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name
        )
        
        # ===== افزودن آیتم‌ها ===== #
        for item_data in items_data:
            self.add_item_to_order(order, item_data)
            
        # ===== اعمال قیمت دستی (Override) ===== #
        if total_price_override is not None:
            order.total_price = Decimal(str(total_price_override))
            order.save(update_fields=['total_price'])

        return order

    # ========== UPDATE ORDER FIELDS ========== #
    def update_order_fields(self, order: Order, data: Dict) -> Order:
        """
        ویرایش فیلدهای اصلی سفارش (بدون تغییر وضعیت).
        """
        # ===== لاجیک آدرس در آپدیت ===== #
        if 'address_id' in data or 'full_address' in data:
            new_addr_id = data.get('address_id') or order.address_id
            
            passed_id = data.get('address_id')
            passed_text = data.get('full_address')
            
            if passed_id:
                addr_obj, addr_text = self._resolve_address_data(address_id=passed_id)
                order.address = addr_obj
                order.full_address = addr_text
                
            elif passed_text is not None: 
                order.address = None
                order.full_address = passed_text
        
        # ===== فیلدهای اطلاعاتی ===== #
        if 'recipient_name' in data:
            order.recipient_name = data['recipient_name']
        if 'recipient_phone' in data:
            order.recipient_phone = data['recipient_phone']
        if 'company_name' in data:
            order.company_name = data['company_name']
        if 'order_code' in data:
             order.order_code = data['order_code']
             
        # ===== تغییر نوع سفارش ===== #
        if 'type' in data:
            order.type = data['type']
            
        order.save()
        return order
        
    # ========== CHANGE ORDER STATUS ========== #
    def change_order_status(self, order: Order, new_status_id: int) -> Order:
        """
        تغییر وضعیت سفارش.
        """
        new_status = get_object_or_404(OrderStatus, pk=new_status_id)

        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])
        return order
        
    def _prepare_item_specs_json(self, product: Product, selections: Dict) -> Dict:
        """
        تبدیل ورودی‌ها به JSON استاندارد با در نظر گرفتن مدل‌های Size و ProductSize.
        """
        size_id = selections.get('size_id')
        width = selections.get('custom_width', 0)
        height = selections.get('custom_height', 0)
        
        resolved_size_name = "Custom Size"
        # ===== دریافت اطلاعات سایز ===== #
        if size_id:
            try:
                ps = ProductSize.objects.select_related('size').get(id=size_id, product=product)
                width = float(ps.size.width)
                height = float(ps.size.height)
                resolved_size_name = ps.size.name
            except ProductSize.DoesNotExist:
                pass
            
        # ===== سایز دلخواه ===== #
        elif width and height:
            resolved_size_name = f"{width}x{height}"
            if hasattr(product, 'pricing_config') and not product.pricing_config.accepts_custom_dimensions:
                 raise ValidationError(f"محصول {product.name} ابعاد دلخواه نمی‌پذیرد.")
            
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
                "size_id": size_id,
                "size_name": resolved_size_name,
                "width": float(width),
                "height": float(height),
                "has_design": selections.get('has_design', True)
            },
        }
    
    # ========== ADD ORDER ITEM ========== #
    @transaction.atomic
    def add_item_to_order(self, order: Order, item_data: Dict) -> OrderItem:
        """
        منطق مرکزی افزودن آیتم به سفارش (استفاده شده در ایجاد و ویرایش).
        """
        product_slug = item_data.get('product_slug')
        selections = item_data.get('selections', item_data)
        quantity = int(selections.get('quantity', 1))
        
        product = get_object_or_404(Product, slug=product_slug)
        
        # ===== محاسبه قیمت آیتم ===== #
        if 'item_price' in item_data and item_data['item_price'] is not None:
            line_price = Decimal(str(item_data['item_price']))
        else:
            line_price = product.price * quantity
            
        # ===== ساخت JSON مشخصات ===== #
        specs_json = self._prepare_item_specs_json(product, selections)

        # ===== ایجاد رکورد ===== #
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=line_price,
            status='approved',
            items=specs_json,
            name=selections.get('name', item_data.get('name', product.name)),
            description=selections.get('description', item_data.get('description'))
        )
        
        # ===== بروزرسانی قیمت کل سفارش ===== #
        self.recalculate_order_totals(order)
        return item
    
    # ========== UPDATE EXISTING ITEM ========== #
    @transaction.atomic
    def update_existing_item(self, item: OrderItem, data: Dict) -> OrderItem:
        """
        ویرایش کامل یک آیتم موجود.
        شامل: تغییر تعداد، تغییر قیمت دستی، تغییر توضیحات و حتی تغییر ویژگی‌ها.
        """
        # ===== آپدیت فیلدهای متنی ساده ===== #
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'admin_note' in data:
            item.admin_note = data['admin_note']
            
        # ===== آپدیت تعداد ===== #
        quantity_changed = False
        if 'quantity' in data:
            new_qty = int(data['quantity'])
            if item.quantity != new_qty:
                item.quantity = new_qty
                quantity_changed = True
                
        # ===== آپدیت انتخابات کاربر ===== #
        if 'selections' in data:
            new_specs = self._prepare_item_specs_json(item.product, data['selections'])
            item.items = new_specs
            
        # ===== محاسبه قیمت ===== #
        if 'item_price' in data and data['item_price'] is not None:
            item.price = Decimal(str(data['item_price']))
        elif quantity_changed:
            item.price = item.product.price * item.quantity

        item.save()
        
        # ===== محاسبه قیمت کل سفارش ===== #
        self.recalculate_order_totals(item.order)
        
        return item

    # ========== RECALCULATE ORDER TOTALS ========== #
    def recalculate_order_totals(self, order: Order):
        """
        محاسبه مجدد قیمت کل سفارش بر اساس آیتم‌ها.
        """
        total = order.order_item_order.aggregate(sum=Sum('price'))['sum'] or 0
        order.base_products_price = total
        order.total_price = total
        order.save(update_fields=['total_price', 'base_products_price'])

    # ========== BULK DELETE ========== #    
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
