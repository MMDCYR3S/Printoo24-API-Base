from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import SliderIndex

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
            raise ValidationError("اسلایدر مورد نظر یافت نشد.")
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
