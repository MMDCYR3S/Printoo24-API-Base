from django.db import transaction
from ...utils.base_repository import BaseRepository
from core.models import Address

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
