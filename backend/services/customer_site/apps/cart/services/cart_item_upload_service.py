import logging
from django.db.models import Q
from rest_framework.exceptions import ValidationError, NotFound

from core.models import User
from apps.cart.models import CartItem, CartItemUpload

logger = logging.getLogger('cart.services.item_upload')

class CartItemUploadService:
    """
    سرویس آپلود فایل برای آیتم سبد خرید (پشتیبانی از Guest و Auth).
    """

    def upload_file(
        self, 
        cart_item_id: int, 
        file_obj, 
        user: User = None, 
        session_key: str = None
    ) -> CartItemUpload:
        
        logger.info(f"Uploading file for Item {cart_item_id}")

        # ==== اعتبارسنجی ===== #
        if not user and not session_key:
             raise ValidationError("نشست کاربر معتبر نیست. لطفاً صفحه را رفرش کنید.")

        # ===== یافتن ایمن سبد خرید و آیتم ===== #
        query = Q(id=cart_item_id)
        if user and user.is_authenticated:
            query &= Q(cart__user=user)
        else:
            query &= Q(cart__session_key=session_key, cart__user__isnull=True)

        try:
            cart_item = CartItem.objects.get(query)
        except CartItem.DoesNotExist:
            raise NotFound("آیتم مورد نظر در سبد خرید یافت نشد (یا دسترسی ندارید).")

        # ===== ایجاد عکس آیتم ===== #
        upload_instance = CartItemUpload.objects.create(
            cart_item=cart_item,
            file=file_obj
        )
        
        logger.info(f"File uploaded successfully: {upload_instance.id}")
        return upload_instance
