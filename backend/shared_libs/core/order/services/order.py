# apps/order/services/order_service.py

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
            raise OrderNotFoundException(f"سفارش با شناسه {order_id} یافت نشد")

    def get_order_details(self, user_id: int, order_id: int) -> Order:
        order = Order.objects.get_order_with_items(user_id, order_id)
        if not order:
            raise OrderNotFoundException("سفارش یافت نشد") 
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
                'fields__choices'
            ).get(id=product_id)
        except ObjectDoesNotExist:
            raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")

        # ساخت configuration و محاسبه قیمت
        configuration, calculated_price = self._build_item_configuration(
            product=product,
            quantity=quantity,
            selected_options=selected_options
        )

        # قیمت نهایی
        final_total = total_price_override if total_price_override is not None else calculated_price

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
            items=configuration,  # لیست configuration_summary
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
        """
        order = self.get_order_by_id(order_id)
        
        # ویرایش اطلاعات پایه
        basic_fields = ['recipient_name', 'recipient_phone', 'full_address', 'company_name']
        for field in basic_fields:
            if field in update_data:
                setattr(order, field, update_data[field])

        # ویرایش محصول و مشخصات
        if 'product_id' in update_data:
            product_id = update_data['product_id']
            quantity = update_data.get('quantity', 1)
            selected_options = update_data.get('selected_options', [])

            try:
                product = Product.objects.prefetch_related(
                    'fields__field_dict',
                    'fields__choices'
                ).get(id=product_id)
            except ObjectDoesNotExist:
                raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")

            configuration, calculated_price = self._build_item_configuration(
                product=product,
                quantity=quantity,
                selected_options=selected_options
            )

            # آپدیت آیتم موجود
            order_item = order.order_item_order.first()
            if order_item:
                order_item.product = product
                order_item.quantity = quantity
                order_item.price = calculated_price
                order_item.items = configuration
                order_item.name = product.name
                order_item.description = product.description
                order_item.save()
            else:
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

            order.base_products_price = calculated_price
            
            # قیمت نهایی
            total_override = update_data.get('total_price_override')
            order.total_price = Decimal(str(total_override)) if total_override is not None else calculated_price
        else:
            # فقط قیمت کل تغییر کرده
            total_override = update_data.get('total_price_override')
            if total_override is not None:
                order.total_price = Decimal(str(total_override))

        order.save()
        return order
    
    # ========== CHANGE STATUS ========== #
    @transaction.atomic
    def change_order_status(
        self, 
        order_id: int, 
        internal_code: str, 
        actor: User, 
        description: str = ""
    ) -> Order:
        """
        تغییر وضعیت تکی با استفاده از internal_code
        """
        order = self.get_order_by_id(order_id)
        
        try:
            new_status = OrderStatus.objects.get(internal_code=internal_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {internal_code} یافت نشد.")
            
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
        internal_code: str, 
        actor: User
    ) -> int:
        """
        تغییر وضعیت گروهی
        """
        try:
            new_status = OrderStatus.objects.get(internal_code=internal_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {internal_code} یافت نشد.")
        
        orders = Order.objects.filter(id__in=order_ids)
        updated_count = 0
        
        for order in orders:
            if order.current_status != new_status:
                self.change_order_status(
                    order.id, 
                    internal_code, 
                    actor, 
                    description="تغییر وضعیت گروهی ادمین"
                )
                updated_count += 1
                
        return updated_count

    @transaction.atomic
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, Any]:
        """
        حذف گروهی سفارشات
        """
        deletable_types = ['initial', 'cancel', 'pending']
        
        orders_to_delete = Order.objects.filter(
            id__in=order_ids,
            current_status__status_type__in=deletable_types
        ).exclude(
            Q(invoice__status='finalize') |
            Q(invoice__status='paid_full') |
            Q(invoice__status='paid_partial')
        )

        count_to_delete = orders_to_delete.count()
        deleted_ids = list(orders_to_delete.values_list('id', flat=True))
        
        orders_to_delete.delete()
        
        return {
            "requested_count": len(order_ids),
            "deleted_count": count_to_delete,
            "skipped_count": len(order_ids) - count_to_delete,
            "deleted_ids": deleted_ids,
            "message": f"{count_to_delete} سفارش با موفقیت حذف شدند."
        }

    # ========== HELPER METHOD ========== #
    def _build_item_configuration(
        self, 
        product: Product, 
        quantity: int, 
        selected_options: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Decimal]:
        """
        ساخت configuration_summary و محاسبه قیمت.
        
        Returns:
            (configuration_list, total_price)
        """
        configuration = []
        calculated_price = product.price or Decimal('0.00')

        # ایجاد دیکشنری فیلدها برای دسترسی سریع
        fields_map = {
            field.id: field 
            for field in product.fields.select_related('field_dict').prefetch_related('choices')
        }

        for opt in selected_options:
            field_id = opt.get('field_id')
            
            if field_id not in fields_map:
                raise ValidationError(f"فیلد {field_id} برای این محصول معتبر نیست.")
            
            field = fields_map[field_id]
            field_dict = field.field_dict
            
            config_item = {
                "field_id": field.id,
                "field_title": field_dict.title,
                "field_type": field_dict.field_type,
            }

            # پردازش بر اساس نوع فیلد
            if field_dict.field_type in ['dropdown', 'single_select']:
                choice_id = opt.get('choice_id')
                if not choice_id:
                    raise ValidationError(
                        f"برای فیلد '{field_dict.title}' انتخاب گزینه الزامی است."
                    )
                
                try:
                    choice = field.choices.get(id=choice_id)
                except ObjectDoesNotExist:
                    raise ValidationError(f"گزینه {choice_id} نامعتبر است.")
                
                config_item["value"] = choice.choice_dict.title
                config_item["choice_id"] = choice.id
                
                # اضافه کردن قیمت گزینه
                if choice.numeric_value:
                    calculated_price += choice.numeric_value

            elif field_dict.field_type == 'multi_select':
                choice_ids = opt.get('choice_ids', [])
                if not choice_ids:
                    raise ValidationError(
                        f"برای فیلد '{field_dict.title}' حداقل یک گزینه باید انتخاب شود."
                    )
                
                choices = field.choices.filter(id__in=choice_ids)
                if choices.count() != len(choice_ids):
                    raise ValidationError(f"برخی از گزینه‌های انتخابی نامعتبر هستند.")
                
                config_item["value"] = "، ".join([c.title for c in choices])
                config_item["choices"] = [
                    {"id": c.id, "title": c.title} 
                    for c in choices
                ]
                
                # اضافه کردن قیمت گزینه‌ها
                for c in choices:
                    if c.numeric_value:
                        calculated_price += c.numeric_value

            else:  # text, number, textarea
                text_value = opt.get('value')
                if not text_value:
                    raise ValidationError(
                        f"برای فیلد '{field_dict.title}' مقدار الزامی است."
                    )
                
                config_item["value"] = str(text_value)
                
                # اضافه کردن قیمت فیلد (اگر داشته باشد)
                if field.numeric_value:
                    calculated_price += field.numeric_value
            
            configuration.append(config_item)

        # محاسبه قیمت نهایی با تعداد
        total_price = calculated_price * quantity
        
        return configuration, total_price
