from typing import Dict, Any

from .repositories import UserRepository
from ...models import User
from .exceptions import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException    
)

# ======== User Services ======== #
class UserDomainService:
    """ سرویسی برای منطق کاربر """
    
    def __init__(self):
        """ تعیین ریپازیتوری """
        self._repo = UserRepository()
    
    def check_uniqueness(self, username=None, email=None, exclude_user_id=None):
        """
        بررسی یکتایی کاربر
        :param username: نام کاربری
        :param email: ایمیل
        :param exclude_user_id: شناسه کاربری
        :return: bool
        """
        if username and self._repo.get_by_username(username):
            existing = self._repo.get_by_username(username)
            if existing.id != exclude_user_id:
                raise UsernameAlreadyExistsException("نام کاربری از قبل وجود دارد.")
            
        if email and self._repo.model.objects.filter(user__email=email).first():
            existing = self._repo.model.objects.filter(user__email=email).first()
            if existing.id != exclude_user_id:
                raise EmailAlreadyExistsException("ایمیل از قبل وجود دارد.")
    
    # ===== ثبت نام کاربر جدید ===== #
    def register_new_user(self, data: Dict[str, Any]) -> User:
        """
        یک کاربر با استفاده فیلدهای مورد نیاز ایجاد میشود.
        منطق ایجاد کاربر در اینجا به صورت کامل ایجاد میشود و
        در باقی قسمت ها بدون تکرار باقی می ماند.
        """
        
        # ===== بررسی وجود ایمیل و نام کاربری ===== #
        if self._repo.get_by_email(data.get("email")):
            raise EmailAlreadyExistsException(f"ایمیل '{data.get('email')}' قبلا ثبت شده است.")
        
        if self._repo.get_by_username(data['username']):
            raise UsernameAlreadyExistsException(f"نام کاربری '{data.get('username')}' قبلا ثبت شده است.")
        
        # ===== ایجاد کاربر ===== #
        return self._repo.create_user(data)
    
    # ===== دریافت کاربر توسط شناسه یا ایمیل ===== #
    def get_by_id(self, id: int) -> User | None:
        """
        دریافت کاربر توسط شناسه او
        """
        return self._repo.get_by_id(id)
    
    def get_by_email(self, email: str) -> User | None:
        """ 
        دریافت کاربر توسط ایمیل او
        """
        return self._repo.get_by_email(email)
    
    def verify_user(self, user: User) -> User:
        """تایید حساب کاربری"""
        if user.is_verified:
            return user
        user.is_verified = True
        user.is_active = True
        return self._repo.update(user, {"is_verified": True, "is_active": True})
    
    def set_password(self, user: User, new_password: str):
        """
        تغییر رمز عبور کاربر
        """
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return user
    
    def update(self, instance: User, data: Dict[str, Any]) -> User:
        """
        ویرایش اطلاعات عمومی.
        اینجا جایی است که باید مواظب باشیم کاربر فیلدهای حساس را عوض نکند.
        """
        forbidden = ['password', 'is_superuser', 'is_staff']
        clean_data = {k: v for k, v in data.items() if k not in forbidden}
        return self._repo.update(instance, clean_data)
