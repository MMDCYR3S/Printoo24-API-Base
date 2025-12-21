from django.db import models

# ===== Base QuerySet ===== #
class BaseQuerySet(models.QuerySet):
    """
    متدهای پایه برای شبیه‌سازی رفتار Repository
    """
    
    def get_by_id(self, id: int):
        """
        دریافت رکورد با ID.
        اگر پیدا نشد، None برمی‌گرداند (برای حفظ منطق سرویس‌های قبلی)
        """
        return self.filter(id=id).first()
