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
    Order, OrderItem,
    Product, Address,
    OrderItemFile, User,
    OrderStatus, OrderStateLog
)
from core.order.services import OrderService

try:
    from apps.dashboard.tasks import upload_order_item_file_task
except ImportError:
    upload_order_item_file_task = None

logger = logging.getLogger('dashboard.services.order_dashboard')

# ========== ORDER DASHBOARD SERVICE ========== #
class OrderDashboardService:
    def __init__(self):
        self.order_domain = OrderService()
        self.temp_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_order_uploads'))

    # ===== GET ORDERS LIST ===== #
    def get_orders_list(self):
        """
        لیست تمام سفارشات با جزئیات لازم برای جدول داشبورد.
        ادمین همه نوع سفارشات را می‌بیند.
        """
        return Order.objects.select_related('user__customer_profile', 'current_status')\
            .prefetch_related('order_item_order')\
            .order_by('-created_at')

    # ===== GET ALL ORDERS ===== #
    def get_all_orders_queryset(self):
        """
        لیست تمام سفارشات با جزئیات لازم برای جدول داشبورد.
        ادمین همه نوع سفارشات را می‌بیند.
        """
        return Order.objects.select_related('user__customer_profile', 'current_status')\
            .prefetch_related('order_item_order')\
            .order_by('-created_at')

    # ===== GET ORDER DETAIL ===== #
    def get_order_detail(self, order_id: int):
        """
        دریافت جزئیات کامل سفارش (با فایل‌ها و آیتم‌ها).
        """
        return self.order_domain.get_order_by_id(order_id)

    # ===== CREATE ORDER ===== #
    def create_admin_order(self,
                           user_id: int,
                           items_data: List[Dict],
                           address_id: int = None,
                           total_price_override: float = None,
                           full_address: str = None,
                           recipient_name: str = None,
                           recipient_phone: str = None,
                           company_name: str = None):
        """
        فراخوانی سرویس دامین برای ایجاد سفارش.
        اگر user_id نال باشد، سفارش به عنوان مهمان ثبت می‌شود.
        """
        logger.info(f"Dashboard: Creating order for User {user_id}")

        # ===== مدیریت اطلاعات اختیاری کاربر ===== #
        final_recipient_name = recipient_name
        final_recipient_phone = recipient_phone
        final_full_address = full_address

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if not final_recipient_name:
                    try:
                        final_recipient_name = user.customer_profile.fullname() or user.phone_number
                    except Exception:
                        final_recipient_name = user.phone_number
                if not final_recipient_phone:
                    final_recipient_phone = getattr(user, 'phone_number', None)
            except User.DoesNotExist:
                raise ValidationError(f"کاربری با شناسه {user_id} یافت نشد.")

        # ===== اگر آدرس ارجاع داده شد ===== #
        if address_id and not final_full_address:
            try:
                address_obj = Address.objects.get(id=address_id)
                final_full_address = f"{address_obj.province.name} - {address_obj.city.name} - {address_obj.address}"
            except Address.DoesNotExist:
                raise ValidationError(f"آدرسی با شناسه {address_id} یافت نشد.")

        return self.order_domain.create_order_direct(
            user_id=user_id,
            address_id=address_id,
            recipient_name=final_recipient_name,
            recipient_phone=final_recipient_phone,
            company_name=company_name,
            full_address=final_full_address,
            items_data=items_data,
            total_price_override=total_price_override,
            type="1"
        )

    # ===== UPDATE ORDER ===== #
    @transaction.atomic
    def update_order_details(self, order_id: int, data: Dict):
        """
        ویرایش اطلاعات کلی سفارش (آدرس، نوع، قیمت کل دستی).
        """
        logger.info(f"Updating Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)

        if 'address_id' in data:
            address = get_object_or_404(Address, pk=data['address_id'])
            if order.user_id and address.user_id != order.user_id:
                raise ValidationError("این آدرس متعلق به کاربر سفارش‌دهنده نیست.")
            order.address = address

        if 'type' in data:
            order.type = data['type']

        if 'total_price' in data:
            order.total_price = Decimal(str(data['total_price']))

        order.save()
        logger.info(f"Order {order_id} updated successfully")
        return order

    # ===== ADD ITEM TO ORDER ===== #
    @transaction.atomic
    def add_item_to_order(self, order_id: int, item_data: Dict):
        """افزودن آیتم جدید به سفارش موجود"""
        logger.info(f"Adding item to Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)

        try:
            product_slug = item_data.get('product_slug')
            selections = item_data.get('selections', {})

            # ===== دریافت نام و توضیحات ===== #
            item_name = item_data.get('name') or selections.get('name')
            item_description = item_data.get('description') or selections.get('description')
            quantity = int(selections.get('quantity', 1))

            product = None
            if product_slug:
                product = get_object_or_404(Product, slug=product_slug)
                if not item_name:
                    item_name = product.name

            if not item_name:
                raise ValidationError("برای آیتم‌های بدون محصول، وارد کردن `name` الزامی است.")

            # ===== محاسبه قیمت ===== #
            if 'item_price' in item_data and item_data['item_price'] is not None:
                line_total = Decimal(str(item_data['item_price']))
            elif 'price' in item_data and item_data['price'] is not None:
                line_total = Decimal(str(item_data['price']))
            elif product:
                line_total = product.price * quantity
            else:
                raise ValidationError(f"برای آیتم '{item_name}' قیمت مشخص نشده است.")

            # ===== ساختار JSON متناسب با فیلد items مدل ===== #
            safe_selections = {k: v for k, v in selections.items()
                               if k not in ('quantity', 'name', 'description', 'item_price')}
            specs_json = safe_selections

            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=line_total,
                items=specs_json,
                name=item_name,
                description=item_description
            )

            # ===== بروزرسانی قیمت کل سفارش ===== #
            order.total_price = Decimal(str(order.total_price)) + line_total
            order.save(update_fields=['total_price', 'updated_at'])

            logger.info(f"Item {item.id} added to Order {order.id}. New Total: {order.total_price}")
            return item

        except (ValidationError, Exception) as e:
            logger.error(f"Failed to add item to order {order_id}: {str(e)}", exc_info=True)
            raise

    # ===== REMOVE ITEM ===== #
    def remove_item_from_order(self, order_id: int, item_id: int):
        """حذف آیتم از سفارش و کسر قیمت"""
        logger.info(f"Removing Item {item_id} from Order {order_id}")
        order = get_object_or_404(Order, pk=order_id)
        item = get_object_or_404(OrderItem, pk=item_id, order=order)

        price_deduct = item.price
        item.delete()

        order.total_price = max(Decimal('0'), Decimal(str(order.total_price)) - Decimal(str(price_deduct)))
        order.save(update_fields=['total_price', 'updated_at'])
        logger.info(f"Item removed. New Total: {order.total_price}")

    # ===== DELETE ORDER ===== #
    def delete_order(self, order_id: int):
        """حذف کل سفارش"""
        logger.warning(f"Deleting Order {order_id}")
        Order.objects.filter(pk=order_id).delete()

    # ===== UPLOAD FILE (ASYNC) ===== #
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

                existing_uploads = OrderItemFile.objects.filter(order_item=order_item)
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
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise sync_error

    # ===== GET ALL STATUSES ===== #
    def get_all_order_statuses(self):
        """
        دریافت لیست وضعیت‌ها مرتب شده بر اساس sort_order
        """
        return OrderStatus.objects.all().order_by('sort_order')

    # ===== CHANGE STATUS ===== #
    @transaction.atomic
    def change_order_status(self, order_id: int, status_code: str, actor, description: str = None):
        """
        تغییر وضعیت سفارش بر اساس کد سیستمی.
        تاریخچه تغییر در OrderStateLog ثبت می‌شود.
        """
        logger.info(f"Changing status for Order {order_id} to {status_code}")

        order = get_object_or_404(Order, pk=order_id)

        try:
            new_status = OrderStatus.objects.get(internal_code=status_code)
        except OrderStatus.DoesNotExist:
            raise ValidationError(f"وضعیت با کد '{status_code}' یافت نشد.")

        previous_status = order.current_status
        order.current_status = new_status
        order.save(update_fields=['current_status', 'updated_at'])

        # ===== ثبت تاریخچه تغییر وضعیت ===== #
        OrderStateLog.objects.create(
            order=order,
            from_status=previous_status,
            to_status=new_status,
            actor=actor,
            description=description or ""
        )

        logger.info(f"Order {order.id} status changed: {previous_status} -> {new_status}")
        return order

    # ===== BULK DELETE ===== #
    def bulk_delete_orders(self, order_ids: List[int]) -> Dict:
        """
        حذف گروهی سفارشات با فراخوانی سرویس دامنه.
        """
        logger.warning(f"Bulk delete requested for {len(order_ids)} orders.")
        return self.order_domain.bulk_delete_orders(order_ids)
