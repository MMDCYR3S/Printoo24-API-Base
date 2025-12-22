from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import City, Province
from core.users.services import GeoService

class LocationDashboardService:
    """
    سرویس مدیریت مناطق جغرافیایی (استان و شهر) برای پنل ادمین.
    """
    def __init__(self):
        self.geo_service = GeoService()

    # ==========================
    # ===== Province Logic =====
    # ==========================
    def get_all_provinces(self):
        return self.geo_service.get_all_provinces()

    def get_province_detail(self, province_id: int) -> Province:
        # اصلاح شد: get_by_id -> get_province_by_id
        province = self.geo_service.get_province_by_id(province_id)
        if not province:
            raise ValidationError("استان مورد نظر یافت نشد.")
        return province

    @transaction.atomic
    def create_province(self, data: Dict[str, Any]) -> Province:
        return self.geo_service.create_province(data)

    @transaction.atomic
    def update_province(self, province_id: int, data: Dict[str, Any]) -> Province:
        province = self.get_province_detail(province_id)
        return self.geo_service.update_province(province, data)

    @transaction.atomic
    def delete_province(self, province_id: int):
        province = self.get_province_detail(province_id)
        province.delete()

    @transaction.atomic
    def bulk_delete_provinces(self, ids: List[int]) -> int:
        # اصلاح شد: bulk_delete -> bulk_delete_provinces
        return self.geo_service.bulk_delete_provinces(ids)

    # ======================
    # ===== City Logic =====
    # ======================
    def get_all_cities(self):
        # اصلاح شد: متد صریح
        return self.geo_service.get_all_cities()
    
    def get_cities_by_province(self, province_id: int):
        # اصلاح شد: get_by_province -> get_cities_by_province
        return self.geo_service.get_cities_by_province(province_id)

    def get_city_detail(self, city_id: int) -> City:
        # اصلاح شد: get_by_id -> get_city_by_id
        city = self.geo_service.get_city_by_id(city_id)
        if not city:
            raise ValidationError("شهر مورد نظر یافت نشد.")
        return city

    @transaction.atomic
    def create_city(self, data: Dict[str, Any]) -> City:
        if 'province' in data:
            pass 
        return self.geo_service.create_city(data)

    @transaction.atomic
    def update_city(self, city_id: int, data: Dict[str, Any]) -> City:
        city = self.get_city_detail(city_id)
        return self.geo_service.update_city(city, data)

    @transaction.atomic
    def delete_city(self, city_id: int):
        city = self.get_city_detail(city_id)
        city.delete()

    @transaction.atomic
    def bulk_delete_cities(self, ids: List[int]) -> int:
        # اصلاح شد: bulk_delete -> bulk_delete_cities
        return self.geo_service.bulk_delete_cities(ids)
