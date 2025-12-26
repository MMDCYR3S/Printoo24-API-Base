import logging
from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models import User, CustomerProfile, Role, UserRole
from core.users.services import CustomerService
from apps.accounts.models import Wallet

# تعریف لاگر اختصاصی
logger = logging.getLogger('dashboard.services.customer')

class CustomerOrchestratorService:
    """
    سرویس ارکستراسیون برای مدیریت جامع مشتریان (User + Profile + Wallet + Role).
    """
    def __init__(self):
        self.user_repo = CustomerService()

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
        """
        ایجاد مشتری به همراه تمام متعلقات (پروفایل، کیف پول، نقش).
        """
        username = data.get('username')
        logger.info(f"START: Creating new customer '{username}'")
        
        try:
            # ===== تفکیک داده ها ===== #
            user_data = {
                k: v for k, v in data.items() 
                if k in ['username', 'email', 'password', 'is_active']
            }
            profile_data = {
                k: v for k, v in data.items() 
                if k in ['first_name', 'last_name', 'phone_number', 'company', 'bio']
            }

            # ===== ایجاد کاربر ===== #
            user = self.user_repo.create_customer(user_data)
            logger.info(f"User created: ID={user.id}")

            # ===== ایجاد پروفایل در صورت نبود ===== #
            if not CustomerProfile.objects.filter(user=user).exists():
                CustomerProfile.objects.create(user=user)
                logger.debug(f"Profile created for User {user.id}")
                
            # ===== ایجاد کیف پول ===== #
            if not Wallet.objects.filter(user=user).exists():
                Wallet.objects.create(user=user, decimal=0)
                logger.debug(f"Wallet created for User {user.id}")

            # ===== ایجاد نقش ===== #
            customer_role = Role.objects.filter(is_customer=True).first()
            if customer_role:
                UserRole.objects.create(user=user, role=customer_role)
                logger.debug(f"Role '{customer_role.name}' assigned to User {user.id}")
            else:
                logger.warning("Customer Role not found! User created without explicit role.")

            logger.info(f"SUCCESS: Customer '{username}' (ID: {user.id}) created fully.")
            return user

        except Exception as e:
            logger.error(f"FAILED: Create customer '{username}' failed. Error: {str(e)}", exc_info=True)
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
            allowed_user_fields = ['email', 'username', 'is_active']
            user_update_data = {k: v for k, v in data.items() if k in allowed_user_fields}
            
            if user_update_data:
                self.user_repo.update_customer(user, user_update_data)
                logger.debug(f"User base info updated for {user_id}")
            
            # ===== تغییر رمز ===== #
            if 'password' in data and data['password']:
                user.set_password(data['password'])
                user.save()
                logger.info(f"Password updated for User {user_id}")

            # 3. بروزرسانی پروفایل
            if hasattr(user, 'customer_profile'):
                profile = user.customer_profile
                profile_fields = ['first_name', 'last_name', 'phone_number', 'company', 'bio']
                updated_fields = []
                for field in profile_fields:
                    if field in data:
                        setattr(profile, field, data[field])
                        updated_fields.append(field)
                
                if updated_fields:
                    profile.save()
                    logger.debug(f"Profile fields {updated_fields} updated for User {user_id}")

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
