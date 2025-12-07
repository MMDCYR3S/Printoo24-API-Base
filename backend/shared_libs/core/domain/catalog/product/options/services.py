from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import Option, OptionValue
from .repositories import OptionRepository, OptionValueRepository

# ===== Option Domain Service ===== #
class OptionDomainService:
    def __init__(self):
        self.option_repo = OptionRepository()
        self.value_repo = OptionValueRepository()

    def get_all(self):
        return self.option_repo.get_all_with_values()

    def get_by_id(self, pk: int) -> Option:
        instance = self.option_repo.get_by_id(pk)
        if not instance:
            raise ValidationError(_("ویژگی مورد نظر یافت نشد."))
        return instance

    # ===== شاهکار: ایجاد اتمیک ویژگی و مقادیر ===== #
    @transaction.atomic
    def create_full_option(self, option_data: Dict[str, Any], values_data: List[Dict[str, Any]]) -> Option:
        """
        ایجاد ویژگی به همراه لیست مقادیر آن در یک تراکنش.
        """
        # ===== بررسی یکتایی نام سیستمی ===== #
        if self.option_repo.get_by_name(option_data['name']):
            raise ValidationError(_("ویژگی با این نام سیستمی قبلاً ثبت شده است."))

        # ===== ایجاد ویژگی ===== #
        option = self.option_repo.create_option(option_data)

        # ===== ایجاد مقدار ها ===== #
        if values_data:
            values_to_create = []
            seen_values = set()
            
            for val_data in values_data:
                if val_data['value'] in seen_values:
                    continue
                seen_values.add(val_data['value'])
                
                values_to_create.append(OptionValue(
                    option=option,
                    label=val_data.get('label'),
                    value=val_data['value']
                ))
            
            if values_to_create:
                self.value_repo.bulk_create_values(values_to_create)

        return option

    @transaction.atomic
    def update_option(self, pk: int, data: Dict[str, Any]) -> Option:
        """
        ویرایش اطلاعات پایه ویژگی (بدون تغییر مقادیر فرزند).
        """
        instance = self.get_by_id(pk)
        
        # ===== بررسی یکتایی نام سیستمی ===== #
        if 'name' in data and data['name'] != instance.name:
            if self.option_repo.get_by_name(data['name']):
                raise ValidationError(_("این نام سیستمی تکراری است."))
                
        return self.option_repo.update(instance, data)

    @transaction.atomic
    def add_value_to_option(self, option_id: int, data: Dict[str, Any]) -> OptionValue:
        """
        افزودن یک مقدار جدید به ویژگی موجود.
        """
        option = self.get_by_id(option_id)
        if option.global_values.filter(value=data['value']).exists():
             raise ValidationError(_("این مقدار قبلاً برای این ویژگی تعریف شده است."))
             
        return self.value_repo.create_value(option, data)

    def delete_option(self, pk: int):
        instance = self.get_by_id(pk)
        try:
            instance.delete()
        except Exception:
             raise ValidationError(_("امکان حذف این ویژگی وجود ندارد (در محصولات استفاده شده است)."))