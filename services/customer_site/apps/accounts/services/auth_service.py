import logging
from typing import Dict, Any

from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from core.models import User, Role, UserRole
from core.common.users.user_services import UserService
from .verify_service import VerificationService
from .token_service import TokenService

# ====== Logger Configuration ====== #
logger = logging.getLogger('accounts.services.auth')


# ======= Authentication Service ======= #
class AuthService:
    """
    کلاس سرویس احراز هویت برای مدیریت ثبت‌نام و ورود کاربران.
    این سرویس منطق کامل ثبت‌نام، اختصاص نقش و ورود کاربر را کپسوله می‌کند.
    """
    def __init__(self, user_service: UserService, verify_service: VerificationService):
        """تعیین سرویس‌های وابسته"""
        self._user_service = user_service
        self._verify_service = verify_service
        logger.debug("AuthService initialized")
        
    @transaction.atomic
    def register_user(self, validated_data: Dict[str, Any]) -> User:
        """
        سرویس برای ثبت‌نام مشتری جدید با فیلدهای چک شده.
        
        منطق کامل:
        1- ایجاد کاربر توسط سرویس UserService
        2- بررسی وجود نقش Customer و در صورت وجود، اختصاص به مشتری
        3- پس از ساخت، به لطف سیگنال‌های ایجاد شده، یک سبد خرید، کیف پول
        و پروفایل برای کاربر ساخته خواهد شد.
        4- ارسال کد تأیید به ایمیل کاربر
        
        Args:
            validated_data: دیکشنری حاوی اطلاعات معتبر کاربر
            
        Returns:
            User: شیء کاربر ایجاد شده
            
        Raises:
            ValidationError: در صورت بروز خطا در فرآیند ثبت‌نام
        """
        username = validated_data.get('username', 'N/A')
        email = validated_data.get('email', 'N/A')
        
        logger.info(f"Starting user registration - Username: {username}, Email: {email}")
        
        try:
            # ===== ایجاد کاربر ===== #
            user = self._user_service.create_user(validated_data)
            logger.info(f"User created successfully - User ID: {user.id}, Username: {user.username}")
            
            # ===== بررسی وجود نقش مشتری (Customer) ===== #
            try:
                customer_role, created = Role.objects.get_or_create(name="مشتری")
                
                if created:
                    logger.info("Customer role created for the first time")
                else:
                    logger.debug(f"Customer role retrieved - Role ID: {customer_role.id}")
                
                user_role = UserRole.objects.create(user=user, role=customer_role)
                logger.info(
                    f"Customer role assigned to user - "
                    f"User ID: {user.id}, Role: {customer_role.name}, UserRole ID: {user_role.id}"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to assign customer role to user {user.id}: {str(e)}",
                    exc_info=True
                )
                raise ValidationError(f"خطا در اختصاص نقش مشتری: {str(e)}")
            
            # ===== ارسال کد تأیید ===== #
            logger.info(f"Sending verification code to email: {user.email}")
            self._verify_service.send_verification_code(user.email)
            logger.info(f"Verification code sent successfully to {user.email}")
            
            logger.info(
                f"User registration completed successfully - "
                f"User ID: {user.id}, Username: {user.username}"
            )
            
            return user
            
        except ValidationError:
            # خطاهای ValidationError را مستقیماً پرتاب می‌کنیم
            raise
            
        except Exception as e:
            logger.error(
                f"Unexpected error during user registration - Username: {username}, Error: {str(e)}",
                exc_info=True
            )
            raise ValidationError(f"خطای غیرمنتظره در ثبت‌نام: {str(e)}")

    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        ورود کاربر با استفاده از نام کاربری و رمز عبور.
        
        Args:
            username: نام کاربری
            password: رمز عبور
            
        Returns:
            Dict حاوی اطلاعات کاربر و توکن‌های احراز هویت
            
        Raises:
            ValidationError: در صورت عدم تطابق اطلاعات کاربری
        """
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
            tokens = TokenService.create_token_for_user(user)
            
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
