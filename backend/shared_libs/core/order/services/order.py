import uuid
from decimal import Decimal
from typing import List, Dict, Any

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from core.models import User, Invoice, Order, OrderStatus, Product, OrderItem, OrderStateLog, ProductFieldChoice, ProductField
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
    def create_order_direct(self, product_id: int, quantity: int = 1, has_design: bool = True, selected_options: list = None,
                            user_id: int = None, address_id: int = None,
                            recipient_name: str = None, recipient_phone: str = None,
                            company_name: str = None, full_address: str = None,
                            total_price_override: float = None, type: str = "1", **kwargs) -> Order:
        
        selected_options = selected_options or []
        user = User.objects.get(pk=user_id) if user_id else None
        
        initial_status = OrderStatus.objects.filter(status_type='initial').first()
        if not initial_status:
            initial_status = OrderStatus.objects.first()

        try:
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")

        # ساخت مشخصات با کمک متد _build_item_specifications (که در پاسخ قبل تعریف کردیم)
        specifications, line_price = self._build_item_specifications(product, quantity, has_design, selected_options)

        final_total = Decimal(str(total_price_override)) if total_price_override is not None else line_price

        order = Order.objects.create(
            user=user,
            address_id=address_id,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name,
            full_address=full_address,
            current_status=initial_status,
            total_price=final_total,
            base_products_price=line_price,
            type=type,
            order_code=self._generate_order_code()
        )

        OrderItem.objects.create(
            order=order, product=product, quantity=quantity, price=line_price,
            items=specifications, name=product.name, description=product.description, status='approved'
        )
        
        return order

    @transaction.atomic
    def update_order_details(self, order_id: int, update_data: dict) -> Order:
        order = self.get_order_by_id(order_id)
        
        # 1. ویرایش اطلاعات پایه
        basic_fields = ['recipient_name', 'recipient_phone', 'full_address']
        for field in basic_fields:
            if field in update_data:
                setattr(order, field, update_data[field])

        # 2. بررسی ویرایش محصولِ تکیِ سفارش
        if 'product_id' in update_data:
            product_id = update_data['product_id']
            quantity = update_data.get('quantity', 1)
            has_design = update_data.get('has_design', True)
            selected_options = update_data.get('selected_options', [])

            try:
                product = Product.objects.get(id=product_id)
            except ObjectDoesNotExist:
                raise ValidationError(f"محصولی با شناسه {product_id} یافت نشد.")

            specifications, line_price = self._build_item_specifications(product, quantity, has_design, selected_options)

            # واکشی تنها آیتم موجود در سفارش و آپدیت آن
            order_item = order.order_item_order.first()
            if order_item:
                order_item.product = product
                order_item.quantity = quantity
                order_item.price = line_price
                order_item.items = specifications
                order_item.name = product.name
                order_item.description = product.description
                order_item.save()
            else:
                OrderItem.objects.create(
                    order=order, product=product, quantity=quantity, price=line_price,
                    items=specifications, name=product.name, description=product.description, status='approved'
                )

            total_override = update_data.get('total_price_override')
            order.base_products_price = line_price
            order.total_price = Decimal(str(total_override)) if total_override is not None else line_price
        else:
            total_override = update_data.get('total_price_override')
            if total_override is not None:
                order.total_price = Decimal(str(total_override))

        order.save()
        return order
    
    @transaction.atomic
    def change_order_status(self, order_id: int, internal_code: str, actor: User, description: str = "") -> Order:
        """ تغییر وضعیت تکی با استفاده از internal_code """
        order = self.get_order_by_id(order_id)
        
        try:
            new_status = OrderStatus.objects.get(internal_code=internal_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {internal_code} یافت نشد.")
            
        old_status = order.current_status

        # اگر وضعیت فعلی با وضعیت جدید یکی بود، کاری نکن
        if old_status and old_status.id == new_status.id:
            return order

        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])

        # ===== ایجاد لاگ تغییر وضعیت ===== #
        OrderStateLog.objects.create(
            order=order,
            from_status=old_status,
            to_status=new_status,
            actor=actor,
            description=description
        )
        return order
    
    @transaction.atomic
    def bulk_change_status(self, order_ids: list, internal_code: str, actor: User) -> int:
        """ تغییر وضعیت گروهی با استفاده از internal_code """
        orders = Order.objects.filter(id__in=order_ids)
        
        try:
            # بررسی اینکه آیا وضعیت اصلا وجود داره یا نه
            new_status = OrderStatus.objects.get(internal_code=internal_code)
        except ObjectDoesNotExist:
            raise ValidationError(f"وضعیتی با کد سیستمی {internal_code} یافت نشد.")
        
        updated_count = 0
        for order in orders:
            if order.current_status != new_status:
                # اینجا داریم internal_code رو پاس میدیم به متد بالایی
                self.change_order_status(order.id, internal_code, actor, description="تغییر وضعیت گروهی ادمین")
                updated_count += 1
                
        return updated_count
    @transaction.atomic
    def bulk_change_status(self, order_ids: list, internal_code: str, actor: User) -> int:
        """ تغییر وضعیت گروهی """
        orders = Order.objects.filter(id__in=order_ids)
        new_status = OrderStatus.objects.get(internal_code=internal_code)
        
        updated_count = 0
        for order in orders:
            if order.current_status != new_status:
                self.change_order_status(order.id, internal_code, actor, description="تغییر وضعیت گروهی ادمین")
                updated_count += 1
                
        return updated_count

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

    # ===== HELPER METHODS ===== #
    def _build_item_specifications(self, product, quantity, has_design, selected_options):
        """ این تابع JSON آپشن‌ها و قیمت خط را به صورت امن می‌سازد """
        specifications = {
            "width": None,
            "height": None,
            "has_design": has_design,
            "options": []
        }
        calculated_item_price = product.price or Decimal('0.00')

        for opt in selected_options:
            field_id = opt.get('field_id')
            try:
                field = ProductField.objects.get(id=field_id, product=product)
            except ObjectDoesNotExist:
                raise ValidationError(f"فیلدی با شناسه {field_id} معتبر نیست.")

            opt_data = {
                "field_id": field.id,
                "field_title": field.title,
                "field_type": field.field_type,
            }

            if field.field_type in ['dropdown', 'single_select']:
                choice_id = opt.get('choice_id')
                if not choice_id:
                    raise ValidationError(f"برای فیلد {field.title} انتخاب گزینه الزامی است.")
                
                choice = ProductFieldChoice.objects.filter(id=choice_id, field=field).first()
                if not choice:
                    raise ValidationError(f"گزینه {choice_id} نامعتبر است.")
                    
                opt_data["choice_id"] = choice.id
                opt_data["choice_title"] = choice.title
                opt_data["value"] = choice.title
                calculated_item_price += (choice.numeric_value or Decimal('0.00'))

            elif field.field_type == 'multi_select':
                choice_ids = opt.get('choice_ids', [])
                choices = ProductFieldChoice.objects.filter(id__in=choice_ids, field=field)
                opt_data["choices"] = [{"id": c.id, "title": c.title} for c in choices]
                opt_data["value"] = "، ".join([c.title for c in choices])
                for c in choices:
                    calculated_item_price += (c.numeric_value or Decimal('0.00'))

            else:
                text_value = opt.get('value')
                opt_data["value"] = text_value
                calculated_item_price += (field.numeric_value or Decimal('0.00'))
            
            specifications["options"].append(opt_data)

        line_price = calculated_item_price * quantity
        return specifications, line_price

