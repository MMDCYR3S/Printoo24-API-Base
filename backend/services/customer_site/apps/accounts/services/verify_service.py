import hmac
import logging
import random
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.conf import settings

from ..tasks import send_verification_email_task
from core.domain.infrastructure.cache.cache_services import CacheService
from core.users.models import User
from core.users.services.identity import UserIdentityService

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.verification')
security_logger = logging.getLogger('accounts.services.security')


# ======= Verification Service ======= #
class VerificationService:
    """
    سرویس اپلیکیشن برای مدیریت فرآیند ارسال و بررسی کد تایید.
    (Application Layer Service)
    """
    
    VERIFICATION_CODE_TIMEOUT_IN_SECONDS = timedelta(minutes=5).total_seconds()
    VERIFICATION_CODE_KEY_PREFIX = "verification_code"
    
    def __init__(self):
        self._identity_service = UserIdentityService()
        self._cache_service = CacheService()
        logger.debug("VerificationService initialized")
    
    def _generate_code_number(self) -> str:
        """ایجاد کد 6 رقمی"""
        code = str(random.randint(100000, 999999))
        return code
    
    def _get_cache_key(self, email: str) -> str:
        cache_key = f"{self.VERIFICATION_CODE_KEY_PREFIX}_{email.lower().strip()}"
        logger.debug(f"Generated verification cache key for email: {email}")
        return cache_key
    
    def send_verification_code(self, email: str) -> None:
        """ارسال کد فعال‌سازی"""
        logger.info(f"Initiating verification code send for: {email}")
        
        try:
            # ===== ایجاد کد فعال‌سازی ===== # 
            code = self._generate_code_number()
            cache_key = self._get_cache_key(email)
            
            self._cache_service.set(cache_key, code, self.VERIFICATION_CODE_TIMEOUT_IN_SECONDS)
            
            logger.debug(
                f"Verification code cached - Email: {email}, "
                f"Timeout: {self.VERIFICATION_CODE_TIMEOUT_IN_SECONDS}s"
            )
            
            #  ===== ارسال ایمیل (Async Task) ===== #
            if settings.DEBUG:
                logger.info(f"DEBUG MODE - Verification Code for {email}: {code}")

            send_verification_email_task.delay(email, code)
            
            logger.info(f"Verification code sent/queued for: {email}")
            
        except Exception as e:
            logger.error(f"Error sending verification code to {email}: {e}", exc_info=True)
            raise ValidationError("خطا در ارسال کد فعال‌سازی. لطفاً مجددا تلاش کنید.")
        
    # ========== VERIFY CODE ========== #
    def verify_code(self, email: str, code: str):
        """
        بررسی کد و فعال‌سازی کاربر.
        """
        logger.info(f"Verifying code for: {email}")
        
        try:
            # ===== بررسی وجود کاربر ===== #
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                logger.warning(f"Verification failed - User not found: {email}")
                raise ValidationError("کاربری با این ایمیل یافت نشد.")

            # ===== بررسی فعال‌سازی ===== #
            if user.is_verified:
                raise ValidationError("این حساب قبلاً فعال شده است.")

            # ===== بررسی وجود کد ===== #
            cache_key = self._get_cache_key(email)
            cached_code = self._cache_service.get(cache_key)
            
            if not cached_code:
                raise ValidationError("کد تأیید منقضی شده است. لطفاً درخواست کد جدید دهید.")
            
            # ===== بررسی کد ===== #
            if not hmac.compare_digest(str(cached_code), str(code)):
                security_logger.warning(f"Invalid code attempt for {email}")
                raise ValidationError("کد وارد شده صحیح نیست.")

            # ===== فعال‌سازی کاربر ===== #
            verified_user = self._identity_service.verify_user(user)
            
            # ===== پاک کردن کد ===== #
            self._cache_service.delete(cache_key)
            
            logger.info(f"User verified successfully: {email}")
            return verified_user
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating code for {email}: {e}", exc_info=True)
            raise ValidationError("خطای سیستمی در تأیید کد.")
