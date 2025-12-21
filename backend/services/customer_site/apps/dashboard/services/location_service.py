from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from core.models import City, Province
from core.domain.identity.address import ProvinceRepository, CityRepository

class LocationDashboardService:
    """
    سرویس مدیریت مناطق جغرافیایی (استان و شهر) برای پنل ادمین.
    """
    def __init__(self):
        self.province_repo = ProvinceRepository()
        self.city_repo = CityRepository()

    # ==========================
    # ===== Province Logic =====
    # ==========================
    def get_all_provinces(self):
        return self.province_repo.get_all_ordered()

    def get_province_detail(self, province_id: int) -> Province:
        province = self.province_repo.get_by_id(province_id)
        if not province:
            raise ValidationError("استان مورد نظر یافت نشد.")
        return province

    @transaction.atomic
    def create_province(self, data: Dict[str, Any]) -> Province:
        """ ایجاد استان جدید """
        # اینجا می‌توانید ولیدیشن‌های بیزنس اضافه کنید (مثلاً عدم تکرار نام)
        return self.province_repo.create_province(data)

    @transaction.atomic
    def update_province(self, province_id: int, data: Dict[str, Any]) -> Province:
        """ ویرایش استان """
        province = self.get_province_detail(province_id)
        return self.province_repo.update_province(province, data)

    @transaction.atomic
    def delete_province(self, province_id: int):
        """ حذف تکی استان """
        province = self.get_province_detail(province_id)
        # چک کردن وابستگی‌ها (مثلاً اگر شهر دارد نباید پاک شود یا کسکید می‌شود)
        # فرض بر Cascade در مدل است، اما اگر Restrict باشد باید اینجا هندل شود.
        province.delete()

    @transaction.atomic
    def bulk_delete_provinces(self, ids: List[int]) -> int:
        """ حذف گروهی استان‌ها """
        return self.province_repo.bulk_delete(ids)

    # ======================
    # ===== City Logic =====
    # ======================
    def get_all_cities(self):
        return self.city_repo.get_all_ordered()
    
    def get_cities_by_province(self, province_id: int):
        return self.city_repo.get_by_province(province_id)

    def get_city_detail(self, city_id: int) -> City:
        city = self.city_repo.get_by_id(city_id)
        if not city:
            raise ValidationError("شهر مورد نظر یافت نشد.")
        return city

    @transaction.atomic
    def create_city(self, data: Dict[str, Any]) -> City:
        # چک کردن وجود استان
        if 'province' in data:
            # اگر ID استان ارسال شده باشد، باید مطمئن شویم وجود دارد (معمولا DRF این کار را میکند)
            pass 
        return self.city_repo.create_city(data)

    @transaction.atomic
    def update_city(self, city_id: int, data: Dict[str, Any]) -> City:
        city = self.get_city_detail(city_id)
        return self.city_repo.update_city(city, data)

    @transaction.atomic
    def delete_city(self, city_id: int):
        city = self.get_city_detail(city_id)
        city.delete()

    @transaction.atomic
    def bulk_delete_cities(self, ids: List[int]) -> int:
        return self.city_repo.bulk_delete(ids)
