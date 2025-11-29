import logging
from django.core.exceptions import ValidationError
from core.domain.address import AddressRepository
from core.models import City

# ===== تعریف لاگر اختصاصی برای سرویس آدرس ===== #
logger = logging.getLogger('userprofile.services.address')

class UserAddressService:
    """
    سرویس مدیریت آدرس‌های کاربر.
    
    این سرویس وظیفه دارد آدرس‌های کاربر را ایجاد، ویرایش، حذف و بازیابی کند.
    همچنین اعتبارسنجی منطقی (مثل تطابق شهر و استان) در این لایه انجام می‌شود.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی مخزن آدرس ===== #
        self._repo = AddressRepository()

    def _validate_location(self, province_id, city_id):
        """
        بررسی تطابق شهر و استان انتخاب شده.
        
        Raises:
            ValidationError: اگر شهر با استان مطابقت نداشته باشد یا شهر نامعتبر باشد.
        """
        if province_id and city_id:
            try:
                # ===== اعتبارسنجی شهر و تطابق آن با والد خود، یعنی استان ===== #
                city = City.objects.get(id=city_id)
                if city.province_id != province_id:
                    logger.warning(f"Location mismatch: City {city_id} does not belong to Province {province_id}")
                    raise ValidationError({"city": "شهر انتخاب شده با استان مطابقت ندارد."})
            except City.DoesNotExist:
                logger.warning(f"Invalid City ID provided: {city_id}")
                raise ValidationError({"city": "شهر انتخاب شده نامعتبر است."})

    def get_all_addresses(self, user_id: int):
        """
        دریافت تمام آدرس‌های ثبت شده برای یک کاربر.
        """
        logger.info(f"Fetching addresses for User ID: {user_id}")
        return self._repo.get_user_addresses(user_id)

    def add_address(self, user_id: int, data: dict):
        """
        افزودن آدرس جدید برای کاربر.
        """
        logger.info(f"Adding new address for User ID: {user_id}")
        
        try:
            # ===== اعتبارسنجی موقعیت مکانی ===== #
            self._validate_location(data.get('province_id'), data.get('city_id'))
            
            # ===== ایجاد آدرس ===== #
            address = self._repo.create_address(user_id, data)
            logger.info(f"Address created successfully with ID: {address.id}")
            return address
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error adding address for User ID: {user_id}")
            raise ValidationError("خطای سیستمی در ثبت آدرس.")

    def edit_address(self, user_id: int, address_id: int, data: dict):
        """
        ویرایش آدرس موجود.
        """
        logger.info(f"Editing Address ID: {address_id} for User ID: {user_id}")
        
        try:
            # ===== اعتبارسنجی مجدد موقعیت مکانی در صورت تغییر ===== #
            if 'province_id' in data or 'city_id' in data:
                self._validate_location(data.get('province_id'), data.get('city_id'))
            
            # ===== اعمال ویرایش بر روی آدرس ===== #
            address = self._repo.update_address(user_id, address_id, data)
            
            if not address:
                logger.warning(f"Address ID {address_id} not found or access denied for User ID: {user_id}")
                raise ValidationError("آدرس یافت نشد.")
            
            logger.info(f"Address ID: {address_id} updated successfully.")
            return address
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error editing address {address_id}")
            raise ValidationError("خطای سیستمی در ویرایش آدرس.")

    def remove_address(self, user_id: int, address_id: int):
        """
        حذف آدرس کاربر.
        """
        logger.info(f"Removing Address ID: {address_id} for User ID: {user_id}")
        
        try:
            success = self._repo.delete_address(user_id, address_id)
            if not success:
                logger.warning(f"Address ID {address_id} could not be deleted (Not found/Access denied).")
                raise ValidationError("آدرس یافت نشد یا قابل حذف نیست.")
            
            logger.info(f"Address ID: {address_id} deleted successfully.")
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            logger.exception(f"Unexpected error removing address {address_id}")
            raise ValidationError("خطای سیستمی در حذف آدرس.")
