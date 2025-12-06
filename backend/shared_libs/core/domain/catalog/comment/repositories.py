from django.db.models import Avg, Count
from core.models import ProductRating, ProductComment, OrderItem
from core.utils.base_repository import BaseRepository

class RatingRepository(BaseRepository[ProductRating]):
    """
    ریپازیتوری بخش مربوط به امتیازدهی
    """
    def __init__(self):
        super().__init__(ProductRating)

    def get_user_rating(self, user_id: int, product_id: int):
        return self.model.objects.filter(user_id=user_id, product_id=product_id).first()

    def get_product_average_score(self, product_id: int) -> float:
        """محاسبه میانگین امتیاز یک محصول"""
        result = self.model.objects.filter(product_id=product_id).aggregate(avg_score=Avg('score'))
        return result['avg_score'] or 0.0

class CommentRepository(BaseRepository[ProductComment]):
    """
    ریپازیتوری بخش کامنت
    """
    def __init__(self):
        super().__init__(ProductComment)

    def get_approved_comments(self, product_id: int):
        """دریافت نظرات تایید شده برای نمایش در سایت"""
        return self.model.objects.filter(
            product_id=product_id, 
            status=ProductComment.STATUS_APPROVED,
            parent__isnull=True  # فقط نظرات اصلی (پاسخ‌ها را در سریالایزر می‌گیریم)
        ).select_related('user__customer_profile').prefetch_related('replies')

    def has_user_commented(self, user_id: int, product_id: int) -> bool:
        return self.model.objects.filter(user_id=user_id, product_id=product_id).exists()
    
    def get_comments_by_user(self, user_id: int):
        """
        [جدید] دریافت تمام نظرات یک کاربر (چه تایید شده چه نشده).
        برای نمایش در پروفایل شخصی کاربر.
        """
        return self.model.objects.filter(user_id=user_id)\
            .select_related('product')\
            .order_by('-created_at')

class PurchaseCheckRepository:
    """
    ریپازیتوری کمکی برای چک کردن سابقه خرید.
    این را جدا کردیم چون مربوط به Order است اما برای Feedback استفاده می‌شود.
    """
    def has_purchased_product(self, user_id: int, product_id: int) -> bool:
        """
        بررسی وجود داشتن محصول برای کاربر جهت امتیاز دادن
        اگر کاربر محصول را خریداری نکرده باش، حق امتیازدهی
        ندارد و ابتدا باید محصول را خریداری کند.
        """
        return OrderItem.objects.filter(
            order__user_id=user_id, 
            product_id=product_id
        ).exists()
