import logging
from typing import Dict, Any

from django.conf import settings
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.services import UserIdentityService
# from .verify_service import VerificationService

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
            raise ValidationError("خطایی در سیستم رخ داده است. لطفاً مجددا تلاش کنید.")

    # ========== LOGIN ========== #
    def login_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ورود مشتری.
        """
        username = data.get('username') or data.get('email')
        password = data.get('password')
        
        logger.info(f"Login attempt for: {username}")
        
        try:
            # ===== اعتبارسنجی ===== #
            user = authenticate(username=username, password=password)
            
            if not user:
                logger.warning(f"Invalid credentials for: {username}")
                raise ValidationError("نام کاربری یا رمز عبور اشتباه است.")
            
            # ===== حساب کاربری فعال باشد ===== #
            if not user.is_active:
                logger.warning(f"Login blocked - Inactive user: {username}")
                raise ValidationError("حساب کاربری شما غیرفعال است.")

            # ===== ایمیل تأیید شده باشد ===== #
            if not user.is_verified:
                raise ValidationError("لطفاً ابتدا ایمیل خود را تأیید کنید.")
            
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
            logger.error(f"Login error for {username}: {e}", exc_info=True)
            raise ValidationError("خطای سیستمی در ورود.")
