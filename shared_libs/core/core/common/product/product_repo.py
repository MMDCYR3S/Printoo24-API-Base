from typing import List, Optional
from django.db.models import Prefetch, QuerySet

from ..repositories import IRepository
from core.models import (
    Product, 
    ProductQuantity, 
    ProductSize, 
    ProductMaterial, 
    ProductOption,
    ProductImage,
    ProductAttachment
)

# ====== Product Repository ====== #
class ProductRepository(IRepository[Product]):
    """
    ریپازیتوری مربوط به قوانین و کوئری‌های مدل Product.
    این لایه مسئولیت تمام تعاملات با دیتابیس برای محصولات را بر عهده دارد.
    """
    
    def __init__(self):
        super().__init__(Product)
        
    def get_all_products(self) -> QuerySet[Product]:
        """
        دریافت لیست تمام محصولات به همراه دسته‌بندی آن‌ها.
        از select_related برای بهینه‌سازی کوئری مربوط به ForeignKey استفاده می‌شود.
        """
        return self.model.objects.filter(is_active=True).select_related('category')

    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        """
        دریافت جزئیات کامل یک محصول با استفاده از اسلاگ.
        این متد به شدت برای جلوگیری از مشکل N+1 بهینه‌سازی شده است.
        - select_related: برای روابط یک-به-یک یا یک-به-چند (ForeignKey).
        - prefetch_related: برای روابط چند-به-چند یا معکوس یک-به-چند (Reverse ForeignKey).
        """
        try:
            return self.model.objects.select_related(
                'category'
            ).prefetch_related(
                # ===== دریافت و مرتب سازی تیراژها ===== #
                Prefetch('product_quantity', queryset=ProductQuantity.objects.order_by('quantity')),
                
                # ===== دریافت و مرتب سازی سایزها ===== #
                Prefetch('product_size', queryset=ProductSize.objects.select_related('size').order_by('size__name')),
                
                # ===== دریافت و مرتب سازی حنس ها ===== #
                Prefetch('product_material', queryset=ProductMaterial.objects.select_related('material').order_by('material__name')),
                
                # ===== دریافت و مرتب سازی گزینه ها ===== #
                Prefetch(
                    'product_option_product', 
                    queryset=ProductOption.objects.select_related(
                        'option_value__option'
                    ).order_by('option_value__option__name', 'option_value__value')
                ),
                
                Prefetch(
                    'product_image',
                    queryset=ProductImage.objects.order_by('product', 'id')
                ),
                Prefetch(
                    'product_attachment_product',
                    queryset=ProductAttachment.objects.order_by('product', 'id')
                )
            ).get(slug=slug, is_active=True)
        except self.model.DoesNotExist:
            return None
