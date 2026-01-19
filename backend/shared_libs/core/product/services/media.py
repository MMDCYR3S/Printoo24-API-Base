from typing import List
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Product, ProductImage, Attachment

# ========== MEDIA SERVICE ========== #
class ProductMediaService:
    """
    سرویس مدیریت رسانه‌های محصول (تصاویر و فایل‌ها)
    """

    # ===== مدیریت تصاویر ===== #
    @transaction.atomic
    def upload_product_image(self, product_id: int, user, image_file):
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ValidationError("محصول یافت نشد.")
            
        return ProductImage.objects.add_image(product, image_file, user)

    @transaction.atomic
    def delete_product_image(self, product_id: int, image_id: int):
        ProductImage.objects.delete_image(image_id)

    @transaction.atomic
    def reorder_images(self, product_id: int, image_ids: List[int]):
        """
        تغییر ترتیب تصاویر بر اساس لیست ID های ارسال شده.
        """
        # دریافت تصاویر به صورت QuerySet لیست شده
        images = list(ProductImage.objects.get_images_by_ids(image_ids))
        image_map = {img.id: img for img in images}
        
        to_update = []
        for index, img_id in enumerate(image_ids):
            if img_id in image_map:
                img = image_map[img_id]
                if int(img.product_id) != int(product_id):
                     raise ValidationError(f"تصویر {img_id} متعلق به این محصول نیست. - محصول: {img.product_id}")
                
                img.order = index + 1
                to_update.append(img)
        
        if to_update:
            ProductImage.objects.bulk_update_orders(to_update)

    # ===== مدیریت فایل‌های پیوست =====
    def upload_attachment_to_library(self, user, file, product_id: int, name: str = None):
        product = Product.objects.get_by_id(product_id)
        if not product:
            raise ValidationError("محصول یافت نشد.")
        return Attachment.objects.create_attachment(user=user, name=name, file=file, product=product)
