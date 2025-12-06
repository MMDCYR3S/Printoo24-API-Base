from typing import Optional
from django.db.models import QuerySet

from core.models import ContactUs, PromotionalModal, SliderIndex
from core.utils import BaseRepository

# ===== Contact Us Repository ===== #
class ContactUsRepository(BaseRepository[ContactUs]):
    
    def __init__(self):
        super().__init__(ContactUs)
    
    """
    ریپازیتوری ساده برای مدیریت تماس با ما.
    """
    def create_message(self, data: dict) -> ContactUs:
        return ContactUs.objects.create(**data)

    def get_unread_messages(self) -> QuerySet[ContactUs]:
        return ContactUs.objects.filter(is_read=False)


# ===== Promotional Modal Repository ===== #
class ModalRepository(BaseRepository[PromotionalModal]):
    
    def __init__(self):
        super().__init__(PromotionalModal)
    
    """
    ریپازیتوری برای دسترسی به داده‌های مودال.
    """
    def get_active_modal(self) -> Optional[PromotionalModal]:
        """
        دریافت مودال فعال (باید فقط یکی باشد).
        """
        return PromotionalModal.objects.filter(is_active=True).first()

    def get_all_modals(self) -> QuerySet[PromotionalModal]:
        return PromotionalModal.objects.all().order_by('-created_at')
    
    def get_by_id(self, modal_id: int) -> Optional[PromotionalModal]:
        try:
            return PromotionalModal.objects.get(id=modal_id)
        except PromotionalModal.DoesNotExist:
            return None
            
    def create_modal(self, data: dict) -> PromotionalModal:
        return PromotionalModal.objects.create(**data)
        
    def delete_modal(self, instance: PromotionalModal):
        instance.delete()

    def deactivate_all(self):
        """
        غیرفعال کردن تمام مودال‌ها (برای استفاده در سرویس).
        """
        PromotionalModal.objects.update(is_active=False)

# ===== Slider Repository ===== #
class SliderRepository(BaseRepository[SliderIndex]):
    """
    ریپازیتوری مدیریت اسلایدرهای صفحه اصلی.
    """
    def __init__(self):
        super().__init__(SliderIndex)

    def get_all_sliders(self) -> QuerySet[SliderIndex]:
        """
        دریافت تمام اسلایدرها به ترتیب جدیدترین.
        """
        return self.model.objects.all().order_by('-created_at')
