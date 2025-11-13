from typing import List, Dict, Any
from .user_repo import UserRepository
from ...models import User

# ======== User Services ======== #
class UserService:
    """ سرویسی برای منطق کاربر """
    
    def __init__(self, repository: UserRepository):
        """ تعیین ریپازیتوری """
        self._repository = repository
        
    def create_user(self, data: Dict[str, Any]) -> User:
        """
        یک کاربر با استفاده فیلدهای مورد نیاز ایجاد میشود.
        منطق ایجاد کاربر در اینجا به صورت کامل ایجاد میشود و
        در باقی قسمت ها بدون تکرار باقی می ماند.
        """
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # ==== ایجاد کاربر ==== #
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
    
    def get_by_id(self, id: int) -> User | None:
        """
        دریافت کاربر توسط شناسه او
        """
        return self._repository.get_by_id(id)
    
    def get_by_email(self, email: str) -> User | None:
        """ 
        دریافت کاربر توسط ایمیل او
        """
        return self._repository.get_by_email(email)
    
    def set_user_as_verified(self, user: User) -> User:
        """
        کاربر را به صورت تایید شده تنظیم می کند
        """
        if not user.is_verified: 
            user.is_verified = True
            user.is_active = True
            self._repository.save(user)
        return user
    
    def set_password(self, user: User, new_password: str):
        """
        تغییر رمز عبور کاربر
        """
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return user
