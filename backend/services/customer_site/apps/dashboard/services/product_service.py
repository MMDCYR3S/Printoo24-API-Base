import os
import logging
import uuid
from typing import Dict, Any, List
from kombu.exceptions import OperationalError
from django.db import transaction
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.db.models import Prefetch

# فرض بر این است که متدهای مربوط به EAV را در Domain Service نوشته‌اید
from core.product.services import ProductService, ProductMediaService
from core.models import Product, ProductImage

try:
    from apps.dashboard.tasks import upload_product_image_task, upload_attachment_library_task
except ImportError:
    upload_product_image_task = None
    upload_attachment_library_task = None

logger = logging.getLogger('dashboard.services.product_dashboard')

class ProductDashboardService:
    """
    سرویس اپلیکیشن داشبورد با معماری جدید فیلدساز و فرمول‌ساز
    """
    def __init__(self):
        self._domain_service = ProductService()
        self.media_service = ProductMediaService()
        self.temp_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_uploads'))

    # ===== CREATE & UPDATE CORE PRODUCT ===== #
    @transaction.atomic
    def create_product_core(self, user, data: Dict[str, Any]):
        """ ساخت اطلاعات پایه و شناسنامه‌ای محصول """
        return self._domain_service.create_product_shell(user, data)

    @transaction.atomic
    def update_product_core(self, product_id: int, user, data: Dict[str, Any]):
        """ ویرایش اطلاعات پایه محصول """
        self._domain_service.update_product_shell(product_id, data)
        return self._domain_service.get_product_detail_by_id(product_id)

    # ===== SYNC FIELDS (FORM BUILDER) ===== #
    @transaction.atomic
    def sync_product_fields(self, product_id: int, fields_data: List[Dict]):
        """
        دریافت تمام فیلدها، گزینه‌ها و شروط از فرانت‌اند و همگام‌سازی کامل با دیتابیس
        (این متد باید در Domain Service شما پیاده‌سازی شده باشد تا دیتای قبلی را پاک یا آپدیت کند)
        """
        # فرض بر این است که متد sync_fields در دامنه، لاجیک ساخت/ویرایش مدل‌های ProductField را هندل می‌کند
        return self._domain_service.sync_fields(product_id, fields_data)

    # ===== SYNC FORMULAS (FORMULA BUILDER) ===== #
    @transaction.atomic
    def sync_product_formulas(self, product_id: int, formulas_data: List[Dict]):
        """
        دریافت و همگام‌سازی فرمول‌های قیمت‌گذاری
        """
        return self._domain_service.sync_formulas(product_id, formulas_data)

    # ===== FETCH METHODS ===== #
    def get_all_products(self):
        return self._domain_service.get_all_products()

    def get_product_detail(self, product_id):
        return self._domain_service.get_product_detail_by_id(product_id) 

    # ===== BULK & DELETE ===== #
    def delete_product(self, product_id: int):
        self._domain_service.delete_product(product_id)

    def bulk_update_product_status(self, product_ids: List[int], is_active: bool) -> int:
        return self._domain_service.bulk_update_status(product_ids, is_active)

    def bulk_delete_products(self, product_ids: List[int]) -> Dict[str, int]:
        return self._domain_service.bulk_delete_products(product_ids)

    # ===== UPLOAD MEDIA (مبقی ماندن کدهای رسانه بدون تغییر) ===== #
    def _save_temp_file(self, file_obj) -> str:
        if not os.path.exists(self.temp_storage.location):
            os.makedirs(self.temp_storage.location)
        ext = os.path.splitext(file_obj.name)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        saved_path = self.temp_storage.save(unique_name, file_obj)
        return self.temp_storage.path(saved_path)

    # ===== آپلود تصویر (با Fallback) ===== #
    def upload_product_image_async(self, product_id, user, file_obj, order=0):
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
                original_filename=original_name,
                order=order
            )
            return {"status": "processing", "detail": "Image upload queued"}

        except (OperationalError, Exception) as e:
            logger.error(f"Celery connection failed: {str(e)}. Switching to Sync mode.")

            # ===== FALLBACK: اجرای همگام (Sync) ===== #
            try:
                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = self.media_service.upload_product_image(product_id, user, django_file, order=order)
                
                # ===== حذف فایل موقت ===== #
                os.remove(temp_path)
                return {"status": "completed", "id": instance.id}
            except Exception as sync_error:
                logger.error(f"Sync upload also failed: {str(sync_error)}")
                raise sync_error

    # ===== UPLOAD ATTACHMENTS ===== #
    def upload_attachment_library_async(self, user, file_obj, product_id: int, name: str = None):
        """
        آپلود فایل در کتابخانه با مکانیزم Async + Sync Fallback.
        """
        # ===== ذخیره فایل به صورت موقت ===== #
        temp_path = self._save_temp_file(file_obj)
        original_name = file_obj.name
        #‌ ===== تلاش برای آپلود از طریق Celery ===== #
        try:
            logger.info(f"Attempting async attachment upload: {name}")
            upload_attachment_library_task.delay(
                user_id=user.id,
                product_id=product_id,
                temp_file_path=temp_path,
                original_filename=original_name,
                name_in_library=name
            )
            return {"status": "processing", "detail": "Attachment upload queued"}

        except (OperationalError, Exception) as e:
            logger.error(f"Celery failed for attachment: {str(e)}. Switching to Sync mode.")
            
            # ===== تلاش برای باز کردن فایل و ارسال مستقیم ===== #
            try:
                with open(temp_path, 'rb') as f:
                    django_file = File(f, name=original_name)
                    instance = self.media_service.upload_attachment_to_library(user, django_file, product_id, name)
                
                os.remove(temp_path)
                return {"status": "completed", "id": instance.id}
            except Exception as sync_error:
                logger.error(f"Sync attachment upload failed: {str(sync_error)}")
                raise sync_error

    # ===== GET ALL PRODUCTS ===== #
    def get_all_products(self):
        """ دریافت لیست کامل محصولات (فرمت درختی) """
        return self._domain_service.get_all_products()

    # ===== GET PRODUCT DETAIL ===== #
    def get_product_detail(self, product_id):
        """ دریافت جزئیات کامل محصول (فرمت درختی) """
        return self._domain_service.get_product_detail_by_id(product_id) 

    # ===== DELETE PRODUCT ===== #
    def delete_product(self, product_id: int):
        self._domain_service.delete_product(product_id)
    
    # ===== DELETE IMAGE ===== #
    def delete_product_image_from_app(self, product_id: int, image_id: int):
        """
        واسط حذف تصویر محصول از طریق لایه اپلیکیشن
        """
        # در صورت نیاز به بررسی سطوح دسترسی بیزینسی خاص، اینجا پیاده‌سازی می‌شود
        return self.media_service.delete_product_image(product_id=product_id, image_id=image_id)

    # ===== DELTE ATTACHMENT ===== #
    def delete_product_attachment_from_app(self, product_id: int, attachment_id: int):
        """
        واسط حذف فایل پیوست محصول از طریق لایه اپلیکیشن
        """
        return self.media_service.delete_product_attachment(product_id=product_id, attachment_id=attachment_id)

    # ========== BULK ACTIONS ========== #
    def bulk_update_product_status(self, product_ids: List[int], is_active: bool) -> int:
        """
        تغییر وضعیت فعال/غیرفعال برای لیستی از محصولات.
        """
        return self._domain_service.bulk_update_status(product_ids, is_active)

    def bulk_delete_products(self, product_ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی محصولات.
        خروجی: تعداد حذف شده‌های واقعی و تعداد غیرفعال شده‌ها (Soft Delete).
        """
        return self._domain_service.bulk_delete_products(product_ids)

    def get_minimal_active_products(self):
        """
        دریافت ۴ فیلد اصلی + اولین عکس برای محصولات فعال
        """
        return Product.objects.filter(is_active=True).only(
            'id', 'name', 'slug', 'code'
        ).prefetch_related(
            Prefetch(
                'product_image', 
                queryset=ProductImage.objects.order_by('order'),
                to_attr='prefetched_images'
            )
        ).order_by('-id')
