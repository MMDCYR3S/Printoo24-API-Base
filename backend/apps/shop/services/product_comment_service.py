import logging
from typing import Dict, Any
from django.shortcuts import get_object_or_404

from core.models import User, Product
from core.product.services import FeedbackService

# تعریف لاگر اختصاصی با نام دقیق
logger = logging.getLogger('shop.services.feedback')

class FeedbackService:
    """
    سرویس مدیریت بازخوردها در سمت مشتری.
    مسئول ثبت نظرات و امتیازات و نمایش آن‌ها.
    """
    def __init__(self):
        self.domain_service = FeedbackService()

    def get_product_feedback_summary(self, product_id: int, user_id: int = None):
        """
        دریافت خلاصه فیدبک محصول (میانگین امتیاز + نظرات + امتیاز کاربر جاری).
        """
        avg_score = self.domain_service.get_product_average_score(product_id)
        comments = self.domain_service.get_approved_comments(product_id)
        
        user_rating = None
        if user_id:
            rating_obj = self.domain_service.get_user_rating_for_product(user_id, product_id)
            if rating_obj:
                user_rating = rating_obj.score

        return {
            "average_score": avg_score,
            "comments": comments,
            "user_rating": user_rating
        }

    def submit_review(self, user: User, product_slug: str, data: Dict[str, Any]):
        """
        ثبت همزمان امتیاز و نظر.
        """
        logger.info(f"Start submit_review for User ID: {user.id}, Product Slug: {product_slug}")
        
        try:
            product = get_object_or_404(Product, slug=product_slug)
        except Exception as e:
            logger.warning(f"Product not found for slug: {product_slug}")
            raise e

        results = {}

        # ===== 1. ثبت امتیاز (Rating) ===== #
        if 'score' in data:
            try:
                score = data['score']
                logger.debug(f"Attempting to add rating: {score} for Product ID: {product.id}")
                
                self.domain_service.add_rating(user, product, score)
                
                results['rating'] = "امتیاز شما با موفقیت ثبت شد."
                logger.info(f"Rating {score} added successfully for User ID: {user.id}")
                
            except Exception as e:
                logger.error(f"Failed to add rating for User ID: {user.id}. Error: {str(e)}")
                # بسته به بیزنس، می‌توانیم خطا را raise کنیم یا نادیده بگیریم و فقط نظر را ثبت کنیم
                raise e

        # ===== 2. ثبت نظر (Comment) ===== #
        if 'message' in data:
            try:
                message = data['message']
                logger.debug(f"Attempting to add comment for Product ID: {product.id}")
                
                self.domain_service.add_comment(user, product, message)
                
                results['comment'] = "نظر شما ثبت شد و پس از بررسی نمایش داده می‌شود."
                logger.info(f"Comment submitted successfully for User ID: {user.id}")
                
            except Exception as e:
                logger.error(f"Failed to add comment for User ID: {user.id}. Error: {str(e)}")
                raise e

        if not results:
            logger.warning(f"Empty review submission from User ID: {user.id} (No score or message)")

        return results

    def get_product_feedbacks(self, product_slug: str) -> Dict[str, Any]:
        """
        دریافت لیست نظرات و آمار امتیازات.
        """
        logger.info(f"Fetching feedbacks for Product Slug: {product_slug}")
        
        product = get_object_or_404(Product, slug=product_slug)
        
        # الف) لیست نظرات تایید شده
        comments = self._comment_read_repo.get_approved_comments(product.id)
        logger.debug(f"Retrieved {comments.count()} approved comments.")
        
        # ب) میانگین امتیاز
        avg_score = self._rating_read_repo.get_product_average_score(product.id)
        total_ratings = product.ratings.count()
        
        logger.debug(f"Product stats - Avg: {avg_score}, Total Ratings: {total_ratings}")
        
        return {
            "comments": comments,
            "average_rating": round(avg_score, 1),
            "total_ratings": total_ratings
        }
