from ..repositories import IRepository
from ...models import User

# ====== User Repository ====== #
class UserRepository(IRepository[User]):
    """ ریپازیتوری مربوط به قوانین کاربران سیستم """
    
    def __init__(self):
        super().__init__(User)
        
    def get_by_username(self, username: str) -> User | None:
        """ دریافت کاربر با نام کاربری مشخص """
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None
        
    def get_by_email(self, email: str) -> User | None:
        """ دریافت کاربر با ایمیل مشخص """
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None
