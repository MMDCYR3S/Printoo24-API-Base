from typing import List, Dict, Any
from django.core.exceptions import ValidationError
from django.db.models import QuerySet


from core.models import User, OrderItem 
from core.product.models import Product, ProductRating, ProductComment, ProductCommentChoices
from core.product.exceptions import OverRatingNumberException, NotBuyerException

# ========== FEEDBACK SERVICE ========== #
class FeedbackService:
    """
    سرویس دامنه مدیریت نظرات و امتیازات.
    شامل متدهای خواندن (Read) و نوشتن (Write).
    """

    # ===== Write Operations ===== #
    def add_rating(self, user: User, product: Product, score: int):
        """
        ثبت امتیاز با قوانین بیزنس.
        """
        if not (1 <= score <= 5):
            raise OverRatingNumberException("امتیاز باید بین ۱ تا ۵ باشد.")

        # قانون: هر کاربر یک امتیاز برای هر محصول
        existing_rating = ProductRating.objects.get_user_rating(user.id, product.id)
        if existing_rating:
            # آپدیت امتیاز قبلی
            existing_rating.score = score
            existing_rating.save()
            return existing_rating
        
        # ایجاد امتیاز جدید
        return ProductRating.objects.create_rating(user, product, score)

    def add_comment(self, user: User, product: Product, message: str):
        """
        ثبت نظر با قوانین:
        1. کاربر حتما باید محصول را خریده باشد.
        """
        # قانون: کاربر باید محصول را خریده باشد
        has_purchased = OrderItem.objects.filter(
            order__user_id=user.id, 
            product_id=product.id
        ).exists()

        if not has_purchased:
            raise NotBuyerException("برای ثبت نظر، ابتدا باید این محصول را خریداری کرده باشید.")

        return ProductComment.objects.create_comment({
            'user': user,
            'product': product,
            'message': message,
            'status': ProductCommentChoices.PENDING
        })

    # ===== Read Operations (Proxy to Manager) ===== #
    
    def get_product_average_score(self, product_id: int) -> float:
        """محاسبه میانگین امتیاز یک محصول"""
        return ProductRating.objects.get_product_average_score(product_id)

    def get_user_rating_for_product(self, user_id: int, product_id: int):
        """دریافت امتیاز کاربر به یک محصول خاص (اگر داده باشد)"""
        return ProductRating.objects.get_user_rating(user_id, product_id)

    def get_approved_comments(self, product_id: int) -> QuerySet:
        """دریافت نظرات تایید شده برای نمایش در صفحه محصول"""
        return ProductComment.objects.get_approved_comments(product_id)

    def get_user_comment_history(self, user_id: int) -> QuerySet:
        """دریافت تاریخچه نظرات کاربر برای پروفایل"""
        return ProductComment.objects.get_comments_by_user(user_id)
    
    def has_user_commented(self, user_id: int, product_id: int) -> bool:
        """بررسی اینکه آیا کاربر قبلاً نظر داده است"""
        return ProductComment.objects.has_user_commented(user_id, product_id)
