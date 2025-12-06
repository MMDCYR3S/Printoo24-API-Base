from typing import List, Optional
from django.db.models import Max
from core.models import Product, ProductImage, Attachment, ProductAttachment
from core.utils.base_repository import BaseRepository

class ProductMediaRepository:
    """
    مدیریت داده‌های مربوط به تصاویر و فایل‌های پیوست محصول.
    """

    # ===== (Images) ===== #
    
    def add_image(self, product: Product, image_file, user) -> ProductImage:
        """ افزودن تصویر جدید به انتهای لیست """
        # ===== محاسبه ترتیب ===== 
        max_order = ProductImage.objects.filter(product=product).aggregate(Max('order'))['order__max']
        new_order = (max_order or 0) + 1
        
        return ProductImage.objects.create(
            product=product,
            user=user,
            image=image_file,
            order=new_order
        )

    def delete_image(self, image_id: int):
        ProductImage.objects.filter(id=image_id).delete()

    def get_images_by_ids(self, image_ids: List[int]) -> List[ProductImage]:
        return list(ProductImage.objects.filter(id__in=image_ids))

    def bulk_update_orders(self, images: List[ProductImage]):
        ProductImage.objects.bulk_update(images, ['order',])

    # ===== (Attachments Library) ===== #

    def create_attachment_in_library(self, file, name: str, user) -> Attachment:
        """ آپلود فایل در کتابخانه """
        return Attachment.objects.create(user=user, file=file, name=name)

    def delete_attachment_from_library(self, attachment_id: int):
        Attachment.objects.filter(id=attachment_id).delete()
        
    def get_attachment_by_id(self, attachment_id: int) -> Optional[Attachment]:
        return Attachment.objects.filter(id=attachment_id).first()

    # ===== (Linking) ===== #

    def link_attachment_to_product(self, product: Product, attachment: Attachment, user) -> ProductAttachment:
        return ProductAttachment.objects.create(
            product=product,
            attachment=attachment,
            user=user
        )

    def unlink_attachment(self, product: Product, attachment: Attachment):
        ProductAttachment.objects.filter(product=product, attachment=attachment).delete()

    def is_attached(self, product: Product, attachment: Attachment) -> bool:
        return ProductAttachment.objects.filter(product=product, attachment=attachment).exists()