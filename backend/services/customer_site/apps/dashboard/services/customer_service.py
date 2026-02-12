import logging
from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, CustomerProfile, Role, UserRole, User
from core.users.services import CustomerService, AddressService
from apps.accounts.models import Wallet

# تعریف لاگر اختصاصی
logger = logging.getLogger('dashboard.services.customer')

class CustomerOrchestratorService:
    """
    سرویس ارکستراسیون برای مدیریت جامع مشتریان (User + Profile + Wallet + Role).
    """
    def __init__(self):
        self.user_repo = CustomerService()
        self.address_service = AddressService()

    def get_customer_list(self):
        logger.debug("Fetching customer list")
        return self.user_repo.get_all_customers()

    def get_customer_detail(self, user_id: int) -> User:
        """ دریافت جزئیات کامل مشتری به همراه پروفایل و کیف پول """
        logger.info(f"Fetching details for Customer {user_id}")
        user = self.user_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"Customer {user_id} not found")
            raise ValidationError("کاربر یافت نشد.")
        return user

    # ===== شاهکار: ایجاد اتمیک مشتری ===== #
    @transaction.atomic
    def create_customer(self, data: Dict[str, Any]) -> User:
        # ===== دریافت نام کاربری برای لاگ ===== #
        username = data.get('username')
        logger.info(f"START: Creating new customer '{username}'")
        
        try:
            # ===== تفکیک داده های ورودی ===== #
            user_payload = {
                k: v for k, v in data.items() 
                if k in ['username', 'email', 'password', 'is_active']
            }
            profile_payload = {
                k: v for k, v in data.items() 
                if k in ['first_name', 'last_name', 'phone_number', 'company', 'bio']
            }
            addresses_data = data.get('addresses', [])

            # ===== ایجاد کاربر در دیتابیس ===== #
            user = self.user_repo.create_customer(user_payload)
            logger.info(f"User created: ID={user.id}")

            # ===== ایجاد یا آپدیت پروفایل مشتری (حل مشکل عدم ذخیره مشخصات) ===== #
            CustomerProfile.objects.update_or_create(
                user=user,
                defaults=profile_payload
            )
            logger.debug(f"Profile synced for User {user.id}")
                
            # ===== ایجاد کیف پول (اصلاح باگ AttributeError و فیلد balance) ===== #
            Wallet.objects.get_or_create(
                user=user,
                defaults={'balance': 0}
            )
            logger.debug(f"Wallet initialized for User {user.id}")

            # ===== اختصاص نقش مشتری به کاربر ===== #
            customer_role = Role.objects.filter(is_customer=True).first()
            if customer_role:
                UserRole.objects.get_or_create(user=user, role=customer_role)
                logger.debug(f"Role '{customer_role.name}' assigned.")
            else:
                logger.warning("Customer Role not found!")

            # ===== ثبت آدرس های کاربر ===== #
            if addresses_data:
                for addr in addresses_data:
                    addr.pop('id', None)
                    self.address_service.create_address(user_id=user.id, data=addr)
            
            # ===== اتمام موفقیت آمیز عملیات ===== #
            logger.info(f"SUCCESS: Customer '{username}' created fully.")
            return user

        except Exception as e:
            # ===== لاگ خطا و بازگشت تغییرات ===== #
            logger.error(f"FAILED: Create customer '{username}'. Error: {str(e)}", exc_info=True)
            raise e

    # ===== ویرایش اتمیک مشتری ===== #
    @transaction.atomic
    def update_customer(self, user_id: int, data: Dict[str, Any]) -> User:
        logger.info(f"START: Updating Customer {user_id}")
        
        try:
            user = self.user_repo.get_customer_by_id(user_id)
            if not user:
                raise ValidationError("کاربر یافت نشد.")

            # ===== بروزرسانی اطلاعات پایه ===== #
            allowed_user_fields = ['email', 'username', 'is_active', 'password']
            user_update_data = {k: v for k, v in data.items() if k in allowed_user_fields}
            
            if user_update_data:
                self.user_repo.update_customer(user_id, user_update_data)
                logger.debug(f"User base info updated for {user_id}")
            
            # ===== تغییر رمز ===== #
            if 'password' in data and data['password']:
                user.set_password(data['password'])
                user.save()
                logger.info(f"Password updated for User {user_id}")

            # 3. بروزرسانی پروفایل
            if hasattr(user, 'customer_profile'):
                profile = user.customer_profile
                profile_nested_data = data.get('customer_profile', {})
                
                profile_fields = ['first_name', 'last_name', 'phone_number', 'company', 'bio']
                updated_fields = []
                for field in profile_fields:
                    if field in profile_nested_data:
                        setattr(profile, field, profile_nested_data[field])
                        updated_fields.append(field)
                
                if updated_fields:
                    profile.save()
                    logger.debug(f"Profile fields {updated_fields} updated for User {user_id}")

            logger.info(f"START: Updating Customer {user_id} and addresses")
        
            # ===== دریافت آدرس ===== #
            addresses_data = data.pop('addresses', None)

            # ===== آپدیت اطلاعات کاربر ===== #
            user = self.user_repo.update_customer(user_id, data)

            # ===== داده‌های آدرس ===== #
            if addresses_data is not None:
                self._handle_address_updates(user, addresses_data)

                logger.info(f"SUCCESS: Customer {user_id} updated.")
                return user

        except Exception as e:
            logger.error(f"FAILED: Update customer {user_id} failed. Error: {str(e)}", exc_info=True)
            raise e

    # ===== عملیات حذف تکی ===== #
    @transaction.atomic
    def delete_customer(self, user_id: int):
        logger.warning(f"START: Deleting Customer {user_id}")
        try:
            user = self.user_repo.get_customer_by_id(user_id)
            if user:
                user.delete()
                logger.info(f"SUCCESS: Customer {user_id} deleted.")
            else:
                logger.warning(f"Delete failed: Customer {user_id} not found.")
        except Exception as e:
            logger.error(f"FAILED: Delete customer {user_id} error: {str(e)}", exc_info=True)
            raise e

    # ===== عملیات بالک ===== #
    def bulk_toggle_status(self, user_ids: List[int], is_active: bool):
        logger.info(f"Bulk toggling status to {is_active} for {len(user_ids)} users")
        return self.user_repo.bulk_toggle_active(user_ids, is_active)

    def bulk_delete(self, user_ids: List[int]):
        logger.warning(f"Bulk deleting {len(user_ids)} users: {user_ids}")
        return self.user_repo.bulk_delete_customers(user_ids)

    def _handle_address_updates(self, user: User, addresses_data: List[Dict]):
        """
        متد کمکی برای مدیریت منطق:
        - اگر ID دارد -> آپدیت کن
        - اگر ID ندارد -> بساز
        - (اختیاری: اگر ID در لیست نیست -> حذف کن؟ فعلا فقط ایجاد/ویرایش را پیاده می‌کنیم)
        """
        for addr_data in addresses_data:
            address_id = addr_data.get('id')
            
            if address_id:
                # ===== حالت ویرایش ===== #
                existing_address = self.address_service.get_user_addresses(user.id).filter(id=address_id).exists()
                if existing_address:
                    self.address_service.update_address(user.id, address_id, addr_data)
                else:
                    logger.warning(f"Address ID {address_id} does not belong to user {user.id} or not found.")
            else:
                # ===== حالت ایجاد ===== #
                self.address_service.create_address(user.id, addr_data)
