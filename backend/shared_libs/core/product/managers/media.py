from typing import List
from django.db import models
from django.db.models import Max
from .base import BaseQuerySet

# ========== IMAGE QUERYSET ========== #
class ProductImageQuerySet(BaseQuerySet):
    """
    کوئری‌های مربوط به تصاویر محصول
    """
    def add_image(self, product, image_file, user):
        """ افزودن تصویر جدید به انتهای لیست """
        # ===== محاسبه ترتیب ===== 
        max_order = self.filter(product=product).aggregate(Max('order'))['order__max']
        new_order = (max_order or 0) + 1
        
        return self.create(
            product=product,
            user=user,
            image=image_file,
            order=new_order
        )

    def get_images_by_ids(self, image_ids: List[int]):
        return self.filter(id__in=image_ids)

# ========== IMAGE MANAGERS ========== #
class ProductImageManager(models.Manager):
    def get_queryset(self):
        return ProductImageQuerySet(self.model, using=self._db)

    def add_image(self, product, image_file, user):
        return self.get_queryset().add_image(product, image_file, user)

    def get_images_by_ids(self, image_ids: List[int]):
        return self.get_queryset().get_images_by_ids(image_ids)
    
    def bulk_update_orders(self, images: List):
        return self.bulk_update(images, ['order'])
    
    def delete_image(self, image_id: int):
        self.filter(id=image_id).delete()

# ========== ATTACHMENT QUERYSET ========== #
class AttachmentQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به فایل‌های پیوست"""
    pass

# ========== ATTACHMENT MANAGERS ========== #
class AttachmentManager(models.Manager):
    def get_queryset(self):
        return AttachmentQuerySet(self.model, using=self._db)

    def create_attachment(self, *, user, file, product, name: str):
        """ آپلود فایل در کتابخانه """
        return self.create(user=user, file=file, name=name, product=product)
    
    def get_by_id(self, attachment_id: int):
        return self.filter(id=attachment_id).first()
    
    def delete_attachment(self, attachment_id: int):
        self.filter(id=attachment_id).delete()