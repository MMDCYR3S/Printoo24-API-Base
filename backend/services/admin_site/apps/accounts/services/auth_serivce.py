import logging

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from core.domain.identity.users.repositories import UserRepository
from core.domain.infrastructure.logger import AuditLogDomainService

# ===== Logger ===== #
logger = logging.getLogger('apps.users.services.auth_app_service')

# ===== Auth App Service ===== #
class AuthAppService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.audit_service = AuditLogDomainService()

    def login_staff(self, username, password, request_meta=None):
        """
        عملیات لاگین مخصوص پرسنل.
        بررسی می‌کند که کاربر is_staff باشد.
        """
        # ===== احراز هویت کاربر ===== #
        user = authenticate(username=username, password=password)
        
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
        if not user_role_rel or user_role_rel.role.is_customer == True:
            self.audit_service.record_log(
                user=user,
                obj=user,
                action='LOGIN_DENIED',
                changes={'reason': 'No admin access', 'role': str(user_role_rel.role.slug if user_role_rel else 'None')},
                description=_("تلاش کاربر عادی برای ورود به پنل ادمین"),
                request_meta=request_meta
            )
            logger.warning(f"Login denied: Non-staff user '{username}' tried to access admin panel")
            raise PermissionDenied("شما مجوز ورود به پنل مدیریت را ندارید.")

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
        
        # ===== Custom Payload Injection ===== #
        refresh.access_token['username'] = user.username
        refresh.access_token['email'] = user.email
        
        # ===== دریافت اطلاعات کاربر برای توکن ===== 
        user_role_obj = self.user_repo.get_user_role(user)
        if user_role_obj:
            refresh.access_token['role'] = user_role_obj.role.slug
            refresh.access_token['role_name'] = user_role_obj.role.name
        else:
            refresh.access_token['role'] = None

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user_role_obj.role.slug if user_role_obj else None
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
