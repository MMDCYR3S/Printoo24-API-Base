import logging
from typing import Dict, Any

from django.conf import settings
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.services import UserIdentityService
from core.infrastructure.messages import msg_provider

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.auth')


# ======= Authentication Application Service ======= #
class AuthService:
    """
    سرویس اپلیکیشن احراز هویت (Application Layer).
    وظیفه: هماهنگی بین سرویس دامین (ثبت نام) و سرویس‌های جانبی (ایمیل، توکن).
    """

    def __init__(self):
        self._identity_service = UserIdentityService()
        # self._verify_service = VerificationService()
        logger.debug("AuthService initialized with UserIdentityService")
    
    def _generate_tokens(self, user) -> Dict[str, str]:
        """تولید اکسس توکن و رفرش توکن"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    # ========== REGISTER ========== #
    @transaction.atomic
    def register_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        مدیریت جریان ثبت نام مشتری.
        Flow: Validate & Create (Domain) -> Send Email (Notification) -> Generate Token (Auth)
        """
        email = data.get('email')
        logger.info(f"Starting registration process for: {email}")
        
        try:
            # ===== ایجاد یوزر ===== # 
            user = self._identity_service.register_new_customer(data)
            self._identity_service.verify_user(user)
            
            logger.info(f"User created in DB - ID: {user.id}")
            
            # ===== ارسال کد تأیید ===== #
            # logger.info(f"Sending verification code to: {email}")
            # self._verify_service.send_verification_code(user.email)
            
            # ===== تولید توکن ===== #
            tokens = self._generate_tokens(user)
            
            return {
                "user": user,
                "tokens": tokens
            }
            
        except ValidationError as e:
            logger.warning(f"Registration validation failed for {email}: {e}")
            raise e
            
        except Exception as e:
            logger.error(f"Critical error during registration for {email}: {e}", exc_info=True)
            raise ValidationError("هەڵەیەک لە سیستمەکەدا ڕوویداوە. تکایە دووبارە هەوڵ بدەرەوە.")

    # ========== LOGIN ========== #
    def login_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ورود مشتری.
        """
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        logger.info(f"Login attempt for: {phone_number}")
        
        try:
            # ===== اعتبارسنجی ===== #
            user = authenticate(phone_number=phone_number, password=password)
            
            if not user:
                logger.warning(f"Invalid credentials for: {phone_number}")
                raise ValidationError(msg_provider.get("auth.E1001"))
            
            # ===== حساب کاربری فعال باشد ===== #
            if not user.is_active:
                logger.warning(f"Login blocked - Inactive user: {phone_number}")
                raise ValidationError(msg_provider.get("auth.E1002"))
            
            # ===== تولید توکن ===== #
            tokens = self._generate_tokens(user)
            
            logger.info(f"User logged in: {user.id}")
            
            return {
                "user": user,
                "tokens": tokens,
            }
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Login error for {phone_number}: {e}", exc_info=True)
            raise ValidationError(msg_provider.get("auth.E1003"))

    # ========== UNIFIED AUTH ========== #
    def authenticate_or_register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        دریافت اطلاعات و تصمیم‌گیری برای لاگین یا ثبت‌نام
        """
        phone_number = data.get('phone_number')
        
        from core.models import User
        user_exists = User.objects.filter(phone_number=phone_number).exists()

        if user_exists:
            logger.info(f"User found. Routing to login flow: {phone_number}")
            result = self.login_customer(data)
            result['action'] = 'login'
            return result
        else:
            logger.info(f"User not found. Routing to registration flow: {phone_number}")
            result = self.register_customer(data)
            result['action'] = 'register'
            return result
