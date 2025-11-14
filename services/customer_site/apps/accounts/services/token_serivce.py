from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from core.models import User

# ======= Token Service ======= #
class TokenService:
    """
    سرویس ایجاد توکن برای کاربر
    """
    
    @staticmethod
    def create_token_for_user(user: User) -> dict:
        """
        ایجاد توکن Access و Refresh برای کاربر
        """
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        
    @staticmethod
    def refresh_token_for_user(user: User) -> dict:
        """
        رفرش کردن توکن
        """
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        
    @staticmethod
    def send_to_blacklist(refresh_token: str):
        """
        انتقال توکن به لیست سیاه
        روند کار به این صورت هست که توکن کاربر را یکبار رفرش میکنیم.
        پس از انجام این کار، توکن به دست آمده رو وارد لیست سیاه میکنیم.
        """
        
        try:
            # ==== ایجاد یک شیء از روی توکن ==== 
            token = RefreshToken(refresh_token)
            # ==== انتقال توکن به لیست سیاه ==== #
            token.blacklist()
        except TokenError:
            pass
        