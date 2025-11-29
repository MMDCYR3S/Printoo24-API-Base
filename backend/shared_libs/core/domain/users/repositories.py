from typing import Any, Dict, Optional

from ...utils.base_repository import BaseRepository
from ...models import User
from .exceptions import (
    EmailAlreadyExistsException,
    EmailNotFoundException,
    UsernameNotFoundException
)

# ====== User Repository ====== #
class UserRepository(BaseRepository[User]):
    """ ریپازیتوری مربوط به قوانین کاربران سیستم """
    
    def __init__(self):
        super().__init__(User)
    
    # ===== دریافت براساس شناسه ===== #
    def get_by_id(self, id: int) -> Optional[User]:
        """ دریافت یک کاربر با شناسه """
        return self.model.objects.filter(id=id).first()
        
    # ===== دریافت براساس نام کاربری ===== #
    def get_by_username(self, username: str) -> Optional[User]:
        """ دریافت کاربر با نام کاربری مشخص """
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            raise UsernameNotFoundException(f"کاربری با نام کاربری '{username}' یافت نشد.")
    
    # ===== دریافت براساس ایمیل ===== #
    def get_by_email(self, email: str) -> Optional[User]:
        """ دریافت کاربر با ایمیل مشخص """
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            raise EmailNotFoundException(f"کاربری با ایمیل '{email}' یافت نشد.")
    
    # ===== ایجاد کاربر ===== #
    def create_user(self, data: Dict[str, Any]) -> User:
        """
        ایجاد یک کاربر جدید با داده های مشخص شده
        """
        return self.model.objects.create_user(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
            **{k: v for k, v in data.items() if k not in ['username', 'email', 'password']}
        )
    
    def save(self, user: User) -> User:
        """ ذخیره کاربر """
        user.save()
        return user
