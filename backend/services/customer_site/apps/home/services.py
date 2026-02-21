from celery import current_app
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import ContactUs, PromotionalModal, SliderIndex
from core.infrastructure.messages import msg_provider

# ========== CONTACT SERVICE ========== #
class ContactService:
    """
    سرویس مدیریت پیام‌های تماس با ما.
    """

    def submit_contact_form(self, data: dict) -> ContactUs:
        """
        ثبت پیام تماس با ما.
        """
        return ContactUs.objects.create_message(data)

    def reply_to_user_message(self, message_id: int, reply_text: str, admin_user=None):
        """
        پاسخ به پیام کاربر و ارسال ایمیل.
        """
        message = ContactUs.objects.get_by_id(message_id)
            
        if not message:
            raise ValidationError(msg_provider.get("home.E5001"))
        
        # ===== جلوگیری از پاسخ مجدد ===== #
        if message.admin_reply:
            raise ValidationError(msg_provider.get("home.E5002"))

        if not message.email:
             raise ValidationError(msg_provider.get("home.E5003"))

        # ===== ذخیره پاسخ و تغییر وضعیت ===== #
        message.is_read = True
        message.admin_reply = reply_text
        message.replied_at = timezone.now()
        if admin_user:
            message.replied_by = admin_user
            
        message.save()

        # ===== ارسال تسک ایمیل ===== #
        current_app.send_task(
            'send_contact_us_reply',
            kwargs={
                'user_email': message.email,
                'user_name': message.full_name,
                'reply_message': reply_text,
                'original_subject': message.subject
            }
        )

        return message

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
            raise ValidationError(msg_provider.get("home.E5004"))

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
            raise ValidationError(msg_provider.get("home.E5004"))

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

# ========== SLIDER SERVICE ========== #
class SliderService:
    """
    سرویس مدیریت اسلایدرها.
    """

    def get_all(self):
        return SliderIndex.objects.get_all_sliders()

    def get_detail(self, pk: int) -> SliderIndex:
        slider = SliderIndex.objects.get_by_id(pk)
        if not slider:
            raise ValidationError(msg_provider.get("home.E5005"))
        return slider

    @transaction.atomic
    def create_slider(self, data: dict, file_obj=None) -> SliderIndex:
        """
        ایجاد اسلایدر جدید.
        """
        if file_obj:
            data['image'] = file_obj
            
        return SliderIndex.objects.create_slider(data)

    @transaction.atomic
    def update_slider(self, pk: int, data: dict, file_obj=None) -> SliderIndex:
        """
        ویرایش اسلایدر با مدیریت جایگزینی تصویر.
        """
        slider = self.get_detail(pk)

        if file_obj:
            # ===== حذف تصویر قبلی از حافظه ===== #
            if slider.image:
                slider.image.delete(save=False)
            
            data['image'] = file_obj

        # آپدیت دستی
        for key, value in data.items():
            setattr(slider, key, value)
        slider.save()
        
        return slider

    def delete_slider(self, pk: int):
        slider = self.get_detail(pk)
        if slider.image:
            slider.image.delete(save=False)
            
        slider.delete()

