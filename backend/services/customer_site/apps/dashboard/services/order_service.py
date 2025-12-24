import os
import logging
import uuid
import time
from typing import Dict, List
from decimal import Decimal
from kombu.exceptions import OperationalError

from django.db import transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.exceptions import ValidationError

from core.models import (
    User,Order, OrderItem, OrderStatus,
    Product, Address,
    OrderItemFile, ProductOptionValue,
    ProductSize, ProductOptionValue
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
    def create_admin_order(self, user_id: int, address_id: int, items_data: List[Dict], total_price_override: float = None):
        """
        فراخوانی سرویس دامین برای ایجاد سفارش.
        """
        logger.info(f"Dashboard: Creating order for User {user_id}")
        return self.order_domain.create_order_direct(
            user_id=user_id,
            address_id=address_id,
            items_data=items_data,
            total_price_override=total_price_override
        )

    # ===== ویرایش سفارش (Update) ===== #
    @transaction.atomic
    def update_order_details(self, order_id: int, data: Dict):
        """
        ویرایش اطلاعات کلی سفارش (آدرس، نوع، قیمت کل دستی).
        """
        logger.info(f"Updating Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)
        # ===== ویرایش آدرس ===== #
        if 'address_id' in data:
            address = get_object_or_404(Address, pk=data['address_id'])
            if address.user_id != order.user_id:
                raise ValidationError("این آدرس متعلق به کاربر سفارش‌دهنده نیست.")
            order.address = address
        # ===== ویرایش نوع ===== #
        if 'type' in data:
            order.type = data['type']
        # ===== ویرایش قیمت کل ===== #
        if 'total_price' in data:
            order.total_price = Decimal(str(data['total_price']))
            
        order.save()
        logger.info(f"Order {order_id} updated successfully")
        return order

    # ===== مدیریت آیتم‌های سفارش (Add/Remove Item) ===== #
    
    @transaction.atomic
    def add_item_to_order(self, order_id: int, item_data: Dict):
        """ افزودن آیتم جدید به سفارش موجود """
        logger.info(f"Adding item to Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)
        
        try:
            product_slug = item_data.get('product_slug')
            selections = item_data.get('selections', item_data)
            product = get_object_or_404(Product, slug=product_slug)
            quantity = selections.get('quantity', 1)
            
            # قیمت دستی آیتم یا پیش‌فرض
            if 'item_price' in item_data and item_data['item_price'] is not None:
                line_total = Decimal(str(item_data['item_price']))
            else:
                line_total = product.price * quantity # ساده

            specs_json = {
                'size_id': selections.get('size_id'),
                'custom_width': selections.get('custom_width'),
                'custom_height': selections.get('custom_height'),
                'option_value_ids': selections.get('option_value_ids'),
                'has_design': selections.get('has_design', True)
            }

            # ایجاد آیتم
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=line_total,
                items=specs_json
            )
            
            # آپدیت قیمت کل سفارش (جمع زدن با قیمت قبلی)
            order.total_price += line_total
            order.save()
            
            logger.info(f"Item {item.id} added to Order {order.id}. New Total: {order.total_price}")
            return item
            
        except Exception as e:
            logger.error(f"Failed to add item to order {order_id}: {str(e)}", exc_info=True)
            raise e

    def remove_item_from_order(self, order_id: int, item_id: int):
        """ حذف آیتم از سفارش و کسر قیمت """
        logger.info(f"Removing Item {item_id} from Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)
        item = get_object_or_404(OrderItem, pk=item_id, order=order)
        
        price_deduct = item.price
        item.delete()
        # ===== کسر قیمت ===== #
        order.total_price -= price_deduct
        if order.total_price < 0: order.total_price = 0
        
        order.save()
        logger.info(f"Item removed. New Total: {order.total_price}")

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
