from django.core.exceptions import ValidationError

from core.models import User, Product, ProductCommentChoices
from .repositories import RatingRepository, CommentRepository, PurchaseCheckRepository
from .exceptions import(
    OverRatingNumberException,
    NotBuyerException
)

class FeedbackDomainService:
    def __init__(self):
        self._rating_repo = RatingRepository()
        self._comment_repo = CommentRepository()
        self._purchase_repo = PurchaseCheckRepository()

    def add_rating(self, user: User, product: Product, score: int):
        """
        ثبت امتیاز با قوانین:
        1. امتیاز بین 1 تا 5 باشد.
        2. هر کاربر فقط یک بار امتیاز دهد (اگر هست، آپدیت کند).
        3. (اختیاری) کاربر باید محصول را خریده باشد؟ (معمولا برای امتیاز سخت‌گیر نیستند، اما برای کامنت چرا)
        """
        if not (1 <= score <= 5):
            raise OverRatingNumberException("امتیاز باید بین ۱ تا ۵ باشد.")

        # ===== قانون: کاربر باید محصول را خریده باشد ===== #
        existing_rating = self._rating_repo.get_user_rating(user.id, product.id)
        if existing_rating:
            return self._rating_repo.update(existing_rating, {'score': score})
        
        return self._rating_repo.create({
            'user': user,
            'product': product,
            'score': score
        })

    def add_comment(self, user: User, product: Product, message: str):
        """
        ثبت نظر با قوانین:
        1. کاربر حتما باید محصول را خریده باشد.
        2. کاربر قبلا نظر نداده باشد (اختیاری - شما گفتید فقط یکبار).
        """
        # ===== فقط یکبار امکان ثبت نظر داشته باشد ===== #
        # ===== قانون: کاربر باید محصول را خریده باشد ===== #
        if not self._purchase_repo.has_purchased_product(user.id, product.id):
            raise NotBuyerException("برای ثبت نظر، ابتدا باید این محصول را خریداری کرده باشید.")

        return self._comment_repo.create({
            'user': user,
            'product': product,
            'message': message,
            'status': ProductCommentChoices.PENDING
        })

    def get_user_comment_history(self, user_id: int):
        """
        [جدید] دریافت تاریخچه نظرات کاربر.
        این متد صرفاً دیتا را از ریپازیتوری می‌خواند.
        """
        return self.comment_repo.get_comments_by_user(user_id)
