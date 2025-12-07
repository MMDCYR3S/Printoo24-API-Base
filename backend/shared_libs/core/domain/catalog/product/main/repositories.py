from typing import List, Optional
from django.db.models import Prefetch, QuerySet

from core.utils.base_repository import BaseRepository
from ..exceptions import ProductNotFoundException
from core.models import (
    Product, 
    ProductQuantity, 
    ProductSize, 
    ProductMaterial, 
    ProductOption,
    ProductOptionValue,
    ProductImage,
    ProductAttachment,
    ProductFileUploadRequirement,
)

# ====== Product Repository ====== #
class ProductRepository(BaseRepository[Product]):
    """
    ریپازیتوری مربوط به قوانین و کوئری‌های مدل Product.
    این لایه مسئولیت تمام تعاملات با دیتابیس برای محصولات را بر عهده دارد.
    """
    
    def __init__(self):
        super().__init__(Product)
       
    # ===== Helper Methods ===== #
    def _get_detail_queryset(self) -> QuerySet[Product]:
        """
        یک کوئری‌ست پایه و سنگین که تمام روابط مورد نیاز برای صفحه جزئیات محصول
        را بارگذاری می‌کند (Eager Loading).
        این متد برای جلوگیری از تکرار کد در get_by_id و get_by_slug ساخته شده است.
        """
        return self.model.objects.select_related(
            'category',
            'pricing_config'
        ).prefetch_related(
            # ===== بارگذاری مقادیر ثابت ===== #
            Prefetch('product_quantity', queryset=ProductQuantity.objects.select_related('quantity').order_by('quantity__value')),
            Prefetch('product_size', queryset=ProductSize.objects.select_related('size').order_by('size__width')),
            Prefetch('product_material', queryset=ProductMaterial.objects.select_related('material').order_by('is_default', 'material__name')),
            
            # ===== بارگذاری ویژگی ها ===== #
            Prefetch(
                'options', 
                queryset=ProductOption.objects.select_related('option').prefetch_related(
                    Prefetch(
                        'choices', 
                        queryset=ProductOptionValue.objects.order_by('order')
                    )
                ).order_by('order')
            ),
            
            #  ===== بارگذاری تصاویر و فایل های پیوست ===== #
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
            Prefetch('product_attachment_product', queryset=ProductAttachment.objects.order_by('id')),
            
            # ===== نیازمندی‌های آپلود فایل ===== #
            Prefetch(
                'file_upload_requirements', 
                queryset=ProductFileUploadRequirement.objects.select_related('spec').order_by('sort_order')
            )
        )
        
    # ===== Read Methods ===== #
    def get_all_products(self) -> QuerySet[Product]:
        """
        دریافت لیست تمام محصولات به همراه دسته‌بندی آن‌ها.
        از select_related برای بهینه‌سازی کوئری مربوط به ForeignKey استفاده می‌شود.
        """
        return self.model.objects.filter(is_active=True).select_related('category')

    def get_products_by_category_ids(self, category_ids: list) -> QuerySet[Product]:
        """
        دریافت محصولات فعال متعلق به لیستی از دسته‌بندی‌ها.
        فقط فیلدهای ضروری برای نمایش در لیست (کارت محصول) را انتخاب می‌کند.
        """
        return self.model.objects.filter(
            category_id__in=category_ids, 
            is_active=True
        ).select_related('category').prefetch_related('product_image').order_by('-created_at')

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        try:
            return self._get_detail_queryset().get(slug=slug, is_active=True)
        except self.model.DoesNotExist:
            return None
    def get_product_detail_by_id(self, id: int) -> Optional[Product]:
        """
        دریافت جزئیات کامل یک محصول با استفاده از اسلاگ.
        این متد به شدت برای جلوگیری از مشکل N+1 بهینه‌سازی شده است.
        - select_related: برای روابط یک-به-یک یا یک-به-چند (ForeignKey).
        - prefetch_related: برای روابط چند-به-چند یا معکوس یک-به-چند (Reverse ForeignKey).
        """
        try:
            return self.model.objects.select_related(
                'category',
                'pricing_config'
            ).prefetch_related(
                Prefetch('product_quantity', queryset=ProductQuantity.objects.select_related('quantity').order_by('quantity__value')),
                Prefetch('product_size', queryset=ProductSize.objects.select_related('size').order_by('size__width')),
                Prefetch('product_material', queryset=ProductMaterial.objects.select_related('material').order_by('is_default', 'material__name')),
                
                Prefetch(
                    'options', 
                    queryset=ProductOption.objects.select_related('option').prefetch_related(
                        Prefetch(
                            'choices', 
                            queryset=ProductOptionValue.objects.order_by('order')
                        )
                    ).order_by('order')
                ),
                
                Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
                Prefetch('product_attachment_product', queryset=ProductAttachment.objects.order_by('id')),
                
                Prefetch(
                    'file_upload_requirements', 
                    queryset=ProductFileUploadRequirement.objects.select_related('spec').order_by('sort_order')
                )

            ).get(pk=id, is_active=True)
            
        except self.model.DoesNotExist:
            raise ProductNotFoundException(f"محصولی با اسلاگ '{id}' یافت نشد.")

    # =====  (Write Methods) ===== #
    def create_product(self, data: dict) -> Product:
        """ ایجاد بدنه اصلی محصول (Shell) """
        return self.model.objects.create(**data)

    def update_product(self, instance: Product, data: dict) -> Product:
        """ آپدیت اطلاعات پایه """
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def get_by_id(self, pk: int) -> Optional[Product]:
        """ دریافت محصول برای ویرایش (بدون کوئری‌های سنگین) """
        return self.model.objects.filter(pk=pk).first()

    # ===== (Relations) ===== #
    
    def clear_materials(self, product: Product):
        """ حذف تمام متریال‌های محصول (برای عملیات Sync) """
        product.product_material.all().delete()

    def clear_quantities(self, product: Product):
        """ حذف تمام تیراژهای محصول """
        product.product_quantity.all().delete()
        
    def bulk_update_option_values(self, values: list[ProductOptionValue], fields: list[str]):
        """
        بروزرسانی گروهی مقادیر آپشن (برای پرفورمنس بالا).
        """
        ProductOptionValue.objects.bulk_update(values, fields)

    def get_product_option_values(self, product_option_id: int):
        """ دریافت تمام مقادیر یک آپشن خاص محصول """
        return ProductOptionValue.objects.filter(product_option_id=product_option_id)
    
    def clear_file_requirements(self, product: Product):
        """ حذف تمام نیازمندی‌های فایل فعلی """
        product.file_upload_requirements.all().delete()
