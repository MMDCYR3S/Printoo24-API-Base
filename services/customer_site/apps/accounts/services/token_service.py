import logging
from typing import Dict

from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from core.models import User

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.token')
security_logger = logging.getLogger('accounts.services.security')


# ======= Token Service ======= #
class TokenService:
    """
    سرویس مدیریت توکن‌های JWT برای کاربران.
    
    این سرویس مسئول:
    - ایجاد توکن‌های Access و Refresh برای کاربر
    - رفرش کردن توکن‌های منقضی شده
    - انتقال توکن‌ها به لیست سیاه (Blacklist) برای لاگ‌اوت
    """
    
    @staticmethod
    def create_token_for_user(user: User) -> Dict[str, str]:
        """
        ایجاد توکن‌های Access و Refresh برای کاربر.
        
        Args:
            user: شیء کاربر
            
        Returns:
            Dict حاوی توکن‌های access و refresh
            
        Example:
            {
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            }
        """
        logger.info(f"Creating tokens for user - User ID: {user.id}, Username: {user.username}")
        
        try:
            refresh = RefreshToken.for_user(user)
            
            tokens = {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
            
            logger.debug(
                f"Tokens created successfully - "
                f"User ID: {user.id}, Access Token Length: {len(tokens['access'])}, "
                f"Refresh Token Length: {len(tokens['refresh'])}"
            )
            
            security_logger.info(
                f"New tokens issued - User: {user.username} ({user.email}), User ID: {user.id}"
            )
            
            return tokens
            
        except Exception as e:
            logger.error(
                f"Failed to create tokens - User ID: {user.id}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطا در ایجاد توکن احراز هویت.")
        
    @classmethod
    def refresh_token_for_user(cls, refresh_token: str) -> Dict[str, str]:
        """
        رفرش کردن توکن‌ها با استفاده از توکن Refresh کاربر.
        
        Args:
            refresh_token: توکن Refresh کاربر
            
        Returns:
            Dict حاوی توکن Access جدید
            
        Raises:
            ValidationError: در صورت نامعتبر بودن توکن
        """
        logger.info("Token refresh requested")
        
        try:
            refresh = RefreshToken(refresh_token)
            
            new_tokens = {
                "access": str(refresh.access_token)
            }
            user_id = refresh.get('user_id', 'Unknown')
            
            logger.info(
                f"Token refreshed successfully - User ID: {user_id}, "
                f"New Access Token Length: {len(new_tokens['access'])}"
            )
            
            security_logger.info(
                f"Token refreshed - User ID: {user_id}"
            )
            
            return new_tokens
            
        except TokenError as e:
            logger.warning(
                f"Invalid refresh token attempt - Error: {str(e)}"
            )
            security_logger.warning(
                f"Failed token refresh attempt - Invalid or expired token"
            )
            raise ValidationError("توکن نامعتبر است.")
            
        except Exception as e:
            logger.error(
                f"Unexpected error during token refresh - Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError("خطا در رفرش توکن.")
        
    @staticmethod
    def send_to_blacklist(refresh_token: str) -> None:
        """
        انتقال توکن به لیست سیاه (Blacklist) برای لاگ‌اوت کاربر.
        
        روند کار:
        1- ایجاد یک شیء RefreshToken از روی توکن دریافتی
        2- انتقال توکن به لیست سیاه
        3- پس از blacklist شدن، توکن دیگر قابل استفاده نیست
        
        Args:
            refresh_token: توکن Refresh که باید به لیست سیاه منتقل شود
            
        Note:
            در صورت بروز خطا (مثلاً توکن نامعتبر)، خطا را نادیده می‌گیریم
            چون هدف اصلی از بین بردن اعتبار توکن است.
        """
        logger.info("Blacklist token requested")
        
        try:
            # ==== ایجاد یک شیء از روی توکن ==== 
            token = RefreshToken(refresh_token)
            user_id = token.get('user_id', 'Unknown')
            # ==== انتقال توکن به لیست سیاه ==== #
            token.blacklist()
            
            logger.info(
                f"Token blacklisted successfully - User ID: {user_id}"
            )
            
            security_logger.info(
                f"User logged out - Token blacklisted for User ID: {user_id}"
            )
            
        except TokenError as e:
            logger.warning(
                f"Attempted to blacklist invalid token - Error: {str(e)}"
            )
            
        except Exception as e:
            logger.error(
                f"Unexpected error during token blacklisting - Error: {str(e)}",
                exc_info=True
            )