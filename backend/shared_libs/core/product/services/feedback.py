from django.core.exceptions import ValidationError

from core.models import OrderItem , User
from core.product.models import Product, ProductRating, ProductComment, ProductCommentChoices
from ..exceptions import OverRatingNumberException, NotBuyerException

# ========== FEEDBACK SERVICE ========== #
class FeedbackService:
    """
    سرویس مدیریت نظرات و امتیازات
    """

    def add_rating(self, user: User, product: Product, score: int):
        """
        ثبت امتیاز با قوانین بیزنس.
        """
        if not (1 <= score <= 5):
            raise OverRatingNumberException("امتیاز باید بین ۱ تا ۵ باشد.")

        # ===== قانون: کاربر باید محصول را خریده باشد ===== #
        existing_rating = ProductRating.objects.get_user_rating(user.id, product.id)
        if existing_rating:
            # آپدیت امتیاز قبلی
            existing_rating.score = score
            existing_rating.save()
            return existing_rating
        
        # ===== ایجاد امتیاز ===== #
        return ProductRating.objects.create_rating(user, product, score)

    def add_comment(self, user: User, product: Product, message: str):
        """
        ثبت نظر با قوانین:
        1. کاربر حتما باید محصول را خریده باشد.
        """
        # ===== قانون: کاربر باید محصول را خریده باشد ===== #
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

    def get_user_comment_history(self, user_id: int):
        """
        دریافت تاریخچه نظرات کاربر.
        """
        return ProductComment.objects.get_comments_by_user(user_id)
