from celery import current_app
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import ContactUs, PromotionalModal, SliderIndex, SiteMedia
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
        return PromotionalModal.objects.get_active_modal()

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
    def create_slider(self, data: dict) -> SliderIndex:
        """
        ایجاد اسلایدر جدید. فایل تصویر داخل خود data وجود دارد.
        """
        return SliderIndex.objects.create_slider(data)

    @transaction.atomic
    def update_slider(self, instance_or_pk, data: dict) -> SliderIndex:
        """
        ویرایش اسلایدر با مدیریت جایگزینی تصویر.
        برای جلوگیری از کوئری مجدد، می‌تواند خود آبجکت را به جای pk دریافت کند.
        """
        slider = instance_or_pk if isinstance(instance_or_pk, SliderIndex) else self.get_detail(instance_or_pk)

        new_image = data.get('image')

        # ===== حذف تصویر قبلی از حافظه در صورت ارسال تصویر جدید ===== #
        if new_image and slider.image:
            slider.image.delete(save=False)

        for key, value in data.items():
            setattr(slider, key, value)
            
        slider.save()
        return slider

    def delete_slider(self, instance_or_pk):
        """
        حذف اسلایدر و فایل متصل به آن
        """
        slider = instance_or_pk if isinstance(instance_or_pk, SliderIndex) else self.get_detail(instance_or_pk)
        
        if slider.image:
            slider.image.delete(save=False)
            
        slider.delete()

# ========== SITE MEDIA SERVICE ========== #
class SiteMediaService:
    """سرویس مدیریت رسانه‌های سایت"""

    def get_all(self):
        return SiteMedia.objects.get_all_media()

    def get_detail(self, pk: int) -> SiteMedia:
        media = SiteMedia.objects.get_by_id(pk)
        if not media:
            raise ValidationError("رسانه مورد نظر یافت نشد.")
        return media

    def get_active_for_display(self) -> SiteMedia:
        """متدی که ویوی پابلیک برای گرفتن عکس فعال صدا می‌زند"""
        return SiteMedia.objects.get_active_media()

    @transaction.atomic
    def create_media(self, data: dict) -> SiteMedia:
        if data.get('is_active') is True:
            SiteMedia.objects.deactivate_all()
    @transaction.atomic
    def update_media(self, instance_or_pk, data: dict) -> SiteMedia:
        media = instance_or_pk if isinstance(instance_or_pk, SiteMedia) else self.get_detail(instance_or_pk)

        if data.get('is_active') is True:
            SiteMedia.objects.exclude(pk=media.pk).deactivate_all()

        new_file = data.get('file')
        if new_file and media.file:
            media.file.delete(save=False)

        for key, value in data.items():
            setattr(media, key, value)
            
        media.save()
        return media

    def delete_media(self, instance_or_pk):
        media = instance_or_pk if isinstance(instance_or_pk, SiteMedia) else self.get_detail(instance_or_pk)
        if media.file:
            media.file.delete(save=False)
        media.delete()
