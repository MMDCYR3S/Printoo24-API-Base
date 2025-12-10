from django.core.files.base import ContentFile
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.domain.commerce.order import (
    OrderItemRepository, OrderItemFileRepository,
    OrderStatusFlowDomainService
)
from core.models import User, OrderItemFile, Order, OrderItem
from apps.permissions import AppPermissionChecker
from apps.operations.tasks import process_uploaded_design_file

class OrderFileAppService:
    def __init__(self):
        self.item_repo = OrderItemRepository()
        self.file_repo = OrderItemFileRepository()
        self.status_flow_service = OrderStatusFlowDomainService()

    def _check_designer_access(self, requester: User, item_id: int):
        """
        چک می‌کند که آیا این کاربر اجازه دستکاری این آیتم خاص را دارد؟
        """
        # ===== دریافت آیتم ===== #
        item = self.item_repo.get_by_id(item_id)
        if not item:
            raise ValidationError("آیتم سفارش یافت نشد.")
        
        # ===== چک کردن اجازه دسترسی ===== #
        if requester.is_superuser:
            return item
        
        # ===== چک کردن نقش کاربر ===== #
        user_role = requester.user_role.first()
        if not user_role:
            raise PermissionDenied("شما نقشی ندارید.")
        
        if item.assigned_to_id != requester.id:
            raise PermissionDenied("این آیتم به شما اختصاص داده نشده است. ابتدا آن را بردارید.")

        return item
    
    def upload_design_file(self, requester: User, item_id: int, file_data, requirement_id: int):
        """
        آپلود فایل جدید (ورژن جدید) برای یک آیتم.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')
        
        item = self._check_designer_access(requester, item_id)
        
        requirement = item.product.file_upload_requirements.filter(id=requirement_id).first()
        if not requirement:
            raise ValidationError("این نوع فایل برای این محصول تعریف نشده است.")
        
        last_file = item.files.filter(requirement_id=requirement_id).order_by('-version').first()
        new_version = (last_file.version + 1) if last_file else 1

        # ===== غیر فعال کردن فایل قبلی ===== #
        if last_file:
            last_file.is_latest = False
            last_file.save()

        # ===== ایجاد فایل جدید ===== #
        new_file = self.file_repo.create({
            "order_item": item,
            "requirement": requirement,
            "file": file_data,
            "version": new_version,
            "is_latest": True,
            "status": "uploading",
        })
        
        process_uploaded_design_file.delay(new_file.id)
        
        return new_file
        
    def change_file_status(self, requester: User, file_id: int, new_status: str, feedback: str = None):
        """
        تغییر وضعیت فایل (تایید / رد / نیازمند اصلاح)
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')

        # ===== دریافت فایل ===== #
        file_obj = self.file_repo.get_by_id(file_id)
        if not file_obj:
            raise ValidationError("فایل یافت نشد.")

        # ===== چک کردن اجازه دسترسی ===== #
        self._check_designer_access(requester, file_obj.order_item.id)

        # ===== چک کردن وضعیت ===== #
        if new_status not in dict(OrderItemFile.STATUS_CHOICES):
            raise ValidationError("وضعیت نامعتبر است.")

        file_obj.status = new_status
        if feedback:
            file_obj.admin_feedback = feedback
        
        file_obj.save()
        return file_obj
        
    def change_file_status(self, requester: User, file_id: int, new_status: str, feedback: str = None):
        """
        تغییر وضعیت یک فایل (تایید / رد) و سپس چک کردن وضعیت کلی سفارش.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')
        
        file_obj = self.file_repo.get_by_id(file_id)
        if not file_obj:
            raise ValidationError("فایل یافت نشد.")
        
        self._check_designer_access(requester, file_obj.order_item.id)
        
        if new_status not in dict(OrderItemFile.STATUS_CHOICES):
            raise ValidationError("وضعیت نامعتبر است.")
        
        file_obj.status = new_status
        if feedback:
            file_obj.admin_feedback = feedback
            
        file_obj.save()
        
        return file_obj
        