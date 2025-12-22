from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PromotionalModal

# ===========  MODAL SERVICE ========== #
class ModalService:
    """
    سرویس مدیریت مودال‌های تبلیغاتی.
    """

    def get_active_modal_for_display(self) -> dict:
        """
        متدی که فرانت‌اند صدا می‌زند تا ببیند چه چیزی نمایش دهد.
        """
        modal = PromotionalModal.objects.get_active_modal()
        if not modal:
            return None
        
        return {
            "title": modal.title,
            "description": modal.description,
            "image": modal.image_url,
            "cta_text": modal.cta_text,
            "cta_url": modal.cta_url
        }

    @transaction.atomic
    def create_modal(self, data: dict) -> PromotionalModal:
        """
        ایجاد مودال جدید.
        """
        is_active = data.get('is_active', False)
        
        if is_active:
            PromotionalModal.objects.deactivate_all()
            
        return PromotionalModal.objects.create_modal(data)

    @transaction.atomic
    def update_modal(self, modal_id: int, data: dict) -> PromotionalModal:
        """
        ویرایش مودال. مدیریت همزمانی فعال بودن.
        """
        modal = PromotionalModal.objects.get_by_id(modal_id)
        if not modal:
            raise ValidationError("مودال یافت نشد.")

        # ===== اگر قرار است فعال شود، بقیه باید غیرفعال شوند ===== #
        if data.get('is_active') is True:
            PromotionalModal.objects.deactivate_all()

        for field, value in data.items():
            setattr(modal, field, value)
        
        modal.save()
        return modal

    @transaction.atomic
    def toggle_modal_status(self, modal_id: int) -> PromotionalModal:
        """
        تغییر وضعیت سریع (Active/Inactive).
        """
        modal = PromotionalModal.objects.get_by_id(modal_id)
        if not modal:
            raise ValidationError("مودال یافت نشد.")

        if not modal.is_active:
            PromotionalModal.objects.deactivate_all()
            modal.is_active = True
        else:
            modal.is_active = False
            
        modal.save()
        return modal
        
    def delete_modal(self, modal_id: int):
        modal = PromotionalModal.objects.get_by_id(modal_id)
        if modal:
            modal.delete()
