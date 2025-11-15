import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict
from django.db.models import QuerySet

from core.common.product.product_services import ProductService
from core.models import Product, ProductOption

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.product_detail')


# ======= Shop Product Detail Service ======= #
class ShopProductDetailService:
    """
    سرویس لایه کاربردی برای مورد استفاده "نمایش جزئیات یک محصول"
    """
    def __init__(self, product_service: ProductService):
        self._product_service = product_service
        logger.debug("ShopProductDetailService initialized")
        
    def get_product_detail_for_display(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        مورد استفاده: دریافت و آماده‌سازی جزئیات یک محصول برای نمایش در صفحه جزئیات.
        """
        logger.info(f"Fetching product details for slug: {slug}")
        
        try:
            # ===== دریافت جزئیات یک مصحول از سرویس ===== #
            product = self._product_service.get_product_detail_by_slug(slug)
            
            if not product:
                logger.warning(f"Product not found with slug: {slug}")
                return None
            
            logger.debug(f"Product found - ID: {product.id}, Name: {product.name}")
                
            # ===== دریافت تمامی ویژگی های یک محصول منحصر به فرد به صورت بهینه ===== #
            quantities = list(product.product_quantity.all())
            sizes = list(product.product_size.all())
            materials = list(product.product_material.all())
            options = list(product.product_option_product.all())
            images = list(product.product_image.all())
            attachments = list(product.product_attachment_product.all())
            
            logger.debug(
                f"Product attributes loaded - "
                f"Quantities: {len(quantities)}, "
                f"Sizes: {len(sizes)}, "
                f"Materials: {len(materials)}, "
                f"Options: {len(options)}, "
                f"Images: {len(images)}, "
                f"Attachments: {len(attachments)}"
            )

            # ===== گروه بندی ویژگی های منحصر به فرد محصول ===== #
            grouped_options = self._group_options_by_type(options)
            
            logger.debug(f"Options grouped into {len(grouped_options)} categories")
            
            # ===== ایجاد دیکشنری ===== #
            product_details = {
                'product': product,
                'quantities': quantities,
                'sizes': sizes,
                'materials': materials,
                'options': grouped_options,
                'images': images,
                'attachments': attachments
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

    def _group_options_by_type(self, options: List[ProductOption]) -> Dict[str, List[ProductOption]]:
        """
        یک متد کمکی برای گروه‌بندی آپشن‌های محصول بر اساس نوع آن‌ها.
        این منطق متعلق به لایه نمایش است و به درستی در این سرویس قرار گرفته است.
        """
        logger.debug(f"Grouping {len(options)} options by type")
        
        grouped = defaultdict(list)
        for po in options:
            try:
                option_type_name = po.option_value.option.name
                grouped[option_type_name].append(po)
            except AttributeError as e:
                logger.warning(
                    f"Skipping option with missing data - ProductOption ID: {po.id}, Error: {str(e)}"
                )
                continue
        
        result = dict(grouped)
        
        logger.debug(
            f"Options grouped successfully - Categories: {list(result.keys())}, "
            f"Distribution: {[(k, len(v)) for k, v in result.items()]}"
        )
        
        return result
