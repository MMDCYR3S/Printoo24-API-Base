import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.domain.product import ProductDomainService
from core.models import ProductOption

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.product_detail')


# ======= Shop Product Detail Service ======= #
class ShopProductDetailService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش جزئیات یک محصول"
    """
    def __init__(self):
        self._product_service = ProductDomainService()
        logger.debug("ShopProductDetailService initialized")
        
    def get_product_detail_for_display(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        مورد استفاده: دریافت و آماده‌سازی جزئیات یک محصول برای نمایش در صفحه جزئیات.
        """
        logger.info(f"Fetching product details for slug: {slug}")
        
        try:
            # ===== دریافت جزئیات یک مصحول از سرویس ===== #
            data = self._product_service.get_product_detail_by_slug(slug)
            
            if not data:
                logger.warning(f"Product not found with slug: {slug}")
                return None
            
            logger.debug(f"Product found - ID: {data['product'].id}, Name: {data['product'].name}")
        
            # ===== دریافت ویژگی‌های یک محصول ===== #
            product = data['product']
            
            # ===== ایجاد دیکشنری ===== #
            product_details = {
                'product': product,
                'quantities': list(product.product_quantity.all()),
                'sizes': list(product.product_size.all()),
                'materials': list(product.product_material.all()),
                'options': data['grouped_options'],
                'images': list(product.product_image.all()),
                'attachments': list(product.product_attachment_product.all())
            }
            
            logger.info(
                f"Product details successfully prepared for slug: {slug} - "
                f"Product ID: {product.id}"
            )
            
            return product_details
            
        except Exception as e:
            logger.error(
                f"Error fetching product details for slug '{slug}': {str(e)}",
                exc_info=True
            )
            raise
