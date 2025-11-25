from django.db import transaction
from ..repositories import IRepository
from core.models import Address

class AddressRepository(IRepository[Address]):
    def __init__(self):
        super().__init__(Address)

    def get_user_addresses(self, user_id: int):
        """دریافت تمام آدرس‌های کاربر (پیش‌فرض اول نمایش داده شود)"""
        return self.model.objects.filter(user_id=user_id).select_related('province', 'city').order_by('-is_default', '-created_at')

    def get_address_by_id(self, user_id: int, address_id: int):
        """دریافت یک آدرس خاص با چک کردن مالکیت کاربر"""
        return self.model.objects.filter(user_id=user_id, id=address_id).first()

    def create_address(self, user_id: int, data: dict) -> Address:
        """
        اضافه کردن آدرس برای کاربر
        """
        return self.model.objects.create(user_id=user_id, **data)

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

    def delete_address(self, user_id: int, address_id: int):
        address = self.get_address_by_id(user_id, address_id)
        if address:
            address.delete()
            return True
        return False
