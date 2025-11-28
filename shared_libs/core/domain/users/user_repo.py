from typing import Any, Dict

from ...utils.base_repository import IRepository
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
    
    def update(self, instance: User, data: Dict[str, Any]) -> User:
        """ ویرایش کاربر """
        ALLOWED_FIELDS = ["email", "username"]
        # ===== فیلترینگ برای امنیت و عدم نفوذ کاربر ===== #
        filtered_data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        return super().update(instance, filtered_data)
    
    def save(self, user: User) -> User:
        """ ذخیره کاربر """
        user.save()
        return user
