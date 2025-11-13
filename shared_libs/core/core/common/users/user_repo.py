from ..repositories import IRepository
from ...models import User

# ====== User Repository ====== #
class UserRepository(IRepository[User]):
    """ ریپازیتوری مربوط به قوانین کاربران سیستم """
    
    def __init__(self):
        super().__init__(User)
        
    def get_by_id(self, id: int) -> User | None:
        """ دریافت یک کاربر با شناسه """
        return self.model.objects.filter(id=id).first()
        
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
        
    def save(self, user: User) -> User:
        """ ذخیره کاربر """
        user.save()
        return user
