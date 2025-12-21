from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import Size, Quantity, User
from .repositories import (
    SizeRepository,
    QuantityRepository
)

# ===== Size Domain Service ===== #
class SizeDomainService:
    def __init__(self):
        self.repo = SizeRepository()

    def get_all(self):
        return self.repo.get_all_sizes()

    def get_by_id(self, size_id: int) -> Size:
        size = self.repo.get_by_id(size_id)
        if not size:
            raise ValidationError(_("سایز مورد نظر یافت نشد."))
        return size

    @transaction.atomic
    def create_size(self, user: User, data: Dict[str, Any]) -> Size:
        """
        ایجاد سایز جدید با بررسی قوانین دامین.
        """
        # ===== بررسی تکراری نبودن نام ===== #
        if self.repo.get_by_name(data['name']):
            raise ValidationError(_("سایزی با این نام قبلاً ثبت شده است."))

        # ===== بررسی مقادیر معتبر ===== #
        if data.get('width', 0) <= 0 or data.get('height', 0) <= 0:
            raise ValidationError(_("طول و عرض باید بزرگتر از صفر باشند."))

        # ===== راه حل صحیح: ادغام دیکشنری‌ها ===== #
        size_data = data.copy()
        size_data['user'] = user

        return self.repo.create_size(size_data)

    @transaction.atomic
    def update_size(self, size_id: int, data: Dict[str, Any]) -> Size:
        size = self.get_by_id(size_id)

        # ===== بررسی تکراری نبودن نام ===== #
        if 'name' in data and data['name'] != size.name:
            if self.repo.get_by_name(data['name']):
                raise ValidationError(_("سایزی با این نام قبلاً ثبت شده است."))

        return self.repo.update(size, data)

    def delete_size(self, size_id: int):
        size = self.repo.get_by_id(size_id)
        try:
            size.delete()
        except Exception as e:
            raise ValidationError(_("امکان حذف این سایز وجود ندارد زیرا در محصولاتی استفاده شده است."))

# ===== Quantity Domain Service ===== #
class QuantityDomainService:
    def __init__(self):
        self.repo = QuantityRepository()

    def get_all(self):
        return self.repo.get_all_quantities()

    def get_by_id(self, pk: int) -> Quantity:
        instance = self.repo.get_by_id(pk)
        if not instance:
            raise ValidationError(_("تیراژ مورد نظر یافت نشد."))
        return 
    
    def update_quantity(self, pk: int, data: Dict[str, Any]) -> Quantity:
        """
        آپدیت تیراژ
        """
        instance = self.repo.get_by_id(pk)
        if instance is None:
            raise ValidationError(_("تیراژ مورد نظر با شناسه وارد شده یافت نشد."))
        if data["value"] != instance.value:
            existing_quantity = self.repo.get_by_value(data["value"])
            if existing_quantity:
                raise ValidationError(_("این مقدار تیراژ قبلاً ثبت شده است."))
        return self.repo.update(instance, data)

    @transaction.atomic
    def create_quantity(self, user: User, value: int) -> Quantity:
        """
        ایجاد تیراژ جدید.
        """
        if value <= 0:
            raise ValidationError(_("مقدار تیراژ باید بزرگتر از صفر باشد."))

        if self.repo.get_by_value(value):
            raise ValidationError(_("این مقدار تیراژ قبلاً ثبت شده است."))

        data = {'user': user, 'value': value}
        return self.repo.create_quantity(data)

    @transaction.atomic
    def delete_quantity(self, pk: int):
        instance = self.repo.get_by_id(pk)
        try:
            instance.delete()
        except Exception:
            raise ValidationError(_("امکان حذف این تیراژ وجود ندارد (در محصولات استفاده شده است)."))
