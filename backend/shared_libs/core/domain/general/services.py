from celery import current_app

from django.db import transaction
from django.core.exceptions import ValidationError

from .repositories import ContactUsRepository, ModalRepository
from core.models import PromotionalModal, ContactUs

# ===== Content Domain Service ===== #
class ContentService:
    """
    سرویسی که هم مودال و هم تماس با ما را مدیریت می‌کند.
    (چون لاجیک‌ها سبک هستند، در یک کلاس تجمیع کردیم تا از تعدد فایل جلوگیری کنیم)
    """
    def __init__(self):
        self.contact_repo = ContactUsRepository()
        self.modal_repo = ModalRepository()

    def reply_to_user_message(self, message_id: int, reply_text: str):
        """
        1. پیام را پیدا می‌کند.
        2. وضعیت را به خوانده شده تغییر می‌دهد.
        3. تسک ارسال ایمیل را در صف سلری می‌گذارد.
        """
        # ===== پیام را پیدا می‌کند. ===== 
        message = self.contact_repo.get_by_id(message_id)
        if not message:
            raise ValidationError("پیام مورد نظر یافت نشد.")
            
        if not message.email:
             raise ValidationError("کاربر ایمیل ندارد، امکان ارسال پاسخ نیست.")

        message.is_read = True
        message.save()

        # --- بخش فراخوانی تسک (Decoupled) ---
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

    # ===== بخش تماس با ما ===== #
    def submit_contact_form(self, data: dict) -> ContactUs:
        """
        ثبت پیام تماس با ما.
        تحلیل‌گر: اینجا جای خوبی برای اضافه کردن تسک ارسال ایمیل به ادمین است.
        """
        # ===== اعتبارسنجی‌های خاص اگر لازم باشد اینجا قرار می‌گیرد ===== #
        return self.contact_repo.create_message(data)

    # ===== بخش مودال ===== #
    def get_active_modal_for_display(self) -> dict:
        """
        متدی که فرانت‌اند صدا می‌زند تا ببیند چه چیزی نمایش دهد.
        """
        modal = self.modal_repo.get_active_modal()
        if not modal:
            return None
        
        # ===== تبدیل به دیکشنری ساده برای مصرف راحت‌تر (اختیاری) ===== #
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
        اگر در داده‌ها is_active=True باشد، بقیه را غیرفعال می‌کند.
        """
        is_active = data.get('is_active', False)
        
        if is_active:
            self.modal_repo.deactivate_all()
            
        modal = self.modal_repo.create_modal(data)
        return modal

    @transaction.atomic
    def update_modal(self, modal_id: int, data: dict) -> PromotionalModal:
        """
        ویرایش مودال. مدیریت همزمانی فعال بودن.
        """
        modal = self.modal_repo.get_by_id(modal_id)
        if not modal:
            raise ValidationError("مودال یافت نشد.")

        # ===== اگر قرار است فعال شود، بقیه باید غیرفعال شوند ===== #
        if data.get('is_active') is True:
            self.modal_repo.deactivate_all()

        for field, value in data.items():
            setattr(modal, field, value)
        
        modal.save()
        return modal

    @transaction.atomic
    def toggle_modal_status(self, modal_id: int) -> PromotionalModal:
        """
        تغییر وضعیت سریع (Active/Inactive).
        """
        modal = self.modal_repo.get_by_id(modal_id)
        if not modal:
            raise ValidationError("مودال یافت نشد.")

        if not modal.is_active:
            self.modal_repo.deactivate_all()
            modal.is_active = True
        else:
            modal.is_active = False
            
        modal.save()
        return modal