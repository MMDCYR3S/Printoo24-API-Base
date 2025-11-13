import random
from datetime import timedelta

from django.core.exceptions import ValidationError

from ...authentication.tasks import send_verification_email_task
from core.common.cache.cache_service import CacheService
from core.common.users.user_services import UserService

# ======= Verification Service ======= #
class VerificationService:
    """ 
    سرویس برای ارسال ایمیل به سمت کاربر برای احراز هویت و فعالسازی حساب کاربری
    """
    
    def __init__(self, user_service: UserService):
        self._user_service = user_service
    
    VERIFICATION_CODE_TIMEOUT_IN_SECONDS = timedelta(minutes=5).total_seconds()
    VERIFICATION_CODE_KEY_PREFIX = "verification_code"
    
    def _generate_code_number(self) -> str:
        """
        یک تابع برای ایجاد عدد تصادفی به صورت رشته برای فعالسازی
        """
        return str(random.randint(000000, 999999))
    
    def _get_cache_key(self, email: str) -> str:
        """
        یک تابع برای ایجاد کلید کش برای ذخیره کد فعال سازی
        کلید کش به صورت منحصربه فرد و با استفاده از ایمیل شخص
        ساخته می شود.
        """
        return f"{self.VERIFICATION_CODE_KEY_PREFIX}_{email}"
    
    def send_verification_code(self, email: str) -> None:
        """
        ارسال ایمیل فعالسازی حساب کاربری
        """
        
        # ===== ایجاد کد فعالسازی ===== # 
        code = self._generate_code_number()

        # ===== ذخیره کد فعالسازی ===== # 
        cache_key = self._get_cache_key(email)
        
        # ===== ایجاد کش با استفاده از سرویس ===== # 
        cache_service = CacheService()
        cache_service.set(cache_key, code, self.VERIFICATION_CODE_TIMEOUT_IN_SECONDS)
        
        #  ===== ارسال ایمیل ===== #
        send_verification_email_task.delay(email, code)
        
    def verify_code(self, email:str, code: str) -> bool:
        """
        اعتبارسنجی کد ارسال شده به کاربر.
        فرایند:
        1- اگرکه کاربر با ایمیل مورد نظر وجود دارد، به بررسی کد میرویم.
        در غیراینصورت، ارور میدهد که چنین ایمیلی وجود ندارد
        2- اگر کد ارسال شده با کد ذخیره شده برابر است، کاربر را تایید
        می کنیم و سپس، اکانت را فعال میکنیم.
        3- اگر کد ارسال شده منقضی شده است، به کاربر اطلاع میدهیم که دوباره
        کد جدید را ارسال نماید.
        """
        
        # ===== صحت سنجی کاربر ===== #
        user = self._user_service.get_by_email(email)
        if not user:
            raise ValidationError("این ایمیل موجود نمی باشد.")
        if user.is_verified:
            raise ValidationError("این حساب کاربری قبلا فعال شده است.")
        
        # ====== بررسی کش ===== #
        cache_service = CacheService()
        cache_key = self._get_cache_key(email)
        cache_code = cache_service.get(cache_key)
        if not cache_code or cache_code != str(code):
            raise ValidationError("کد ارسال شده صحیح نیست.")
        
        # ===== فعالسازی کاربر و حذف کش ===== #
        verified_user = self._user_service.set_user_as_verified(user)
        cache_service.delete(cache_key)
        
        return verified_user
        