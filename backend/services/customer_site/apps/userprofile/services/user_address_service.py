import logging
from django.core.exceptions import ValidationError

from core.users.services import AddressService
from core.models import City, Province
from core.infrastructure.messages import msg_provider

# ===== تعریف لاگر اختصاصی برای سرویس آدرس ===== #
logger = logging.getLogger('userprofile.services.address')

# ========== ADDRESS SERVICE ========== #
class UserAddressService:
    """
    سرویس مدیریت آدرس‌های کاربر.
    
    این سرویس وظیفه دارد آدرس‌های کاربر را ایجاد، ویرایش، حذف و بازیابی کند.
    همچنین اعتبارسنجی منطقی (مثل تطابق شهر و استان) در این لایه انجام می‌شود.
    """
    
    def __init__(self):
        # ===== تزریق وابستگی مخزن آدرس ===== #
        self._repo = AddressService()

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
                    raise ValidationError(msg_provider.get("profile.E8001"))
            except City.DoesNotExist:
                logger.warning(f"Invalid City ID provided: {city_id}")
                raise ValidationError(msg_provider.get("profile.E8002"))

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
            raise ValidationError(msg_provider.get("profile.E8004"))

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
                raise ValidationError(msg_provider.get("profile.E8003"))
            
            logger.info(f"Address ID: {address_id} updated successfully.")
            return address
            
        except ValidationError as e:
            raise e
        except Exception as e:
            logger.exception(f"Unexpected error editing address {address_id}")
            raise ValidationError(msg_provider.get("profile.E8004"))

    def remove_address(self, user_id: int, address_id: int):
        """
        حذف آدرس کاربر.
        """
        logger.info(f"Removing Address ID: {address_id} for User ID: {user_id}")
        
        try:
            success = self._repo.delete_address(user_id, address_id)
            if not success:
                logger.warning(f"Address ID {address_id} could not be deleted (Not found/Access denied).")
                raise ValidationError("ناونیشان نەدۆزرایەوە یان ناتوانرێت بسڕدرێتەوە.")
            
            logger.info(f"Address ID: {address_id} deleted successfully.")
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            logger.exception(f"Unexpected error removing address {address_id}")
            raise ValidationError("دانیشتنی بەکارهێنەر یان سێشن نەدۆزرایەوە.")

    def get_all_provinces(self):
        """
        دریافت لیست تمام استان‌ها مرتب شده بر اساس نام.
        """
        return Province.objects.all().order_by('name')

    def get_cities_by_province(self, province_id: int):
        """
        دریافت شهرهای یک استان خاص.
        """
        if not province_id:
            return City.objects.none()
            
        return City.objects.filter(province_id=province_id).order_by('name')
    
    def get_all_cities(self):
        """دریافت کل شهرها (در صورت نیاز)"""
        return City.objects.all().order_by('name')
    