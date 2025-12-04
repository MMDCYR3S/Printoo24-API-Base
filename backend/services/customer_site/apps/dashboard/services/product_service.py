import os
import logging
import uuid
from typing import Dict, Any, List
from kombu.exceptions import OperationalError

from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files import File

# ===== سرویس های دامنه ===== #
from core.domain.product import ProductDomainService, ProductMediaDomainService

try:
    from apps.dashboard.tasks import upload_product_image_task, upload_attachment_library_task
except ImportError:
    # ====
    upload_product_image_task = None
    upload_attachment_library_task = None

logger = logging.getLogger('dashboard.services.product_dashboard')

class ProductDashboardService:
    """
    سرویس اپلیکیشن (Application Service) مخصوص داشبورد.
    """
    def __init__(self):
        self._domain_service = ProductDomainService()
        self.media_service = ProductMediaDomainService()
        self.temp_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_uploads'))
    # ===== ایجاد اطلاعات اولیه ===== #
    @transaction.atomic
    def create_full_product_core(self, user, data: Dict[str, Any]):
        """
        ایجاد محصول + کانفیگ قیمت + متریال + تیراژ + فایل‌های مورد نیاز
        همه در یک تراکنش واحد.
        """
        # ===== تفکیک داده ها ===== #
        shell_data = data.get('shell')
        pricing_data = data.get('pricing_config', {})
        material_ids = data.get('material_ids', [])
        default_material_id = data.get('default_material_id')
        quantity_ids = data.get('quantity_ids', [])
        file_requirements = data.get('file_requirements', [])
        
        # ===== ایجاد محصول ===== #
        product = self._domain_service.create_product_shell(user, shell_data)
        
        # ===== ایجاد کانفیگ قیمت ===== #
        if pricing_data:
            self._domain_service.update_pricing_config(product.id, pricing_data)
            
        # ===== هماهنگی بین وابستگی ها ===== #
        self._domain_service.sync_materials(product.id, user, material_ids, default_material_id)
        self._domain_service.sync_quantities(product.id, user, quantity_ids)
        self._domain_service.sync_file_requirements(product.id, file_requirements)

        return product
    
    # ===== ویرایش اطلاعات اولیه ===== #
    @transaction.atomic
    def update_full_product_core(self, product_id: int, data: Dict[str, Any]):
        """ ویرایش تجمیعی اطلاعات پایه """
        shell_data = data.get('shell')
        
        # ===== ویرایش اطلاعات پایه ===== #
        if shell_data:
            self._domain_service.update_product_shell(product_id, shell_data)
            
        # ===== بروزرسانی سایر بخش ها در صورت وجود ===== #
        if 'pricing_config' in data:
            self._domain_service.update_pricing_config(product_id, data['pricing_config'])
        
        if 'material_ids' in data:
            self._domain_service.sync_materials(product_id, data['material_ids'])
        
        if 'file_requirements' in data:
            self._domain_service.sync_file_requirements(product_id, data['file_requirements'])
            
        if 'quantity_ids' in data:
            self._domain_service.sync_quantities(product_id, data['quantity_ids'])
            
        if 'default_material_id' in data:
            self._domain_service.sync_materials(product_id, data['default_material_id'])
    
        return self._domain_service.get_product_detail_by_slug(product_id)
    
    # ===== ویرایش آپشن ها ===== #
    @transaction.atomic
    def bulk_sync_options(self, product_id: int, options_data: List[Dict]):
        """
        دریافت لیستی از آپشن‌ها و اعمال آنها روی محصول.
        """
        results = []
        for opt_data in options_data:
            try:
                self._domain_service.attach_option_with_config(product_id, opt_data)
                results.append({'option_id': opt_data['option_id'], 'status': 'synced'})
            except Exception as e:
                raise e
        return results
    
    # ===== تصاویر و فایل های پیوست ===== #
    @transaction.atomic
    def sync_media_assets(self, product_id: int, user, data: Dict[str, Any]):
        """
        مدیریت لینک پیوست‌ها و ترتیب تصاویر.
        """
        attachment_ids = data.get('attachment_ids_to_link', [])
        attachment_ids_to_unlink = data.get('attachment_ids_to_unlink', [])
        image_orders = data.get('image_orders', [])

        # ===== لینک فایل‌ها ===== #
        for att_id in attachment_ids:
            try:
                self.media_service.attach_file_to_product(product_id, att_id, user)
            except ValidationError:
                continue

        # ===== حذف فایل‌ها ===== #
        for att_id in attachment_ids_to_unlink:
            self.media_service.detach_file_from_product(product_id, att_id)

        # ===== ترتیب تصاویر ===== #
        if image_orders:
            self.media_service.reorder_images(product_id, image_orders)

    # ===== متد کمکی ذخیره موقت ===== #
    def _save_temp_file(self, file_obj) -> str:
        """ ذخیره فایل در مسیر موقت و بازگرداندن آدرس کامل آن """
        if not os.path.exists(self.temp_storage.location):
            os.makedirs(self.temp_storage.location)
            
        ext = os.path.splitext(file_obj.name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        saved_path = self.temp_storage.save(unique_name, file_obj)
        return self.temp_storage.path(saved_path)

    # ===== آپلود تصویر (با Fallback) ===== #
    def upload_product_image_async(self, product_id, user, file_obj):
        """
        آپلود تصویر محصول با مکانیزم Async + Sync Fallback.
        """
        temp_path = self._save_temp_file(file_obj)
        original_name = file_obj.name

        try:
            logger.info(f"Attempting async upload for product {product_id}")
            # ===== اجرای همگام (Async) ===== #
            upload_product_image_task.delay(
                product_id=product_id,
                user_id=user.id,
                temp_file_path=temp_path,
                original_filename=original_name
            )
            return {"status": "processing", "detail": "Image upload queued"}

        except (OperationalError, Exception) as e:
            logger.error(f"Celery connection failed: {str(e)}. Switching to Sync mode.")
            
            # === FALLBACK: اجرای همگام (Sync) === #
            try:
                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = self.media_service.upload_product_image(product_id, user, django_file)
                
                # ===== حذف فایل موقت ===== #
                os.remove(temp_path)
                return {"status": "completed", "id": instance.id}
            except Exception as sync_error:
                logger.error(f"Sync upload also failed: {str(sync_error)}")
                raise sync_error

    # ===== آپلود پیوست (با Fallback) ===== #
    def upload_attachment_library_async(self, user, file_obj, name):
        """
        آپلود فایل در کتابخانه با مکانیزم Async + Sync Fallback.
        """
        temp_path = self._save_temp_file(file_obj)
        original_name = file_obj.name

        try:
            logger.info(f"Attempting async attachment upload: {name}")
            upload_attachment_library_task.delay(
                user_id=user.id,
                temp_file_path=temp_path,
                original_filename=original_name,
                name_in_library=name
            )
            return {"status": "processing", "detail": "Attachment upload queued"}

        except (OperationalError, Exception) as e:
            logger.error(f"Celery failed for attachment: {str(e)}. Switching to Sync mode.")
            
            # === FALLBACK === #
            try:
                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = self.media_service.upload_attachment_to_library(user, django_file, name)
                
                os.remove(temp_path)
                return {"status": "completed", "id": instance.id}
            except Exception as sync_error:
                logger.error(f"Sync attachment upload failed: {str(sync_error)}")
                raise sync_error
