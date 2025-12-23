from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import Option, OptionValue

# ========== OPTION SERVICE ========== #
class OptionService:
    """
    سرویس دامنه مدیریت ویژگی‌ها (Options)
    """

    def get_all(self):
        return Option.objects.get_all_with_values()

    def get_by_id(self, pk: int) -> Option:
        instance = Option.objects.get_by_id(pk)
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
        if Option.objects.get_by_name(option_data['name']):
            raise ValidationError(_("ویژگی با این نام سیستمی قبلاً ثبت شده است."))

        # ===== ایجاد ویژگی ===== #
        # (guide_text و guide_type و input_type خودکار توسط **option_data ذخیره می‌شوند)
        option = Option.objects.create(**option_data)

        # ===== ایجاد مقدار ها ===== #
        if values_data:
            values_to_create = []
            seen_values = set()
            
            for val_data in values_data:
                if val_data['value'] in seen_values:
                    continue
                seen_values.add(val_data['value'])
                
                # [FIXED] اضافه شدن فیلدهای guide
                values_to_create.append(OptionValue(
                    option=option,
                    label=val_data.get('label'),
                    value=val_data['value'],
                    guide_text=val_data.get('guide_text', ''),
                    guide_type=val_data.get('guide_type', 'info')
                ))
            
            if values_to_create:
                OptionValue.objects.bulk_create(values_to_create)

        return option

    @transaction.atomic
    def update_full_option(self, pk: int, option_data: Dict[str, Any], values_data: List[Dict[str, Any]] = None) -> Option:
        """
        آپدیت ویژگی والد و همگام‌سازی مقادیر فرزند.
        """
        instance = self.get_by_id(pk)
        
        if 'name' in option_data and option_data['name'] != instance.name:
            if Option.objects.get_by_name(option_data['name']):
                raise ValidationError(_("این نام سیستمی تکراری است."))
        
        for key, value in option_data.items():
            setattr(instance, key, value)
        instance.save()

        if values_data is not None:
            self._sync_option_values(instance, values_data)

        return self.get_by_id(pk)
    
    def _sync_option_values(self, option: Option, values_data: List[Dict]):
        """
        منطق Smart Sync:
        - اگر ID داشت و معتبر بود -> آپدیت
        - اگر ID نداشت -> ایجاد
        - (اختیاری) اگر در لیست نبود -> حذف (در اینجا حذف نمی‌کنیم تا دیتا نپرد، مگر اینکه بخواهید)
        """
        existing_values = {v.id: v for v in option.global_values.all()}
        vals_to_create = []
        vals_to_update = []

        incoming_ids = set()

        for val_data in values_data:
            val_id = val_data.get('id')
            
            # ===== آپدیت رکورد موجود ===== #
            if val_id and val_id in existing_values:
                obj = existing_values[val_id]
                # آپدیت فیلدها
                obj.label = val_data.get('label', obj.label)
                obj.value = val_data.get('value', obj.value)
                obj.guide_text = val_data.get('guide_text', obj.guide_text)
                obj.guide_type = val_data.get('guide_type', obj.guide_type)
                vals_to_update.append(obj)
                incoming_ids.add(val_id)
            
            # ===== ایجاد رکورد جدید ===== #
            elif not val_id:
                vals_to_create.append(OptionValue(
                    option=option,
                    label=val_data.get('label'),
                    value=val_data.get('value'),
                    guide_text=val_data.get('guide_text', ''),
                    guide_type=val_data.get('guide_type', 'info')
                ))

        # ===== اعمال تغییرات در دیتابیس ===== #
        if vals_to_create:
            OptionValue.objects.bulk_create(vals_to_create)
        
        if vals_to_update:
            OptionValue.objects.bulk_update(
                vals_to_update, 
                ['label', 'value', 'guide_text', 'guide_type']
            )

        # OptionValue.objects.filter(option=option).exclude(id__in=incoming_ids).delete()
    
    @transaction.atomic
    def add_value_to_option(self, option_id: int, data: Dict[str, Any]) -> OptionValue:
        """
        افزودن یک مقدار جدید به ویژگی موجود.
        """
        option = self.get_by_id(option_id)
        if option.global_values.filter(value=data['value']).exists():
             raise ValidationError(_("این مقدار قبلاً برای این ویژگی تعریف شده است."))

        return OptionValue.objects.create(option=option, **data)

    def delete_option(self, pk: int):
        instance = self.get_by_id(pk)
        try:
            instance.delete()
        except Exception:
             raise ValidationError(_("امکان حذف این ویژگی وجود ندارد (در محصولات استفاده شده است)."))
