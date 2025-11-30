import logging
from typing import List
from core.models import User, ProductComment
from core.domain.comment.services import FeedbackDomainService

# ===== Logger ===== #
logger = logging.getLogger('userprofile.services.feedback')

# ===== User Feedback Service ===== #
class UserFeedbackService:
    """
    سرویس مدیریت نظرات و بازخوردهای کاربر در پنل کاربری.
    """
    
    def __init__(self, user: User):
        self.user = user
        # ===== تزریق وابستگی‌ها ===== #
        self._domain_service = FeedbackDomainService()

    def get_my_comments(self) -> List[ProductComment]:
        """
        دریافت لیست تمام نظراتی که کاربر ثبت کرده است.
        """
        logger.info(f"Fetching comment history for User ID: {self.user.id}")
        
        try:
            comments = self._domain_service.get_user_comment_history(self.user.id)
            count = comments.count()
            
            logger.info(f"Retrieved {count} comments for User ID: {self.user.id}")
            return comments
            
        except Exception as e:
            logger.exception(f"Error fetching comments for User ID: {self.user.id}")
            raise e