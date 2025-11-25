from django.core.exceptions import ValidationError
from core.common.address import AddressRepository
from core.models import City, Province

# ===== User Address Service ===== # 
class UserAddressService:
    def __init__(self):
        self._repo = AddressRepository()

    def _validate_location(self, province_id, city_id):
        """چک می‌کند که شهر متعلق به استان انتخاب شده باشد"""
        if province_id and city_id:
            try:
                # ===== اعتبارسنجی شهر و تطابق آن با والد خود، یعنی استان ===== #
                city = City.objects.get(id=city_id)
                if city.province_id != province_id:
                    raise ValidationError({"city": "شهر انتخاب شده با استان مطابقت ندارد."})
            except City.DoesNotExist:
                raise ValidationError({"city": "شهر انتخاب شده نامعتبر است."})

    def get_all_addresses(self, user_id: int):
        """دریافت تمام آدرس های کاربر"""
        return self._repo.get_user_addresses(user_id)

    def add_address(self, user_id: int, data: dict):
        """اضافه کردن آدرس برای کاربر"""
        self._validate_location(data.get('province_id'), data.get('city_id'))
        return self._repo.create_address(user_id, data)

    def edit_address(self, user_id: int, address_id: int, data: dict):
        """ویرایش آدرس"""
        if 'province_id' in data or 'city_id' in data:
            self._validate_location(data.get('province_id'), data.get('city_id'))
        # ===== اعمال ویرایش بر روی آدرس ===== #
        address = self._repo.update_address(user_id, address_id, data)
        if not address:
            raise ValidationError("آدرس یافت نشد.")
        return address

    def remove_address(self, user_id: int, address_id: int):
        success = self._repo.delete_address(user_id, address_id)
        if not success:
            raise ValidationError("آدرس یافت نشد یا قابل حذف نیست.")
