import os
import logging
import uuid
from typing import Dict, List
from decimal import Decimal
from kombu.exceptions import OperationalError

from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.exceptions import ValidationError

from core.models import (
    Order, OrderItem,
    OrderItemFile
)
from core.order.services import OrderService

try:
    from apps.dashboard.tasks import upload_order_item_file_task
except ImportError:
    upload_order_item_file_task = None

logger = logging.getLogger('dashboard.services.order_dashboard')

class OrderDashboardService:
    def __init__(self):
        self.order_domain = OrderService()
        self.temp_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_order_uploads'))

    # ===== LIST ORDERS ===== #
    def get_orders_list(self, filters: Dict = None):
        """
        دریافت لیست سفارشات با قابلیت فیلترینگ پیشرفته برای داشبورد.
        """
        queryset = Order.objects.select_related(
            'user__customer_profile', 
            'current_status', 
            'current_status__group'
        ).prefetch_related('order_item_order').order_by('-created_at')
        
        if filters:
            # ===== فیلتر جستجو (کد، نام کاربر، موبایل) ===== #
            if search := filters.get('search'):
                queryset = queryset.filter(
                    Q(order_code__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(user__customer_profile__last_name__icontains=search) |
                    Q(recipient_phone__icontains=search)
                )
            
            # ===== فیلتر بازه زمانی ===== #
            if date_from := filters.get('date_from'):
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to := filters.get('date_to'):
                queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    # ===== لیست و جزئیات ===== #
    def get_all_orders_queryset(self):
        """
        لیست تمام سفارشات با جزئیات لازم برای جدول داشبورد.
        """
        return Order.objects.select_related('user__customer_profile', 'current_status')\
            .prefetch_related('order_item_order')\
            .order_by('-created_at')

    def get_order_detail(self, order_id: int):
        """
        دریافت جزئیات کامل سفارش (با فایل‌ها و آیتم‌ها).
        """
        return self.order_domain.get_order_by_id(order_id) 

    # ===== ایجاد سفارش مستقیم (Direct Order) ===== #
    def create_admin_order(self, items_data: List[Dict], user_id: int = None, 
                           address_id: int = None, full_address: str = None, 
                           total_price_override: float = None,
                           recipient_name: str = None,
                           recipient_phone: str = None,
                           company_name: str = None):
        """
        ایجاد سفارش جدید از پنل ادمین.
        """
        
        user_log = f"User {user_id}" if user_id else "GUEST"
        logger.info(f"Dashboard: Creating order for {user_log}")
        
        return self.order_domain.create_order_direct(
            user_id=user_id,
            items_data=items_data,
            address_id=address_id,
            full_address=full_address,
            total_price_override=total_price_override,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            company_name=company_name
        )

    # ===== Update Operations ===== #
    @transaction.atomic
    def update_full_order(self, order_id: int, data: Dict):
        """
        ویرایش اطلاعات عمومی (آدرس، نوع، قیمت کل).
        """
        logger.info(f"Updating Full Order {order_id}")
        order = self.order_domain.get_order_by_id(order_id)
        
        self.order_domain.update_order_fields(order, data)
        
        # ===== ویرایش آیتم ها ===== #
        if 'items' in data and isinstance(data['items'], list):
           for item_data in data['items']:
                if 'id' in item_data and item_data['id']:
                    try:
                        item = OrderItem.objects.get(pk=item_data['id'], order=order)
                        self.order_domain.update_existing_item(item, item_data)
                    except OrderItem.DoesNotExist:
                        pass
                elif 'product_slug' in item_data:
                    self.order_domain.add_item_to_order(order, item_data)
                    
        # ===== ویرایش قیمت کل ===== #
        if 'total_price' in data and data['total_price'] is not None:
            order.total_price = Decimal(str(data['total_price']))
            order.save(update_fields=['total_price'])
        
        # ===== ویرایش سفارش ===== #
        logger.info(f"Order {order_id} updated successfully.")
        return order

    # ===== ORDER ITEM OPERATIONS ===== #
    def add_item_to_order(self, order_id: int, item_data: Dict):
        """
        افزودن آیتم. تمام منطق محاسباتی به دامین منتقل شد.
        """
        order = self.order_domain.get_order_by_id(order_id)
        item = self.order_domain.add_item_to_order(order, item_data)
        logger.info(f"Item added to Order {order_id}")
        return item

    # ========== REMOVE ITEM ========== #
    def remove_item_from_order(self, order_id: int, item_id: int):
        """
        حذف آیتم و محاسبه مجدد قیمت.
        """
        order = self.order_domain.get_order_by_id(order_id)
        item = get_object_or_404(OrderItem, pk=item_id, order=order)
        
        item.delete()

        self.order_domain.recalculate_order_totals(order)
        logger.info(f"Item {item_id} removed from Order {order_id}")

    def delete_order(self, order_id: int):
        """ حذف کل سفارش """
        logger.warning(f"Deleting Order {order_id}")
        Order.objects.filter(pk=order_id).delete()

    # ===== آپلود فایل سفارش (Async) ===== #
    def upload_order_file_async(self, order_item_id: int, file_obj):
        logger.info(f"START: Async Upload for OrderItem {order_item_id}")
        
        if not os.path.exists(self.temp_storage.location):
            os.makedirs(self.temp_storage.location)
            
        ext = os.path.splitext(file_obj.name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        saved_path = self.temp_storage.save(unique_name, file_obj)
        temp_path = self.temp_storage.path(saved_path)
        original_name = file_obj.name

        try:
            if upload_order_item_file_task:
                upload_order_item_file_task.delay(
                    order_item_id=order_item_id,
                    temp_file_path=temp_path,
                    original_filename=original_name
                )
                return {"status": "processing", "detail": "File upload queued"}
            else:
                logger.warning("Task missing. Switching to SYNC.")
                raise OperationalError("Task missing")

        except (OperationalError, Exception) as e:
            logger.warning(f"ASYNC FAILED: {str(e)}. Fallback to SYNC.")
            
            try:
                order_item = OrderItem.objects.get(id=order_item_id)
                
                existing_uploads = OrderItemFile.objects.filter(
                    order_item=order_item
                )
                for upload in existing_uploads:
                    if upload.file:
                        upload.file.delete(save=False)
                    upload.delete()
                
                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = OrderItemFile.objects.create(
                        order_item=order_item,
                        file=django_file
                    )
                
                os.remove(temp_path)
                return {"status": "completed", "id": instance.id}
                
            except Exception as sync_error:
                logger.critical(f"SYNC FAILED: {str(sync_error)}", exc_info=True)
                if os.path.exists(temp_path): os.remove(temp_path)
                raise sync_error

    # ===== Bulk Operations ===== #
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی سفارشات با فراخوانی سرویس دامنه.
        """
        logger.warning(f"Bulk delete requested for {len(order_ids)} orders.")
        return self.order_domain.bulk_delete_orders(order_ids)
