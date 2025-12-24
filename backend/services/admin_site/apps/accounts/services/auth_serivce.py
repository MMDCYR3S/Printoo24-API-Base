import logging

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


from core.models import User
from core.logger.services import LoggerService

# ===== Logger ===== #
logger = logging.getLogger('apps.users.services.auth_app_service')

# ===== AUTH APP SERVICE ===== #
class AuthAppService:
    """
    سرویس اپلیکیشن مدیریت احراز هویت (Login, Logout, Token).
    """
    def __init__(self):
        self.audit_service = LoggerService()

    def login_staff(self, username, password, request_meta=None):
        """
        عملیات لاگین مخصوص پرسنل (Staff Login).
        1. احراز هویت (Username/Password)
        2. بررسی فعال بودن حساب
        3. بررسی دسترسی ادمین/پرسنل (Role Check)
        4. ثبت لاگ
        5. صدور توکن
        """
        # ===== احراز هویت کاربر ===== #
        user = authenticate(username=username, password=password)
        
        # ===== اگر کاربر وجود نداشت، ثبت در لاگ ===== #
        if user is None:
            self.audit_service.record_log(
                user=None, # کاربر ناشناس
                obj=None,
                action='LOGIN_FAILED',
                changes={'username_attempt': username, 'reason': 'Invalid credentials'},
                description=_("تلاش ناموفق برای ورود"),
                request_meta=request_meta
            )
            logger.warning(f"Login failed: Invalid credentials for user '{username}'")
            raise AuthenticationFailed("نام کاربری یا رمز عبور اشتباه است.")
        
        # ===== اگر کاربر فعال نبود، ثبت در لاگ ===== #
        if not user.is_active:
            self.audit_service.record_log(
                user=user,
                obj=user,
                action='LOGIN_BLOCKED',
                changes={'reason': 'Account disabled'},
                description=_("تلاش برای ورود با حساب غیرفعال"),
                request_meta=request_meta
            )
            logger.warning(f"Login failed: Account disabled for user '{username}'")
            raise AuthenticationFailed("حساب کاربری غیرفعال است.")
        
        # ===== بررسی دسترسی کاربر ===== #
        user_role_rel = user.user_role.select_related("role").first()
        has_access = user.is_superuser or user.is_staff or (user_role_rel and not user_role_rel.role.is_customer)
        if not has_access:
            self._log_failed_attempt(
                username, 
                f"No staff access. Role: {user_role_rel.role.slug if user_role_rel else 'None'}", 
                request_meta, 
                user,
                action='LOGIN_DENIED'
            )
            raise PermissionDenied(_("شما مجوز ورود به پنل مدیریت را ندارید."))

        # ===== لاگ موفقیت ===== #
        self.audit_service.record_log(
            user=user,
            obj=user,
            action='LOGIN',
            changes={'login_method': 'password'},
            description=_("ورود موفق پرسنل به سیستم"),
            request_meta=request_meta
        )

        # ===== تولید توکن با داده سفارشی ===== #
        logger.info(f"Staff login successful: User '{username}' (ID: {user.id})")
        return self._generate_tokens_with_claims(user)

    def _generate_tokens_with_claims(self, user):
        """
        تزریق Role, Email, Username به توکن JWT
        """
        refresh = RefreshToken.for_user(user)
        
        # ===== اگر نقش کاربر دریافت نشده است===== #
        if not user_role_rel:
            user_role_rel = user.user_role.select_related("role").first()
        # ===== ثبت اطلاعات در توکن ===== #
        refresh.access_token['username'] = user.username
        refresh.access_token['email'] = user.email
        
        role_slug = None
        role_name = None
        # ===== اگر کاربر مشتری است ===== #
        if user_role_rel:
            role_slug = user_role_rel.role.slug
            role_name = user_role_rel.role.name
        elif user.is_superuser:
            role_slug = 'superuser'
            role_name = 'مدیر کل'
            
        # ===== اطلاعات نقش کاربر ===== #
        refresh.access_token['role'] = role_slug
        refresh.access_token['role_name'] = role_name
        
        # ===== اطلاعات کاربر ===== #
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': self._get_full_name(user),
                'role': role_slug,
                'role_name': role_name
            }
        }
        
    def logout(self, refresh_token, user=None):
        """
        خروج با Blacklist کردن رفرش توکن
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            if user and user.is_authenticated:
                self.audit_service.record_log(
                    user=user,
                    obj=user,
                    action='LOGOUT',
                    description=_("خروج از سیستم")
                )
            logger.info("Logout successful (Token blacklisted)")
        except Exception as e:
            logger.warning(f"Logout failed: {str(e)}")

    # ===== Helpers ===== #
    def _log_failed_attempt(self, username, reason, request_meta, user=None, action='LOGIN_FAILED'):
        """ متد کمکی برای لاگ خطا """
        self.audit_service.record_log(
            user=user,
            obj=user,
            action=action,
            changes={'username_attempt': username, 'reason': reason},
            description=_("تلاش ناموفق برای ورود"),
            request_meta=request_meta
        )
        logger.warning(f"Login attempt failed: {reason} - User: {username}")

    def _get_full_name(self, user):
        """ تلاش برای دریافت نام کامل (اگر پروفایل مشتری دارد یا فیلد استاندارد) """
        if hasattr(user, 'customer_profile'):
            return user.customer_profile.fullname()
        return user.username
