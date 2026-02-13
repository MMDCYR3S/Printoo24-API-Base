from typing import List, Dict, Any
from django.db import transaction
from rest_framework.validators import ValidationError

from core.models import User
from core.users.services import CustomerService, AddressService, GeoService

# ===== CUSTOMER SERVICE ===== #
class CustomerAppService:
    """
    سرویس اپلیکیشن برای مدیریت مشتریان.
    این سرویس وظیفه هماهنگی بین لایه API و لایه دامین را دارد.
    """
    def __init__(self):
        self.domain_service = CustomerService()
        self.address_service = AddressService()
        self.geo_service = GeoService()
    
    # ========== CRUD OPERATIONS ======== #
    def get_customer_list(self, requester_user) -> List[Any]:
        """
        دریافت لیست تمام مشتریان.
        """
        return self.domain_service.get_all_customers_admin()

    def get_customer_details(self, requester_user, user_id: int) -> User:
        """
        دریافت جزئیات کامل مشتری برای نمایش در بخش Detail
        """
        try:
            customer = self.domain_service.get_customer_by_id_admin(user_id)
        except User.DoesNotExist:
            raise ValidationError("مشتری یافت نشد.")
        except Exception as e:
            raise e

        return User.objects.filter(pk=user_id)\
            .with_full_profile_admin()\
            .prefetch_related('addresses__province', 'addresses__city')\
            .first()

    @transaction.atomic
    def create_customer(self, requester_user, data: Dict[str, Any]):
        """
        ایجاد مشتری جدید + آدرس‌های احتمالی.
        """
        # ===== دریافت اطلاعات آدرس ===== #
        addresses_data = data.pop('addresses', [])

        # ===== ذخیره مشتری ===== #
        user = self.domain_service.create_customer(data)

        # ===== اگر آدرس وجود داشت، ذخیره آدرس ===== #
        if addresses_data:
            for addr in addresses_data:
                self.address_service.create_address(user.id, addr)
        
        return user

    def update_customer(self, requester_user, user_id: int, data: Dict[str, Any]):
        """
        بروزرسانی مشتری.
        """
        return self.domain_service.update_customer(user_id, data)

    def delete_customer(self, requester_user, user_id: int):
        """
        حذف یک مشتری.
        """
        self.domain_service.delete_customer(user_id)

    # ========== BULK OPERATIONS ======== #
    def bulk_delete(self, requester_user, ids: List[int]) -> Dict[str, int]:
        """
        حذف گروهی.
        """
        count = self.domain_service.bulk_delete_customers(ids)
        return {"deleted_count": count}

    def bulk_toggle_active(self, requester_user, ids: List[int], is_active: bool) -> int:
        """
        فعال/غیرفعال سازی گروهی.
        """
        return self.domain_service.bulk_toggle_active(ids, is_active)

    # ================= ADDRESS MANAGEMENT ================= #
    def get_customer_addresses(self, requester_user, user_id: int):
        """دریافت لیست آدرس‌های یک مشتری خاص"""
        return self.address_service.get_user_addresses(user_id)

    def add_address_to_customer(self, requester_user, user_id: int, data: Dict[str, Any]):
        """افزودن یک آدرس جدید به مشتری موجود"""
        # چک کردن وجود مشتری
        self.domain_service.get_customer_by_id_admin(user_id)
        return self.address_service.create_address(user_id, data)

    def update_customer_address(self, requester_user, user_id: int, address_id: int, data: Dict[str, Any]):
        """ویرایش آدرس مشتری"""
        return self.address_service.update_address(user_id, address_id, data)

    def delete_customer_address(self, requester_user, user_id: int, address_id: int):
        """حذف آدرس مشتری"""
        return self.address_service.delete_address(user_id, address_id)

    # ================= GEO DATA ================= #
    def get_provinces(self):
        return self.geo_service.get_all_provinces()

    def get_cities(self, province_id: int = None):
        if province_id:
            return self.geo_service.get_cities_by_province(province_id)
        return self.geo_service.get_all_cities()
