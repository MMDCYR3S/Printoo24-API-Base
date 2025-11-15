import logging
from datetime import timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from core.models import User
from core.common.users.user_services import UserService
from core.common.cache.cache_service import CacheService

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
    PASSWORD_RESET_KEY_TIMEOUT_IN_SECONDS = timedelta(minutes=5).total_seconds()
    PASSWORD_RESET_KEY = "password_reset"
    
    def __init__(self, user_service: UserService, cache_service: CacheService):
        """
        مقداردهی اولیه سرویس بازنشانی رمز عبور
        
        Args:
            user_service: سرویس مدیریت کاربران
            cache_service: سرویس مدیریت کش
        """
        self._user_service = user_service
        self._cache_service = cache_service
        self._token_generator = PasswordResetTokenGenerator()
        logger.debug("PasswordResetService initialized")
        
    def _get_cache_key(self, email: str) -> str:
        """
        ایجاد کلید کش برای ذخیره‌سازی ایمیل و اعتبارسنجی لینک رمز عبور.
        همچنین ایجاد یک تایمر برای عدم اسپم در این صفحه.
        
        Args:
            email: ایمیل کاربر
            
        Returns:
            str: کلید کش منحصر به فرد برای این ایمیل
        """
        cache_key = f"{self.PASSWORD_RESET_KEY}_{email}"
        logger.debug(f"Generated cache key: {cache_key}")
        return cache_key
    
    def send_reset_link(self, email: str) -> None:
        """
        ارسال لینک بازنشانی رمز عبور به ایمیل کاربر.
        
        فرآیند:
        1- بررسی وجود کاربر با این ایمیل
        2- بررسی محدودیت زمانی (جلوگیری از اسپم)
        3- ایجاد توکن و لینک بازنشانی
        4- ارسال ایمیل به کاربر
        
        Args:
            email: ایمیل کاربر
            
        Raises:
            ValidationError: در صورت درخواست مکرر یا خطا در ارسال
        """
        logger.info(f"Password reset link requested for email: {email}")
        
        try:
            # ===== دریافت کاربر بر اساس ایمیل ===== #
            user = self._user_service.get_by_email(email)
            
            if not user:
                # برای امنیت، خطای مشخص نمی‌دهیم که کاربر وجود ندارد
                logger.warning(f"Password reset requested for non-existent email: {email}")
                security_logger.warning(
                    f"Password reset attempt for non-existent email: {email}"
                )
                # پیام عمومی برای جلوگیری از User Enumeration
                raise ValidationError("درخواست شما ثبت شد. در صورت وجود حساب کاربری، لینک بازنشانی ارسال خواهد شد.")
            
            logger.debug(f"User found for password reset - User ID: {user.id}, Email: {email}")
            
            # ===== بررسی اینکه آیا قبلاً از کش استفاده شده یا خیر ===== #
            cache_key = self._get_cache_key(email)
            
            if self._cache_service.get(cache_key):
                logger.warning(
                    f"Duplicate password reset request blocked - Email: {email}, "
                    f"Cache still active"
                )
                security_logger.warning(
                    f"Potential spam attempt - Multiple password reset requests for: {email}"
                )
                raise ValidationError(
                    "شما قبلاً یک‌بار درخواست بازنشانی رمز عبور دادید. "
                    "باید کمی صبر کنید تا ایمیل برای شما ارسال شود."
                )
            
            logger.debug(f"Cache check passed for email: {email}")
            
            # ===== ایجاد کش برای ایمیل و اعتبارسنجی ===== #
            self._cache_service.set(
                cache_key, 
                True, 
                self.PASSWORD_RESET_KEY_TIMEOUT_IN_SECONDS
            )
            logger.debug(
                f"Cache set for password reset - Email: {email}, "
                f"Timeout: {self.PASSWORD_RESET_KEY_TIMEOUT_IN_SECONDS}s"
            )
            
            # ===== ایجاد توکن و UID ===== #
            token = self._token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            logger.debug(
                f"Password reset token generated - User ID: {user.id}, UID: {uid}"
            )
            
            # ===== ایجاد لینک بازنشانی ===== #
            reset_link = f"http://127.0.0.1:9010/reset/password/confirm/{uid}/{token}/"
            
            logger.info(
                f"Password reset link generated - User ID: {user.id}, Email: {email}"
            )
            
            # ===== ارسال ایمیل به سمت کاربر (Async Task) ===== #
            logger.debug(f"Triggering email task for password reset - Email: {email}")
            send_password_reset_email_task.delay(user_email=email, reset_link=reset_link)
            
            logger.info(
                f"Password reset email task queued successfully - "
                f"User ID: {user.id}, Email: {email}"
            )
            
        except ValidationError:
            # خطاهای ValidationError را مستقیماً پرتاب می‌کنیم
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error during password reset link generation - "
                f"Email: {email}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطای غیرمنتظره در ارسال لینک بازنشانی رمز عبور.")
            
    def confirm_password_reset(
        self, 
        uidb64: str, 
        token: str, 
        new_password: str
    ) -> User:
        """
        تأیید توکن و لینک بازنشانی و تنظیم رمز عبور جدید.
        
        پس از اینکه لینک مورد نظر تأیید شد (به واسطه توکن و ID)، کاربر
        باید رمز عبور جدید خود را وارد کند و پس از آن، رمز عبور جدید
        ایجاد شده و کاربر می‌تواند با آن وارد حساب کاربری خود شود.
        
        Args:
            uidb64: شناسه رمزگذاری شده کاربر (Base64)
            token: توکن بازنشانی رمز عبور
            new_password: رمز عبور جدید
            
        Returns:
            User: کاربری که رمز عبور او تغییر یافته است
            
        Raises:
            ValidationError: در صورت نامعتبر بودن لینک، توکن یا انقضای زمان
        """
        logger.info(f"Password reset confirmation attempt - UID: {uidb64}")
        
        try:
            # ===== بررسی و دکد شناسه کاربر ===== #
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = self._user_service.get_by_id(uid)
                
                logger.debug(
                    f"UID decoded successfully - User ID: {uid}, Username: {user.username if user else 'N/A'}"
                )
                
            except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
                logger.warning(
                    f"Invalid UID in password reset - UID: {uidb64}, Error: {str(e)}"
                )
                security_logger.warning(
                    f"Suspicious password reset attempt - Invalid UID: {uidb64}"
                )
                user = None

            if user is None:
                logger.warning(f"User not found for password reset - UID: {uidb64}")
                raise ValidationError("لینک بازنشانی نامعتبر یا منقضی شده است.")
            
            # ===== بررسی کش ===== #
            cache_key = self._get_cache_key(user.email)
            
            if not self._cache_service.get(cache_key):
                logger.warning(
                    f"Expired password reset link accessed - "
                    f"User ID: {user.id}, Email: {user.email}, Cache expired"
                )
                security_logger.warning(
                    f"Expired password reset attempt - User: {user.username} ({user.email})"
                )
                raise ValidationError("لینک بازنشانی رمز عبور منقضی شده است.")
            
            logger.debug(f"Cache validation passed for user: {user.email}")
                
            # ===== بررسی توکن ===== #
            if not self._token_generator.check_token(user, token):
                logger.warning(
                    f"Invalid token for password reset - "
                    f"User ID: {user.id}, Email: {user.email}"
                )
                security_logger.warning(
                    f"Invalid token used in password reset - User: {user.username} ({user.email})"
                )
                raise ValidationError("لینک بازنشانی نامعتبر یا منقضی شده است.")
            
            logger.debug(f"Token validated successfully for user: {user.email}")
            
            # ===== پاک کردن کش و تغییر رمز عبور ===== #
            logger.debug(f"Deleting cache and updating password - User ID: {user.id}")
            self._cache_service.delete(cache_key)
            
            updated_user = self._user_service.set_password(user, new_password)
            
            logger.info(
                f"Password reset completed successfully - "
                f"User ID: {updated_user.id}, Username: {updated_user.username}"
            )
            security_logger.info(
                f"Password changed via reset link - User: {updated_user.username} ({updated_user.email})"
            )
            
            return updated_user
            
        except ValidationError:
            # خطاهای ValidationError را مستقیماً پرتاب می‌کنیم
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error during password reset confirmation - "
                f"UID: {uidb64}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطای غیرمنتظره در تأیید بازنشانی رمز عبور.")
