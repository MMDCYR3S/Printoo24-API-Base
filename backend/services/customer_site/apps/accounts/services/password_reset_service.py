import logging
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from core.users.models import User
from core.users.services.identity import UserIdentityService
from core.domain.infrastructure.cache.cache_services import CacheService

from ..tasks import send_password_reset_email_task
# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.password_reset')
security_logger = logging.getLogger('accounts.services.security')


# ======= Password Reset Service ======= #
class PasswordResetService:
    """
    سرویس بازنشانی رمز عبور برای مدیریت کامل فرآیند فراموشی رمز عبور.
    
    این سرویس شامل:
    - ارسال لینک بازنشانی به ایمیل کاربر
    - اعتبارسنجی توکن و تأیید بازنشانی
    - محدودیت زمانی برای جلوگیری از اسپم
    - مدیریت کش برای کنترل درخواست‌های متوالی
    """
    
    # ===== متغیرهای کش ===== #
    PASSWORD_RESET_KEY_TIMEOUT_IN_SECONDS = timedelta(minutes=2).total_seconds()
    PASSWORD_RESET_KEY = "password_reset"
    
    def __init__(self):
        self._identity_service = UserIdentityService()
        self._cache_service = CacheService()
        self._token_generator = PasswordResetTokenGenerator()
        logger.debug("PasswordResetService initialized")
        
    def _get_cache_key(self, email: str) -> str:
        """ایجاد کلید کش برای جلوگیری از اسپم"""
        logger.debug(f"Generated cache key for: {email}")
        return f"{self.PASSWORD_RESET_KEY}_{email.lower().strip()}"
    
    def send_reset_link(self, email: str) -> None:
        """
        ارسال لینک بازنشانی.
        """
        logger.info(f"Password reset requested for: {email}")
        
        try:
            # ===== دریافت کاربر ===== #
            user = User.objects.filter(email=email).first()
            
            if not user:
                logger.warning(f"Reset requested for non-existent email: {email}")
                return
            
            # ===== جلوگیری از اسپم ===== #
            cache_key = self._get_cache_key(email)
            if self._cache_service.get(cache_key):
                logger.warning(f"Rate limit hit for: {email}")
                raise ValidationError("لطفاً چند دقیقه صبر کنید و سپس مجددا تلاش کنید.")
            
            # ===== توکن تولید ===== #
            token = self._token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://127.0.0.1:9010')
            reset_link = f"{frontend_url}/reset/password/confirm/{uid}/{token}/"
            
            # ===== ذخیره کش ===== #
            self._cache_service.set(
                cache_key, 
                True, 
                self.PASSWORD_RESET_KEY_TIMEOUT_IN_SECONDS
            )
            
            # ===== ارسال ایمیل ===== #
            send_password_reset_email_task.delay(user_email=email, reset_link=reset_link)
            
            logger.info(f"Reset link sent to: {email}")
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error sending reset link to {email}: {e}", exc_info=True)
            raise ValidationError("خطای سیستمی در پردازش درخواست.")
            
    def confirm_password_reset(
        self, 
        uidb64: str, 
        token: str, 
        new_password: str
    ) -> User:
        """
        تأیید نهایی و تغییر رمز عبور.
        """
        logger.info(f"Processing password reset confirmation.")
        
        try:
            # ===== دریافت کاربر ===== #
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                # ===== دریافت کاربر ===== #
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                security_logger.warning(f"Invalid UID/User in reset attempt: {uidb64}")
                raise ValidationError("لینک بازنشانی نامعتبر است.")

            # ===== اعتبارسنجی توکن ===== #
            if not self._token_generator.check_token(user, token):
                security_logger.warning(f"Invalid/Expired token for user: {user.email}")
                raise ValidationError("لینک منقضی شده یا نامعتبر است.")

            # ===== تغییر رمز عبور ===== #
            self._identity_service.change_password(user, new_password)
            
            logger.info(f"Password reset successful for user: {user.id}")
            security_logger.info(f"Password reset for: {user.email}")
            
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Critical error resetting password for UID {uidb64}: {e}", exc_info=True)
            raise ValidationError("خطای سیستمی در تغییر رمز عبور.")
