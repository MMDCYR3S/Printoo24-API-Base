from datetime import datetime
from typing import Optional, Dict, Any, List

from django.db.models import Prefetch, QuerySet, Q, Count

from core.utils.base_repository import BaseRepository
from ..exceptions import ProductNotFoundException
from core.models import (
    Product, 
    ProductQuantity, 
    ProductSize, 
    ProductOption,
    ProductOptionValue,
    ProductImage,
    ProductAttachment,
    ProductPricingConfig
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
        )
        
    # ===== Helper Methods (Internal) ===== #
    def _get_optimized_queryset(self) -> QuerySet[Product]:
        """
        کوئری‌ست پایه با بارگذاری روابط اصلی (بدون آپشن‌ها و فایل‌ها).
        """
        return self.model.objects.select_related(
            'category',
            'pricing_config'
        ).prefetch_related(
            # ===== بارگذاری تیراژ ===== #
            Prefetch(
                'product_quantity', 
                queryset=ProductQuantity.objects.select_related('quantity').order_by('quantity__value')
            ),
            # ===== تصویر محصول ===== #
            Prefetch('product_image', queryset=ProductImage.objects.order_by('order')),
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

            ).get(pk=id)
            
        except self.model.DoesNotExist:
            raise ProductNotFoundException(f"محصولی با شناسه '{id}' یافت نشد.")

    # =====  (Write Methods) ===== #
    def create_product(self, data: Dict[str, Any]) -> Product:
        """ایجاد بدنه اصلی محصول"""
        return self.model.objects.create(**data)

    def update_product(self, product: Product, data: Dict[str, Any]) -> Product:
        """آپدیت فیلدهای محصول"""
        for key, value in data.items():
            setattr(product, key, value)
        product.save()
        return product

    def get_by_id(self, pk: int) -> Optional[Product]:
        """ دریافت محصول برای ویرایش (بدون کوئری‌های سنگین) """
        return self.model.objects.filter(pk=pk).first()

    # ===== Pricing Config Management ===== #
    def update_or_create_pricing_config(self, product: Product, data: Dict[str, Any]) -> ProductPricingConfig:
        """ایجاد یا ویرایش تنظیمات قیمت"""
        config, created = ProductPricingConfig.objects.update_or_create(
            product=product,
            defaults=data
        )
        return config

    # ===== (Relations) ===== #
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
    
    # ===== Quantity Relations Management ===== #
    def sync_product_quantities(self, product: Product, user, quantity_ids: List[int]):
        """
        همگام‌سازی تیراژهای محصول.
        استراتژی: حذف قبلی‌ها و ایجاد جدیدها (Full Sync).
        """
        # 1. حذف همه روابط قبلی
        ProductQuantity.objects.filter(product=product).delete()
        
        # 2. ایجاد روابط جدید
        new_relations = [
            ProductQuantity(user=user, product=product, quantity_id=qid, price=0)
            for qid in quantity_ids
        ]
        if new_relations:
            ProductQuantity.objects.bulk_create(new_relations)
    
    # ========== Dashboard / Stats Methods ========== #
    def get_total_count(self) -> int:
        """تعداد کل محصولات"""
        return self.model.objects.count()

    def get_count_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """تعداد محصولات ایجاد شده در یک بازه زمانی خاص"""
        return self.model.objects.filter(created_at__range=(start_date, end_date)).count()

    def get_status_breakdown(self) -> dict:
        """
        تفکیک وضعیت (فعال/غیرفعال)
        خروجی: {'active': 10, 'inactive': 2}
        """
        return self.model.objects.aggregate(
            active=Count('id', filter=Q(is_active=True)),
            inactive=Count('id', filter=Q(is_active=False))
        )
    
    def get_quantity_status_breakdown(self) -> dict:
        """تعداد محصولات دارای تیراژ و بدون تیراژ"""
        return self.model.objects.aggregate(
            with_quantity=Count('id', filter=Q(has_quantity=True)),
            without_quantity=Count('id', filter=Q(has_quantity=False))
        )

