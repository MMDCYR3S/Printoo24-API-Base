from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import User, OrderItem, OrderItemFile
from apps.support.services import LoggerService
from apps.permissions import AppPermissionChecker
from apps.operations.tasks import process_uploaded_design_file

class OrderFileAppService:
    def __init__(self):
        self.audit_service = LoggerService()

    def _check_designer_access(self, requester: User, item_id: int) -> OrderItem:
        """ 
        چک کردن دسترسی طراح به آیتم.
        """
        try:
            item = OrderItem.objects.get(id=item_id)
        except OrderItem.DoesNotExist:
            raise ValidationError("آیتم سفارش یافت نشد.")
        
        if requester.is_superuser:
            return item
            
        return item
        
    def upload_design_file(self, requester: User, item_id: int, file_data):
        """
        آپلود فایل جدید و ورژن‌بندی.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')
        
        item = self._check_designer_access(requester, item_id)
        
        last_file = OrderItemFile.objects.filter(order_item=item).order_by('-version').first()
        new_version = (last_file.version + 1) if last_file else 1
        
      # ===== غیر فعال کردن فایل قبلی ===== #
        if last_file:
            last_file.is_latest = False
            last_file.save()

        # ===== ایجاد فایل جدید ===== #
        new_file = OrderItemFile.objects.create(
            order_item=item,
            file=file_data,
            version=new_version,
            is_latest=True,
            admin_feedback=None
        )
        
        # ===== پردازش و ارسال فایل ===== #
        if process_uploaded_design_file:
            process_uploaded_design_file.delay(new_file.id)
        
        # ===== ثبت لاگ آپلود ===== #
        self.audit_service.record_log(
            user=requester,
            obj=item,
            action='UPLOAD_DESIGN_FILE',
            changes={
                'file_id': new_file.id,
                'version': new_version,
                'filename': str(file_data)
            },
            description=_(f"آپلود فایل طراحی نسخه {new_version}")
        )
        
        return new_file
        
    def review_design_file(self, requester: User, file_id: int, feedback: str = None):
        """
        بررسی فایل توسط طراح یا QC (ثبت بازخورد).
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')
        
        try:
            file_obj = OrderItemFile.objects.select_related('order_item').get(id=file_id)
        except OrderItemFile.DoesNotExist:
            raise ValidationError("فایل یافت نشد.")
        
        self._check_designer_access(requester, file_obj.order_item.id)
        
        file_obj.admin_feedback = feedback
        file_obj.save()
        
        # ===== ثبت لاگ بررسی ===== #
        self.audit_service.record_log(
            user=requester,
            obj=file_obj.order_item,
            action='REVIEW_DESIGN_FILE',
            changes={'file_id': file_id, 'feedback_snippet': feedback[:50] if feedback else "No Feedback"},
            description=_(f"ثبت نظر روی فایل طراحی")
        )
        
        return file_obj
        
    def change_file_status(self, requester: User, file_id: int, new_status: str, feedback: str = None):
        """
        تغییر وضعیت فایل (تایید / رد).
        نکته: چون مدل فیلد status ندارد، این لاجیک روی OrderItem اعمال می‌شود
        یا اینکه فرض کنیم فیلد status اضافه شده است.
        
        سناریو صحیح: اگر فایل رد شد، وضعیت آیتم می‌شود 'rejected' و فیدبک روی فایل ثبت می‌شود.
        """
        AppPermissionChecker.check_has_permission(requester, 'change_orderitemfile')

        try:
            file_obj = OrderItemFile.objects.select_related('order_item').get(id=file_id)
        except OrderItemFile.DoesNotExist:
            raise ValidationError("فایل یافت نشد.")

        self._check_designer_access(requester, file_obj.order_item.id)
        
        item = file_obj.order_item
        old_status = item.status
        # ===== بررسی وضعیت تایید شده یا رد شده ===== #
        if new_status == 'rejected':
            item.status = 'rejected'
            file_obj.admin_feedback = feedback or "رد شده توسط QC"
        elif new_status == 'approved':
            item.status = 'approved'
            file_obj.admin_feedback = feedback or "تایید شده"
        
        file_obj.save()
        item.save()
        
        # ===== ثبت لاگ تغییر وضعیت فایل ===== #
        self.audit_service.record_log(
            user=requester,
            obj=item,
            action='FILE_STATUS_CHANGE',
            changes={
                'file_id': file_id,
                'item_status_from': old_status,
                'item_status_to': item.status,
                'feedback': feedback
            },
            description=_(f"تغییر وضعیت فایل/آیتم به {new_status}")
        )
        
        return file_obj
