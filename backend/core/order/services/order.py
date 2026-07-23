import uuid
from decimal import Decimal
from typing import List, Dict, Any, Tuple

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from core.models import (
    User, Invoice, Order, OrderStatus, Product, OrderItem, 
    OrderStateLog, ProductFieldChoice, ProductField
)
from core.product.services import ProductPricingDomainService
from ..exceptions import OrderNotFoundException

class OrderService:
    """
    سرویس دامنه مدیریت سفارشات دستی توسط ادمین
    """

    def _generate_order_code(self) -> str:
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    def get_order_by_id(self, order_id: int) -> Order:
        try:
            return Order.objects.select_related(
                'current_status', 'user', 'address'
            ).prefetch_related(
                'order_item_order__product',
                'order_item_order__files'
            ).get(id=order_id)
        except Order.DoesNotExist:
            raise OrderNotFoundException(f"داواکاری بە ناسنامەی {order_id} نەدۆزرایەوە.")

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("داواکاری نەدۆزرایەوە.") 
        return order

    def get_user_orders_summary(self, user_id: int) -> List[Order]:
        user = User.objects.get(id=user_id) 
        return Order.objects.get_user_orders_summary(user)
    
    # ========== CREATE ORDER DIRECT ========== #
    @transaction.atomic
    def create_order_direct(
        self, 
        product_id: int, 
        quantity: int = 1, 
        selected_options: List[Dict[str, Any]] = None,
        user_id: int = None, 
        address_id: int = None,
        recipient_name: str = None, 
        recipient_phone: str = None,
        company_name: str = None, 
        full_address: str = None,
        total_price_override: Decimal = None, 
        type: str = "1",
        **kwargs
    ) -> Order:
        """
        ایجاد سفارش دستی توسط ادمین.
        
        Args:
            product_id: شناسه محصول
            quantity: تعداد
            selected_options: لیست انتخاب‌های کاربر با فرمت:
                [
                    {
                        "field_id": 1,
                        "choice_id": 5  # برای dropdown/single_select
                    },
                    {
                        "field_id": 2,
                        "choice_ids": [7, 8]  # برای multi_select
                    },
                    {
                        "field_id": 3,
                        "value": "متن دلخواه"  # برای text/number
                    }
                ]
            total_price_override: قیمت دستی (اختیاری)
        """
        selected_options = selected_options or []
        user = User.objects.get(pk=user_id) if user_id else None
        
        if address_id:
            from core.models import Address
            try:
                address = Address.objects.select_related('province', 'city').get(pk=address_id)
                if user and address.user_id != user.id:
                    raise ValidationError("این آدرس متعلق به کاربر مشخص‌شده نیست.")
                full_address = f"{address.province.name} - {address.city.name} - {address.address}"
            except Address.DoesNotExist:
                raise ValidationError(f"آدرسی با شناسه {address_id} یافت نشد.")
        elif not full_address:
            province_id = kwargs.get('province_id')
            city_id = kwargs.get('city_id')
            address_text = kwargs.get('address_text') or kwargs.get('address')
            if province_id and city_id and address_text:
                from core.models import Province, City
                try:
                    p_name = Province.objects.get(pk=province_id).name
                    c_name = City.objects.get(pk=city_id).name
                    full_address = f"{p_name} - {c_name} - {address_text}"
                except (Province.DoesNotExist, City.DoesNotExist):
                    pass

        # دریافت وضعیت اولیه
        initial_status = OrderStatus.objects.filter(
            status_type='initial'
        ).order_by('sort_order').first()
        
        if not initial_status:
            initial_status = OrderStatus.objects.first()

        # دریافت محصول با فیلدها و گزینه‌ها
        try:
            product = Product.objects.prefetch_related(
                'fields__field_dict',
                'fields__choices__choice_dict'
            ).get(id=product_id)
        except ObjectDoesNotExist:
            raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")

        user_selections = {}
        for opt in selected_options:
            fid = str(opt['field_id'])
            if 'choice_id' in opt and opt['choice_id'] is not None:
                user_selections[fid] = opt['choice_id']
            elif 'choice_ids' in opt and opt['choice_ids']:
                user_selections[fid] = opt['choice_ids']
            elif 'value' in opt and opt['value'] is not None:
                user_selections[fid] = opt['value']

        calculated_price, configuration = ProductPricingDomainService.calculate_final_price(
            product_id=product_id,
            user_selections=user_selections,
            strict_validation=False
        )

        # قیمت نهایی
        final_total = calculated_price

        # ایجاد سفارش
        order = Order.objects.create(
            user=user,
            address_id=address_id,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name,
            full_address=full_address,
            current_status=initial_status,
            total_price=final_total,
            base_products_price=calculated_price,
            type=type,
            order_code=self._generate_order_code()
        )

        # ایجاد آیتم سفارش
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=calculated_price,
            items=configuration,
            name=product.name,
            description=product.description,
            status='approved'
        )
        
        return order

    # ========== UPDATE ORDER ========== #
    @transaction.atomic
    def update_order_details(self, order_id: int, update_data: Dict[str, Any]) -> Order:
        """
        ویرایش سفارش موجود.

        منطق قیمت:
        - total_price ارسال شد → قیمت دستی، calculate اجرا نمی‌شه
        - total_price نبود ولی product_id یا selected_options بود → calculate_price
        """
        order = self.get_order_by_id(order_id)

        # ===== ۱. فیلدهای پایه‌ی Order ===== #
        order_basic_fields = ['recipient_name', 'recipient_phone', 'full_address', 'company_name']
        for field in order_basic_fields:
            if field in update_data:
                setattr(order, field, update_data[field])

        if 'address_id' in update_data:
            address_id = update_data['address_id']
            order.address_id = address_id
            if address_id:
                from core.models import Address
                try:
                    address = Address.objects.select_related('province', 'city').get(pk=address_id)
                    order.full_address = f"{address.province.name} - {address.city.name} - {address.address}"
                except Address.DoesNotExist:
                    raise ValidationError(f"آدرسی با شناسه {address_id} یافت نشد.")

        # ===== ۲. تشخیص نوع آپدیت ===== #
        has_product          = 'product_id' in update_data
        has_options          = 'selected_options' in update_data
        has_price_override   = (
            'total_price' in update_data
            and update_data['total_price'] is not None
        )

        if has_product or has_options or has_price_override:

            order_item = order.order_item_order.first()

            # ===== ۳. محصول ===== #
            if has_product:
                product_id = update_data['product_id']
                try:
                    product = Product.objects.prefetch_related(
                        'fields__field_dict',
                        'fields__choices'
                    ).get(id=product_id)
                except ObjectDoesNotExist:
                    raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")
            else:
                product = order_item.product if order_item else None

            # ===== ۴. تعیین قیمت نهایی ===== #
            if has_price_override:
                # قیمت دستی → اولویت مطلق، حتی اگه آپشن‌ها هم عوض شدن
                final_price   = update_data['total_price']
                configuration = order_item.items if order_item else None
            else:
                # قیمت خودکار از calculate
                selected_options = update_data.get('selected_options', [])
                user_selections  = {}
                for opt in selected_options:
                    fid = str(opt['field_id'])
                    if opt.get('choice_id') is not None:
                        user_selections[fid] = opt['choice_id']
                    elif opt.get('choice_ids'):
                        user_selections[fid] = opt['choice_ids']
                    elif opt.get('value') is not None:
                        user_selections[fid] = opt['value']

                final_price, configuration = ProductPricingDomainService.calculate_final_price(
                    product_id=product.id,
                    user_selections=user_selections,
                    strict_validation=False
                )

            quantity = update_data.get('quantity', order_item.quantity if order_item else 1)

            # ===== ۵. ذخیره‌ی OrderItem ===== #
            if order_item:
                order_item.quantity = quantity
                order_item.price    = final_price
                order_item.items    = configuration
                if has_product and product:
                    order_item.product = product
                    order_item.name    = product.name
                order_item.save()
            else:
                if not product:
                    raise ValidationError("برای ایجاد آیتم جدید، product_id الزامی است.")
                OrderItem.objects.create(
                    order    = order,
                    product  = product,
                    quantity = quantity,
                    price    = final_price,
                    items    = configuration,
                    name     = product.name,
                    status   = 'approved',
                )

            # ===== ۶. آپدیت قیمت‌های Order ===== #
            order.base_products_price = final_price
            order.total_price         = final_price

        order.save()
        return order
    
    # ========== CHANGE STATUS ========== #
    @transaction.atomic
    def change_order_status(
        self, 
        order_id: int, 
        status_code: str, 
        actor: User, 
        description: str = ""
    ) -> Order:
        """
        تغییر وضعیت تکی با استفاده از status_code
        """
        order = self.get_order_by_id(order_id)
        
        try:
            new_status = OrderStatus.objects.get(internal_code=status_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {status_code} یافت نشد.")
            
        old_status = order.current_status

        if old_status and old_status.id == new_status.id:
            return order

        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])

        OrderStateLog.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            actor=actor,
            description=description
        )
        
        return order
    
    @transaction.atomic
    def bulk_change_status(
        self, 
        order_ids: List[int], 
        status_code: str, 
        actor: User
    ) -> int:
        """
        تغییر وضعیت گروهی
        """
        try:
            new_status = OrderStatus.objects.get(internal_code=status_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {status_code} یافت نشد.")
        
        orders = Order.objects.filter(id__in=order_ids)
        updated_count = 0
        
        for order in orders:
            if order.current_status != new_status:
                self.change_order_status(
                    order.id, 
                    status_code, 
                    actor, 
                    description="تغییر وضعیت گروهی ادمین"
                )
                updated_count += 1
                
        return updated_count

    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, Any]:
        existing_ids = set(Order.objects.filter(id__in=order_ids).values_list('id', flat=True))
        not_found_ids = [oid for oid in order_ids if oid not in existing_ids]

        orders_to_delete = Order.objects.filter(id__in=existing_ids)
        count_to_delete = orders_to_delete.count()
        deleted_ids = list(orders_to_delete.values_list('id', flat=True))

        orders_to_delete.delete()

        return {
            "requested_count": len(order_ids),
            "deleted_count": count_to_delete,
            "skipped_count": len(not_found_ids),
            "deleted_ids": deleted_ids,
            "not_found_ids": not_found_ids,
            "message": f"{count_to_delete} سفارش با موفقیت حذف شدند."
        }
