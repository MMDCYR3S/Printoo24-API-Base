from typing import Dict, Any, List, Optional
from django.db.models import QuerySet
from core.models import Option, OptionValue
from ...utils.base_repository import BaseRepository

# ===== Option Repository ===== #
class OptionRepository(BaseRepository[Option]):
    def __init__(self):
        super().__init__(Option)

    def get_all_with_values(self) -> QuerySet[Option]:
        """
        دریافت تمام ویژگی‌ها همراه با مقادیرشان (برای جلوگیری از N+1).
        """
        return self.model.objects.prefetch_related('global_values').all().order_by('-created_at')

    def get_by_name(self, name: str) -> Optional[Option]:
        return self.model.objects.filter(name=name).first()

    def create_option(self, data: Dict[str, Any]) -> Option:
        return self.model.objects.create(**data)


# ===== Option Value Repository ===== #
class OptionValueRepository(BaseRepository[OptionValue]):
    def __init__(self):
        super().__init__(OptionValue)

    def create_value(self, option: Option, data: Dict[str, Any]) -> OptionValue:
        return self.model.objects.create(option=option, **data)

    def bulk_create_values(self, values: List[OptionValue]):
        self.model.objects.bulk_create(values)

    def delete_by_option(self, option: Option):
        """حذف تمام مقادیر یک ویژگی"""
        self.model.objects.filter(option=option).delete()