from typing import Any, Optional
from django.core.cache import cache

# ======== Cache Service ======== #
class CacheService:
    """ 
    سرویس کش برای سیستم به صورت کلی
    از یک فرایند wrapper برای این کار استفاده می شود.
    """
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        یک مقدار برای ذخیره در کش و همچنین زمانبندی اختیاری، ایجاد میشود.
        در این بخش، ما سه نوع پارامتر می خواهیم:
        key: یک کلید کش برای ذخیره سازی
        value: مقداری که قرار است ذخیره شود.
        timeout: زمانبندی اتمام یک کش
        """
        cache.set(key, value, timeout)
        
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        دریافت یک مقدار کش
        key: کلید کش
        default: مقدار پیش فرض
        return: مقدار کش یا مقدار پیش فرض
        """
        return cache.get(key, default)
    
    def delete(self, key: str) -> None:
        """
        حذف یک مقدار کش
        key: کلید کش
        """
        cache.delete(key)
    