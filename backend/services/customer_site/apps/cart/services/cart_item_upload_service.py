import logging
from django.core.files.base import ContentFile
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

        # 1. اعتبارسنجی ورودی هویتی
        if not user and not session_key:
             raise ValidationError("شناسه کاربر یا نشست مهمان الزامی است.")

        # 2. یافتن ایمن آیتم (Security Check)
        query = Q(id=cart_item_id)
        if user and user.is_authenticated:
            query &= Q(cart__user=user)
        else:
            # برای مهمان: آیتم باید مال این سشن باشد و کاربری نداشته باشد
            query &= Q(cart__session_key=session_key, cart__user__isnull=True)

        try:
            cart_item = CartItem.objects.get(query)
        except CartItem.DoesNotExist:
            raise NotFound("آیتم مورد نظر در سبد خرید یافت نشد.")

        # 3. بررسی ابعاد و الزامات فنی (Validation Logic)
        # این قسمت از روی JSON ذخیره شده در آیتم خوانده می‌شود
        config = cart_item.items or {}
        meta = config.get('meta', {})
        
        # اگر سایز مشخص است، می‌توان اینجا چک کرد (اختیاری)
        # مثال: چک کردن نسبت ابعاد یا حجم فایل
        # فعلا فقط لاگ می‌کنیم چون اعتبارسنجی دقیق فایل معمولاً پیچیده است
        logger.debug(f"Processing upload for config: {meta}")

        # 4. پاکسازی فایل‌های قبلی (استراتژی تک‌فایلی)
        # اگر می‌خواهید چند فایل باشد، این خط را حذف کنید.
        # اما معمولاً برای هر ردیف آپلود (مثلاً طرح رو)، یک فایل نهایی داریم.
        # اگر سیستم شما چند فایلی است (مثلاً طرح رو و پشت)، باید requirement_id هم بگیرید.
        # فرض فعلی: هر آیتم سبد فعلاً یک فایل کلی می‌گیرد (یا لیست فایل‌ها Append می‌شود).
        
        # اگر می‌خواهید فایل‌های قبلی پاک شود (Replace Strategy):
        # CartItemUpload.objects.filter(cart_item=cart_item).delete()

        # 5. ذخیره فایل
        upload_instance = CartItemUpload.objects.create(
            cart_item=cart_item,
            file=file_obj
        )
        
        logger.info(f"File uploaded successfully: {upload_instance.id}")
        return upload_instance
    