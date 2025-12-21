from typing import List, Optional
from ..models import Address, City, Province

# ========== ADDRESS SERVICE ========== #
class AddressService:
    """
    سرویس مدیریت آدرس‌های کاربر (جایگزین منطق نوشتاری ریپازیتوری)
    """

    # ==== ایجاد آدرس جدید ===== #
    def create_address(self, user_id: int, data: dict) -> Address:
        """
        اضافه کردن آدرس برای کاربر
        """
        return Address.objects.create(user_id=user_id, **data)

    # ===== ویرایش آدرس ===== #
    def update_address(self, user_id: int, address_id: int, data: dict) -> Optional[Address]:
        """
        ویرایش آدرس پس از پیدا کردن آن
        """
        address = Address.objects.get_address_by_id(user_id, address_id)
        
        if not address:
            return None

        for field, value in data.items():
            setattr(address, field, value)
        
        address.save()
        return address

    # ===== حذف آدرس ===== #
    def delete_address(self, user_id: int, address_id: int) -> bool:
        address = Address.objects.get_address_by_id(user_id, address_id)
        if address:
            address.delete()
            return True
        return False


class GeoService:
    """
    سرویس مدیریت استان و شهر (برای عملیات ادمین/سیستمی)
    """
    
    # ===== Province Operations ===== #
    def create_province(self, data: dict) -> Province:
        return Province.objects.create(**data)

    def update_province(self, province: Province, data: dict) -> Province:
        for field, value in data.items():
            setattr(province, field, value)
        province.save()
        return province

    def bulk_delete_provinces(self, ids: List[int]) -> int:
        """ حذف گروهی استان‌ها """
        return Province.objects.filter(id__in=ids).delete()[0]

    # ===== City Operations ===== #
    def create_city(self, data: dict) -> City:
        return City.objects.create(**data)

    def update_city(self, city: City, data: dict) -> City:
        for field, value in data.items():
            setattr(city, field, value)
        city.save()
        return city

    def bulk_delete_cities(self, ids: List[int]) -> int:
        return City.objects.filter(id__in=ids).delete()[0]
