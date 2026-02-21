import logging
from django.db.models import Q
from rest_framework.exceptions import ValidationError, NotFound

from core.models import User
from core.infrastructure.messages import msg_provider
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
             raise ValidationError(msg_provider.get("cart.E4022"))

        # ===== یافتن ایمن سبد خرید و آیتم ===== #
        query = Q(id=cart_item_id)
        if user and user.is_authenticated:
            query &= Q(cart__user=user)
        else:
            query &= Q(cart__session_key=session_key, cart__user__isnull=True)

        try:
            cart_item = CartItem.objects.get(query)
        except CartItem.DoesNotExist:
            raise NotFound(msg_provider.get("cart.E4023"))

        # ===== ایجاد عکس آیتم ===== #
        upload_instance = CartItemUpload.objects.create(
            cart_item=cart_item,
            file=file_obj
        )
        
        logger.info(f"File uploaded successfully: {upload_instance.id}")
        return upload_instance

    # ===== متد جدید برای حذف فایل ===== #
    def delete_file(
        self, 
        upload_id: int, 
        user: User = None, 
        session_key: str = None
    ):
        """
        حذف ایمن فایل آپلود شده با بررسی مالکیت سبد خرید و پاکسازی هارد دیسک.
        """
        logger.info(f"Attempting to delete upload {upload_id}")

        if not user and not session_key:
             raise ValidationError(msg_provider.get("cart.E4022"))

        # ===== کوئری ایمن برای بررسی مالکیت فایل ===== #
        query = Q(id=upload_id)
        if user and user.is_authenticated:
            query &= Q(cart_item__cart__user=user)
        else:
            query &= Q(cart_item__cart__session_key=session_key, cart_item__cart__user__isnull=True)

        try:
            upload_instance = CartItemUpload.objects.get(query)
        except CartItemUpload.DoesNotExist:
            raise NotFound(msg_provider.get("cart.E4024"))

        # ===== پاکسازی فیزیکی فایل از ===== #
        if upload_instance.file:
            upload_instance.file.delete(save=False) 

        # ===== حذف رکورد از دیتابیس ===== #
        upload_instance.delete()
        
        logger.info(f"File {upload_id} deleted successfully.")
