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
