from typing import List, Optional
from django.db import transaction
from django.db.models import QuerySet
from core.utils import BaseRepository
from core.models import Address, City, Province

class AddressRepository(BaseRepository[Address]):
    def __init__(self):
        super().__init__(Address)

    # ===== دریافت آدرس‌های کاربر ===== #
    def get_user_addresses(self, user_id: int):
        """دریافت تمام آدرس‌های کاربر (پیش‌فرض اول نمایش داده شود)"""
        return self.model.objects.filter(user_id=user_id).select_related('province', 'city').order_by('-created_at')

    # ===== دریافت یک آدرس ===== #
    def get_address_by_id(self, user_id: int, address_id: int):
        """دریافت یک آدرس خاص با چک کردن مالکیت کاربر"""
        return self.model.objects.filter(user_id=user_id, id=address_id).first()

    # ==== ایجاد آدرس جدید ===== #
    def create_address(self, user_id: int, data: dict) -> Address:
        """
        اضافه کردن آدرس برای کاربر
        """
        return self.model.objects.create(user_id=user_id, **data)

    # ===== ویرایش آدرس ===== #
    def update_address(self, user_id: int, address_id: int, data: dict) -> Address:
        """
        ویرایش آدرس پس از پیدا کردن آن
        """
        address = self.get_address_by_id(user_id, address_id)
        if not address:
            return None

        for field, value in data.items():
            setattr(address, field, value)
        
        address.save()
        return address

    # ===== حذف آدرس ===== #
    def delete_address(self, user_id: int, address_id: int):
        address = self.get_address_by_id(user_id, address_id)
        if address:
            address.delete()
            return True
        return False

# ===== Province Repository ===== #
class ProvinceRepository(BaseRepository[Province]):
    def __init__(self):
        super().__init__(Province)

    def get_all_ordered(self) -> QuerySet[Province]:
        """ دریافت لیست همه استان‌ها مرتب شده """
        return self.model.objects.all().order_by('name')

    def get_by_id(self, province_id: int) -> Optional[Province]:
        return self.model.objects.filter(id=province_id).first()

    def create_province(self, data: dict) -> Province:
        return self.model.objects.create(**data)

    def update_province(self, province: Province, data: dict) -> Province:
        for field, value in data.items():
            setattr(province, field, value)
        province.save()
        return province

    def bulk_delete(self, ids: List[int]) -> int:
        """ حذف گروهی """
        return self.model.objects.filter(id__in=ids).delete()[0]


# ===== City Repository ===== #
class CityRepository(BaseRepository[City]):
    def __init__(self):
        super().__init__(City)

    def get_all_ordered(self) -> QuerySet[City]:
        return self.model.objects.select_related('province').order_by('province__name', 'name')
    
    def get_by_province(self, province_id: int) -> QuerySet[City]:
        """ دریافت شهرهای یک استان خاص """
        return self.model.objects.filter(province_id=province_id).order_by('name')

    def get_by_id(self, city_id: int) -> Optional[City]:
        return self.model.objects.filter(id=city_id).first()

    def create_city(self, data: dict) -> City:
        return self.model.objects.create(**data)

    def update_city(self, city: City, data: dict) -> City:
        for field, value in data.items():
            setattr(city, field, value)
        city.save()
        return city

    def bulk_delete(self, ids: List[int]) -> int:
        return self.model.objects.filter(id__in=ids).delete()[0]
