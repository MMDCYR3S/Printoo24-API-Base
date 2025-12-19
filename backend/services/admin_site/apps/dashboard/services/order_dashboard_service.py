from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, Order, OrderItem, OrderStatus, Product, Address
from core.domain.commerce.order import OrderRepository
from core.domain.financial import FinancialDomainService

# ========== ORDER DASHBOARD SERVICE ========== #
class OrderDashboardService:
    """
    سرویس اپلیکیشن برای مدیریت سفارشات در پنل ادمین (داشبورد).
    شامل: ثبت سفارش اختصاصی، ویرایش سفارش، لیست و حذف گروهی.
    """
    def __init__(self):
        self.order_repo = OrderRepository()
        self.financial_service = FinancialDomainService()
        
    # ============ CREATE CUSTOM ORDER ============ #
    @transaction.atomic
    def create_custom_order(self, admin_user: User, data: Dict[str, Any]) -> Order:
        """
        ثبت سفارش اختصاصی توسط ادمین.
        """
        # ===== دریافت شناسه مشتری ===== #
        customer_id = data.get('user_id')
        if not customer_id:
            raise ValidationError("شناسه مشتری الزامی است.")
        # ===== اعتبارسنجی ===== #
        try:
            customer = User.objects.get(id=customer_id)
        except User.DoesNotExist:
            raise ValidationError("مشتری یافت نشد.")
        # ===== دریافت آدرس و اعتبارسنجی ===== #
        address_id = data.get('address_id')
        if address_id:
            address = Address.objects.get(id=address_id)
        else:
            raise ValidationError("آدرس الزامی است.")
        # ===== دریافت وضعیت اولیه ===== #
        initial_status = OrderStatus.objects.get(status_type='initial', group__code='admin')
        # ===== ایجاد سفارش بدون قیمت ===== #
        order = Order.objects.create(
            user=customer,
            address=address,
            current_status=initial_status,
            type="2",
            description=data.get('description', ''),
        )
        # ===== دریافت و افزودن آیتم ها ===== #
        items_data = data.get('items', [])
        total_price = 0
        base_price = 0
        
        for item in items_data:
            product_id = item.get('product_id')
            product = None
            if product_id:
                product = Product.objects.get(id=product_id)
            # ===== دریافت قسمت و تعداد ===== #
            quantity = item.get('quantity', 1)
            unit_price = item.get('price', 0)
            # ===== قیمت گذاری ===== #
            line_total = quantity
            total_price += line_total
            base_price += line_total
            # ===== ساخت آیتم ===== #
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=unit_price,
                items=item.get('features', {}),
                admin_note=item.get('note', '')
            )
        # ===== تعیین قیمت سفارش ===== #
        order.total_price = total_price
        order.base_products_price = base_price
        order.save()
        # ===== ایجاد فاکتور ===== #
        # if data.get('generate_invoice', True):
        #     self.financial_service.issue_invoice_from_order(order, admin_user)

        return order
    
    # ============ UPDATE ORDER ============ #
    @transaction.atomic
    def update_order_details(self, admin_user: User, order_id: int, data: Dict[str, Any]) -> Order:
        """
        ویرایش جزئیات سفارش (مثلاً تغییر آدرس، تغییر قیمت توافقی).
        توجه: آیتم‌ها معمولا جداگانه مدیریت می‌شوند.
        """
        # ===== دریافت سفارش ===== #
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValidationError("سفارش یافت نشد.")
        # ===== دریافت آدرس ===== #
        if 'address_id' in data:
            order.address_id = data['address_id']
        # ===== توضیحات ===== #
        if 'description' in data:
            order.description = data['description']
        # ===== تغییر قیمت ===== #
        if order.type == "2" and 'total_price' in data:
            order.total_price = data['total_price']
            # ===== بروزرسانی قیمت برای فاکتور ===== #
            # if hasattr(order, 'invoice'):
            #     invoice = order.invoice
            #     if not invoice.is_paid:
            #         invoice.final_amount = data['total_price']
            #         invoice.save()

        order.save()
        return order
    
    # ========== DELETE ========== #
    def delete_order(self, order_id: int):
        """
        حذف یک سفارشات براساس شناسه آن
        """
        order = self.order_repo.get_by_id(order_id)
        try:
            self.order_repo.delete(order)
        except Exception as e:
            raise (f"خطا در حذف سفارش: {str(e)}")
    
    # ============ BULK ACTIONS ============ #
    def bulk_delete_orders(self, admin_user: User, order_ids: List[int]):
        """
        حذف گروهی سفارشات (فقط سفارشات لغو شده یا پیش‌نویس).
        """
        # ===== دریافت سفارشات ===== #
        orders = Order.objects.filter(id__in=order_ids)
        deleted_count = 0

        for order in orders:
            # ===== اگر فاکتور داشت، پاک نکن ===== #
            if hasattr(order, 'invoice') and order.invoice.status in ['PAID_FULL', 'PAID_PARTIAL']:
                continue

            if order.is_locked:
                continue

            order.delete()
            deleted_count += 1
            
        return deleted_count
    
    def bulk_change_status(self, admin_user: User, order_ids: List[int], new_status_id: int):
        """
        تغییر وضعیت گروهی.
        برای این سیستم ممکن هست که این قسمت اصلا نیازی نباشه و به کار نیاد.
        """
        status = OrderStatus.objects.get(id=new_status_id)
        updated_count = Order.objects.filter(id__in=order_ids).update(current_status=status)
        return updated_count
    