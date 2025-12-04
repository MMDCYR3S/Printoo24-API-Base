from typing import List
from django.db import transaction
from django.core.exceptions import ValidationError
from .media_repo import ProductMediaRepository
from .repositories import ProductRepository

class ProductMediaDomainService:
    def __init__(self):
        self.media_repo = ProductMediaRepository()
        self.product_repo = ProductRepository()

    # ===== مدیریت تصاویر ===== #
    @transaction.atomic
    def upload_product_image(self, product_id: int, user, image_file):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValidationError("محصول یافت نشد.")
            
        return self.media_repo.add_image(product, image_file, user)

    @transaction.atomic
    def delete_product_image(self, product_id: int, image_id: int):
        self.media_repo.delete_image(image_id)

    @transaction.atomic
    def reorder_images(self, product_id: int, image_ids: List[int]):
        """
        تغییر ترتیب تصاویر بر اساس لیست ID های ارسال شده.
        مثال ورودی: [5, 2, 8] -> عکس ۵ اول شود، ۲ دوم و...
        """
        images = self.media_repo.get_images_by_ids(image_ids)
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
            self.media_repo.bulk_update_orders(to_update)

    # ===== مدیریت فایل‌های پیوست =====
    def upload_attachment_to_library(self, user, file, name: str):
        return self.media_repo.create_attachment_in_library(file, name, user)

    # ===== مدیریت فایل‌های پیوست ===== #
    @transaction.atomic
    def attach_file_to_product(self, product_id: int, attachment_id: int, user):
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValidationError("محصول یافت نشد.")

        attachment = self.media_repo.get_attachment_by_id(attachment_id)
        if not attachment:
            raise ValidationError("فایل پیوست یافت نشد.")

        # ===== بررسی اینکه فایل قبلا به محصول اضافه شده است ===== #
        if self.media_repo.is_attached(product, attachment):
            raise ValidationError("این فایل قبلاً به محصول اضافه شده است.")

        return self.media_repo.link_attachment_to_product(product, attachment, user)

    def detach_file_from_product(self, product_id: int, attachment_id: int):
        product = self.product_repo.get_by_id(product_id)
        attachment = self.media_repo.get_attachment_by_id(attachment_id)
        
        if product and attachment:
            self.media_repo.unlink_attachment(product, attachment)