import logging
from typing import Dict, Any

from django.conf import settings
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User, Role, UserRole
from core.domain.users.services import UserDomainService
from .verify_service import VerificationService

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.auth')


# ======= Authentication Service ======= #
class AuthService:
    """
    کلاس سرویس احراز هویت برای مدیریت ثبت‌نام و ورود کاربران.
    این سرویس منطق کامل ثبت‌نام، اختصاص نقش و ورود کاربر را کپسوله می‌کند.
    """
    def __init__(self):
        """تعیین سرویس‌های وابسته"""
        self._user_domain_service = UserDomainService()
        self._verify_service = VerificationService()
        logger.debug("AuthService initialized")
    
    def _generate_tokens(self, user) -> Dict[str, str]:
        """متد داخلی برای تولید توکن"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    @transaction.atomic
    def register_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ثبت نام مشتری (Customer Registration Flow)
        """
        logger.info(f"Registering new customer: {data.get('email')}")
        
        username = data.get('username', 'N/A')
        
        try:
            # ===== ایجاد کاربر ===== #
            user = self._user_domain_service.register_new_user(data)
            logger.info(f"User created successfully - User ID: {user.id}, Username: {user.username}")
            
            # ===== ارسال کد تأیید ===== #
            logger.info(f"Sending verification code to email: {user.email}")
            self._verify_service.send_verification_code(user.email)
            logger.info(f"Verification code sent successfully to {user.email}")
            
            logger.info(
                f"User registration completed successfully - "
                f"User ID: {user.id}, Username: {user.username}"
            )
            tokens = self._generate_tokens(user)
            
            return {
                "user": user,
                "tokens": tokens
            }
            
        except ValidationError as e:
            logger.warning(
                f"User registration failed - Email: {data.get('email')}, Error: {str(e)}"
            )
            raise ValidationError(f"خطای اعتبارسنجی: {str(e)}")
            
        except Exception as e:
            logger.error(
                f"Unexpected error during user registration - Username: {username}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError(f"خطای غیرمنتظره در ثبت‌نام: {str(e)}")

    def login_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ورود کاربر و صدور توکن
        """
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Login attempt - Username: {username}")
        
        try:
            # ====== اعتبارسنجی کاربر ====== #
            user = authenticate(username=username, password=password)
            
            if not user:
                logger.warning(f"Failed login attempt - Invalid credentials for username: {username}")
                raise ValidationError("نام کاربری یا رمز عبور نامعتبر است")
            
            logger.debug(f"User authenticated successfully - User ID: {user.id}, Username: {user.username}")
            
            # ====== بررسی وضعیت فعال بودن کاربر ====== #
            if not user.is_active:
                logger.warning(f"Login denied - Inactive user: {user.username} (ID: {user.id})")
                raise ValidationError("حساب کاربری غیرفعال است")
            
            # ====== ایجاد توکن برای کاربر پس از ورود ====== #
            logger.debug(f"Generating authentication tokens for user: {user.username}")
            tokens = self._generate_tokens(user)
            
            logger.info(
                f"User logged in successfully - "
                f"User ID: {user.id}, Username: {user.username}"
            )
            
            return {
                "user": user,
                "tokens": tokens,
            }
            
        except ValidationError:
            # خطاهای ValidationError را مستقیماً پرتاب می‌کنیم
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error during login - Username: {username}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError(f"خطای غیرمنتظره در ورود: {str(e)}")
