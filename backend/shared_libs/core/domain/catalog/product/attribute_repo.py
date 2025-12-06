from typing import Optional, Dict, Any
from django.db.models import QuerySet

from core.models import Size, Material
from core.models import Quantity, FileUploadSpec
from core.utils.base_repository import BaseRepository

# ===== Size Repository ===== #
class SizeRepository(BaseRepository[Size]):
    """
    ریپازیتوری مدیریت سایزها.
    """
    def __init__(self):
        super().__init__(Size)

    def get_all_sizes(self) -> QuerySet[Size]:
        return self.model.objects.all().order_by('name')

    def get_by_name(self, name: str) -> Optional[Size]:
        return self.model.objects.filter(name=name).first()

    def create_size(self, data: Dict[str, Any]) -> Size:
        return self.model.objects.create(**data)

# ===== Material Repository ===== #
class MaterialRepository(BaseRepository[Material]):
    """
    ریپازیتوری مدیریت جنس‌ها (متریال).
    """
    def __init__(self):
        super().__init__(Material)

    def get_all_materials(self) -> QuerySet[Material]:
        return self.model.objects.all().order_by('-is_active', 'created_at')

    def get_active_materials(self) -> QuerySet[Material]:
        """ فقط متریال‌های فعال برای نمایش در سایت """
        return self.model.objects.filter(is_active=True)

    def get_by_name(self, name: str) -> Optional[Material]:
        return self.model.objects.filter(name=name).first()

    def create_material(self, data: Dict[str, Any]) -> Material:
        return self.model.objects.create(**data)
    


# ===== Quantity Repository ===== #
class QuantityRepository(BaseRepository[Quantity]):
    """
    ریپازیتوری مدیریت مقادیر تیراژ.
    """
    def __init__(self):
        super().__init__(Quantity)

    def get_all_quantities(self) -> QuerySet[Quantity]:
        return self.model.objects.all().order_by('value')

    def get_by_value(self, value: int) -> Optional[Quantity]:
        return self.model.objects.filter(value=value).first()
    
    def create_quantity(self, data: Dict[str, Any]) -> Quantity:
        return self.model.objects.create(**data)

# ===== File Upload Spec Repository ===== #
class FileUploadSpecRepository(BaseRepository[FileUploadSpec]):
    """
    ریپازیتوری مدیریت انواع فایل‌های طراحی (مثل طرح رو، خط برش و...).
    """
    def __init__(self):
        super().__init__(FileUploadSpec)

    def get_all_specs(self) -> QuerySet[FileUploadSpec]:
        return self.model.objects.all().order_by('name')

    def get_by_name(self, name: str) -> Optional[FileUploadSpec]:
        return self.model.objects.filter(name=name).first()
    
    def create_spec(self, data: Dict[str, Any]) -> FileUploadSpec:
        return self.model.objects.create(**data)
