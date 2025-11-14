from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from core.models import User, Role, UserRole
from core.common.users.user_services import UserService

from ..tasks import send_password_reset_email_task

# ======= Password Reset Service ======= #
class PasswordResetService:
    """
    سرویس بازنشانی رمز عبور
    """
    
    def __init__(self, user_service: UserService):
        self._user_service = user_service
        self._token_generator = PasswordResetTokenGenerator()
    
    def send_reset_link(self, email:str):
        """
        ارسال لینک بازنشانی رمز عبور به ایمیل
        """
        user = self._user_service.get_by_email(email)
        
        # ===== ارسال ایمیل به سمت کاربر ===== #
        if user:
            token = self._token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # ===== ایجاد لینک ===== #
            reset_link = f"http://127.0.0.1:9010/reset/password/confirm/{uid}/{token}/"
            
            # ===== ارسال ایمیل به سمت کاربر ===== #
            send_password_reset_email_task(user_email=email, reset_link=reset_link)
            
    def confirm_password_reset(self, uidb64: str, token: str, new_password: str) -> User:
        """
        تایید توکن و لینک
        پس از اینکه لینک مورد نظر تایید شد(به واسطه توکن و ID) کاربر
        باید رمز عبور جدید خود را وارد کند و پس از آن، رمز عبور جدید
        ایجاد شده و کاربر می تواند با آن وارد حساب کاربری خود شود.
        """
        
        # ===== بررسی شناسه کاربر ===== #
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self._user_service.get_by_id(uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # ===== بررسی توکن ===== #
        if user is None or not self._token_generator.check_token(user, token):
            raise ValidationError("لینک بازنشانی نامعتبر یا منقضی شده است.")
        
        return self._user_service.set_password(user, new_password)
            