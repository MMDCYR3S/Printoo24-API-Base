import hmac
import logging
import random
from datetime import timedelta

from django.core.exceptions import ValidationError

from ..tasks import send_verification_email_task
from core.domain.cache.cache_services import CacheService
from core.domain.users.services import UserDomainService

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.verification')
security_logger = logging.getLogger('accounts.services.security')


# ======= Verification Service ======= #
class VerificationService:
    """
    سرویس برای ارسال ایمیل به سمت کاربر برای احراز هویت و فعال‌سازی حساب کاربری.
    
    این سرویس شامل:
    - ایجاد کد تصادفی 6 رقمی
    - ذخیره کد در کش با محدودیت زمانی
    - ارسال ایمیل حاوی کد فعال‌سازی
    - اعتبارسنجی کد و فعال‌سازی حساب کاربری
    """
    
    VERIFICATION_CODE_TIMEOUT_IN_SECONDS = timedelta(minutes=5).total_seconds()
    VERIFICATION_CODE_KEY_PREFIX = "verification_code"
    
    def __init__(self):
        """
        مقداردهی اولیه سرویس احراز هویت.
        
        Args:
            user_service: سرویس مدیریت کاربران
        """
        self._user_service = UserDomainService()
        logger.debug("VerificationService initialized")
    
    def _generate_code_number(self) -> str:
        """
        ایجاد یک عدد تصادفی 6 رقمی به صورت رشته برای فعال‌سازی.
        
        Returns:
            str: کد 6 رقمی تصادفی
        """
        code = str(random.randint(100000, 999999))
        logger.debug(f"Verification code generated: {code[:2]}****")
        return code
    
    def _get_cache_key(self, email: str) -> str:
        """
        ایجاد کلید کش برای ذخیره کد فعال‌سازی.
        
        کلید کش به صورت منحصر به فرد و با استفاده از ایمیل شخص ساخته می‌شود.
        
        Args:
            email: ایمیل کاربر
            
        Returns:
            str: کلید کش منحصر به فرد
        """
        cache_key = f"{self.VERIFICATION_CODE_KEY_PREFIX}_{email.lower().strip()}"
        logger.debug(f"Generated verification cache key for email: {email}")
        return cache_key
    
    def send_verification_code(self, email: str) -> None:
        """
        ارسال ایمیل فعال‌سازی حساب کاربری به همراه کد.
        
        فرآیند:
        1- ایجاد کد تصادفی 6 رقمی
        2- ذخیره کد در کش با timeout مشخص
        3- ارسال ایمیل به صورت async
        
        Args:
            email: ایمیل کاربر برای ارسال کد
        """
        logger.info(f"Sending verification code to email: {email}")
        
        try:
            # ===== ایجاد کد فعال‌سازی ===== # 
            code = self._generate_code_number()
            logger.debug(f"Verification code created for email: {email}")

            # ===== ذخیره کد فعال‌سازی در کش ===== # 
            cache_key = self._get_cache_key(email)
            
            # ===== ایجاد کش با استفاده از سرویس ===== # 
            cache_service = CacheService()
            cache_service.set(cache_key, code, self.VERIFICATION_CODE_TIMEOUT_IN_SECONDS)
            
            logger.debug(
                f"Verification code cached - Email: {email}, "
                f"Timeout: {self.VERIFICATION_CODE_TIMEOUT_IN_SECONDS}s"
            )
            
            #  ===== ارسال ایمیل (Async Task) ===== #
            logger.debug(f"Triggering verification email task for: {email}")
            send_verification_email_task.delay(email, code)
            
            logger.info(f"Verification email task queued successfully for: {email}")
            
        except Exception as e:
            logger.error(
                f"Failed to send verification code - Email: {email}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطا در ارسال کد فعال‌سازی.")
        
    def verify_code(self, email: str, code: str) -> bool:
        """
        اعتبارسنجی کد ارسال شده به کاربر.
        
        فرایند:
        1- بررسی وجود کاربر با ایمیل مورد نظر
        2- بررسی اینکه آیا کاربر قبلاً فعال شده یا خیر
        3- مقایسه کد ارسالی با کد ذخیره شده در کش
        4- فعال‌سازی حساب کاربری و حذف کد از کش
        
        Args:
            email: ایمیل کاربر
            code: کد ارسال شده توسط کاربر
            
        Returns:
            User: کاربر فعال شده
            
        Raises:
            ValidationError: در صورت نامعتبر بودن ایمیل، کد یا فعال بودن قبلی حساب
        """
        logger.info(f"Verification code check requested for email: {email}")
        
        try:
            if not hmac.compare_digest(cache_code, str(code)):
                raise ValueError("Invalid verification code")
                
            # ===== صحت‌سنجی کاربر ===== #
            user = self._user_service.get_by_email(email)
            
            if not user:
                logger.warning(f"Verification attempt for non-existent email: {email}")
                security_logger.warning(
                    f"Verification attempt for non-existent email: {email}"
                )
                raise ValidationError("این ایمیل موجود نمی‌باشد.")
            
            logger.debug(f"User found for verification - User ID: {user.id}, Email: {email}")
            
            if user.is_verified:
                logger.warning(
                    f"Verification attempt for already verified user - "
                    f"User ID: {user.id}, Email: {email}"
                )
                raise ValidationError("این حساب کاربری قبلاً فعال شده است.")
            
            # ====== بررسی کش و مقایسه کد ===== #
            cache_service = CacheService()
            cache_key = self._get_cache_key(email)
            cache_code = cache_service.get(cache_key)
            
            if not cache_code:
                logger.warning(
                    f"Verification code expired or not found - "
                    f"User ID: {user.id}, Email: {email}"
                )
                security_logger.warning(
                    f"Expired verification code attempt - User: {user.username} ({email})"
                )
                raise ValidationError("کد فعال‌سازی منقضی شده است. لطفاً کد جدید درخواست کنید.")
            
            if cache_code != str(code):
                logger.warning(
                    f"Invalid verification code submitted - "
                    f"User ID: {user.id}, Email: {email}, "
                    f"Expected: {cache_code[:2]}****, Received: {str(code)[:2]}****"
                )
                security_logger.warning(
                    f"Invalid verification code - User: {user.username} ({email})"
                )
                raise ValidationError("کد ارسال شده صحیح نیست.")
            
            logger.debug(f"Verification code matched for user: {email}")
            
            # ===== فعال‌سازی کاربر و حذف کش ===== #
            logger.info(f"Activating user account - User ID: {user.id}, Email: {email}")
            verified_user = self._user_service.set_user_as_verified(user)
            
            cache_service.delete(cache_key)
            logger.debug(f"Verification code cache deleted for email: {email}")
            
            logger.info(
                f"User account verified successfully - "
                f"User ID: {verified_user.id}, Username: {verified_user.username}"
            )
            
            security_logger.info(
                f"Account activated - User: {verified_user.username} ({verified_user.email})"
            )
            
            return verified_user
            
        except ValidationError:
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error during code verification - Email: {email}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطای غیرمنتظره در تأیید کد.")
    