from typing import List
from django.db import models
from .base import BaseQuerySet


# ========== ADDRESS QUERYSETS ========== #
class AddressQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به آدرس"""
    
    def get_user_addresses(self, user_id: int):
        """دریافت تمام آدرس‌های کاربر (پیش‌فرض اول نمایش داده شود)"""
        return self.filter(user_id=user_id).select_related('province', 'city').order_by('-created_at')

    def get_address_by_id(self, user_id: int, address_id: int):
        """دریافت یک آدرس خاص با چک کردن مالکیت کاربر"""
        return self.filter(user_id=user_id, id=address_id).first()

# ========== ADDRESS MANAGERS ========== #
class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

    def get_user_addresses(self, user_id: int):
        return self.get_queryset().get_user_addresses(user_id)

    def get_address_by_id(self, user_id: int, address_id: int):
        return self.get_queryset().get_address_by_id(user_id, address_id)


# ========== PROVINCE QUERYSETS ========== #
class ProvinceQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به استان"""
    
    def get_all_ordered(self):
        """ دریافت لیست همه استان‌ها مرتب شده """
        return self.order_by('name')

# ========== PROVINCE MANAGERS ========== #
class ProvinceManager(models.Manager):
    def get_queryset(self):
        return ProvinceQuerySet(self.model, using=self._db)

    def get_all_ordered(self):
        return self.get_queryset().get_all_ordered()
    
    def get_by_id(self, province_id: int):
        return self.get_queryset().get_by_id(province_id)


# ========== CITY QUERYSETS ========== #
class CityQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به شهر"""
    
    def get_all_ordered(self):
        return self.select_related('province').order_by('province__name', 'name')
    
    def get_by_province(self, province_id: int):
        """ دریافت شهرهای یک استان خاص """
        return self.filter(province_id=province_id).order_by('name')

# ========== CITY MANAGERS ========== #
class CityManager(models.Manager):
    def get_queryset(self):
        return CityQuerySet(self.model, using=self._db)

    def get_all_ordered(self):
        return self.get_queryset().get_all_ordered()

    def get_by_province(self, province_id: int):
        return self.get_queryset().get_by_province(province_id)

    def get_by_id(self, city_id: int):
        return self.get_queryset().get_by_id(city_id)
