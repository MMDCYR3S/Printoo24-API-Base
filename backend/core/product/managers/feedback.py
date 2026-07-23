from django.db import models
from django.db.models import Avg

from .base import BaseQuerySet

# ========== RATING QUERYSET ========== #
class ProductRatingQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به امتیاز محصول
    """
    def get_user_rating(self, user_id: int, product_id: int):
        return self.filter(user_id=user_id, product_id=product_id).first()

    def get_product_average_score(self, product_id: int) -> float:
        """محاسبه میانگین امتیاز یک محصول"""
        result = self.filter(product_id=product_id).aggregate(avg_score=Avg('score'))
        return result['avg_score'] or 0.0

# ========== RATING MANAGERS ========== #
class ProductRatingManager(models.Manager):
    def get_queryset(self):
        return ProductRatingQuerySet(self.model, using=self._db)

    def get_user_rating(self, user_id: int, product_id: int):
        return self.get_queryset().get_user_rating(user_id, product_id)

    def get_product_average_score(self, product_id: int) -> float:
        return self.get_queryset().get_product_average_score(product_id)
    
    def create_rating(self, user, product, score):
        return self.create(user=user, product=product, score=score)


# ========== COMMENT QUERYSET ========== #
class ProductCommentQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به نظرات محصول
    """
    def get_approved_comments(self, product_id: int):
        """دریافت نظرات تایید شده برای نمایش در سایت"""
        from core.product.models import ProductCommentChoices
        
        return self.filter(
            product_id=product_id, 
            status=ProductCommentChoices.APPROVED if hasattr(ProductCommentChoices, 'APPROVED') else 'approved',
            parent__isnull=True
        ).select_related('user__customer_profile').prefetch_related('replies')

    def has_user_commented(self, user_id: int, product_id: int) -> bool:
        return self.filter(user_id=user_id, product_id=product_id).exists()
    
    def get_comments_by_user(self, user_id: int):
        """دریافت تمام نظرات یک کاربر برای پروفایل"""
        return self.filter(user_id=user_id)\
            .select_related('product')\
            .order_by('-created_at')

# ========== COMMENT MANAGERS ========== #
class ProductCommentManager(models.Manager):
    def get_queryset(self):
        return ProductCommentQuerySet(self.model, using=self._db)

    def get_approved_comments(self, product_id: int):
        return self.get_queryset().get_approved_comments(product_id)

    def has_user_commented(self, user_id: int, product_id: int) -> bool:
        return self.get_queryset().has_user_commented(user_id, product_id)

    def get_comments_by_user(self, user_id: int):
        return self.get_queryset().get_comments_by_user(user_id)
        
    def create_comment(self, data):
        return self.create(**data)
