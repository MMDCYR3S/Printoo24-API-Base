import logging

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from core.domain.identity.users.repositories import UserRepository

# ===== Logger ===== #
logger = logging.getLogger('apps.users.services.auth_app_service')

# ===== Auth App Service ===== #
class AuthAppService:
    def __init__(self):
        self.user_repo = UserRepository()

    def login_staff(self, username, password):
        """
        عملیات لاگین مخصوص پرسنل.
        بررسی می‌کند که کاربر is_staff باشد.
        """
        # ===== احراز هویت کاربر ===== #
        user = authenticate(username=username, password=password)
        
        if user is None:
            logger.warning(f"Login failed: Invalid credentials for user '{username}'")
            raise AuthenticationFailed("نام کاربری یا رمز عبور اشتباه است.")

        if not user.is_active:
            logger.warning(f"Login failed: Account disabled for user '{username}'")
            raise AuthenticationFailed("حساب کاربری غیرفعال است.")

        # ===== بررسی دسترسی کاربر ===== #
        if not user.is_staff:
            logger.warning(f"Login denied: Non-staff user '{username}' tried to access admin panel")
            raise PermissionDenied("شما مجوز ورود به پنل مدیریت را ندارید.")

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
            refresh.access_token['role'] = user_role_obj.role.code
            refresh.access_token['role_name'] = user_role_obj.role.name
        else:
            refresh.access_token['role'] = None

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user_role_obj.role.code if user_role_obj else None
            }
        }

    def logout(self, refresh_token):
        """
        خروج با Blacklist کردن رفرش توکن
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Logout successful (Token blacklisted)")
        except Exception as e:
            logger.warning(f"Logout failed: {str(e)}")
