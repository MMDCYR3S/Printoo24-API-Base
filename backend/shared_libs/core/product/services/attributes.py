from typing import Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import Size, Quantity

# ========== SIZE SERVICE ========== #
class SizeService:
    """
    سرویس مدیریت منطق سایزها (Size Domain Logic)
    """

    def get_all(self):
        return Size.objects.get_all_sizes()

    def get_by_id(self, size_id: int) -> Size:
        size = Size.objects.get_by_id(size_id)
        if not size:
            raise ValidationError(_("سایز مورد نظر یافت نشد."))
        return size

    @transaction.atomic
    def create_size(self, user, data: Dict[str, Any]) -> Size:
        """
        ایجاد سایز جدید با بررسی قوانین دامین.
        """
        # ===== بررسی تکراری نبودن نام ===== #
        if Size.objects.get_by_name(data['name']):
            raise ValidationError(_("سایزی با این نام قبلاً ثبت شده است."))

        # ===== بررسی مقادیر معتبر ===== #
        if data.get('width', 0) <= 0 or data.get('height', 0) <= 0:
            raise ValidationError(_("طول و عرض باید بزرگتر از صفر باشند."))

        return Size.objects.create_size({**data, 'user': user})

    @transaction.atomic
    def update_size(self, size_id: int, data: Dict[str, Any]) -> Size:
        size = self.get_by_id(size_id)

        # ===== بررسی تکراری نبودن نام ===== #
        if 'name' in data and data['name'] != size.name:
            if Size.objects.get_by_name(data['name']):
                raise ValidationError(_("سایزی با این نام قبلاً ثبت شده است."))

        # جایگزین: self.repo.update(size, data)
        for key, value in data.items():
            setattr(size, key, value)
        size.save()
        
        return size

    def delete_size(self, size_id: int):
        size = self.get_by_id(size_id)
        try:
            size.delete()
        except Exception:
            raise ValidationError(_("امکان حذف این سایز وجود ندارد زیرا در محصولاتی استفاده شده است."))


# ========== QUANTITY SERVICE ========== #
class QuantityService:
    """
    سرویس مدیریت منطق تیراژها (Quantity Domain Logic)
    """

    def get_all(self):
        return Quantity.objects.get_all_quantities()

    def get_by_id(self, pk: int) -> Quantity:
        instance = Quantity.objects.get_by_id(pk)
        if not instance:
            raise ValidationError(_("تیراژ مورد نظر یافت نشد."))
        return instance
    
    def update_quantity(self, pk: int, data: Dict[str, Any]) -> Quantity:
        """
        آپدیت تیراژ
        """
        instance = self.get_by_id(pk)
        # چک اضافی که در کد اصلی هم بود: if instance is None raise... (هرچند get_by_id بالا هندل میکند)
        
        if data["value"] != instance.value:
            existing_quantity = Quantity.objects.get_by_value(data["value"])
            if existing_quantity:
                raise ValidationError(_("این مقدار تیراژ قبلاً ثبت شده است."))
        
        # جایگزین: self.repo.update
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        
        return instance

    @transaction.atomic
    def create_quantity(self, user, value: int) -> Quantity:
        """
        ایجاد تیراژ جدید.
        """
        if value <= 0:
            raise ValidationError(_("مقدار تیراژ باید بزرگتر از صفر باشد."))

        if Quantity.objects.get_by_value(value):
            raise ValidationError(_("این مقدار تیراژ قبلاً ثبت شده است."))

        data = {'user': user, 'value': value}
        return Quantity.objects.create_quantity(data)

    @transaction.atomic
    def delete_quantity(self, pk: int):
        instance = self.get_by_id(pk)
        try:
            instance.delete()
        except Exception:
            raise ValidationError(_("امکان حذف این تیراژ وجود ندارد (در محصولات استفاده شده است)."))
