import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Union

from core.models import (
    Product,
    ProductQuantity,
    ProductSize,
    ProductMaterial,
    ProductOption
)

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.price_calculator')


# ====== Product Price Calculator ====== #
class ProductPriceCalculator:
    """
    سرویسی برای محاسبه قیمت نهایی یک محصول بر اساس ویژگی‌های انتخابی.
    این کلاس تمام منطق قیمت‌گذاری را کپسوله می‌کند.
    """
    def __init__(
        self,
        product: Product,
        quantity: ProductQuantity,
        material: ProductMaterial,
        options: List[ProductOption],
        size: Optional[ProductSize] = None,
        custom_dimensions: Optional[Dict[str, Union[int, float]]] = None
    ):
        self.product = product
        self.quantity = quantity
        self.material = material
        self.options = options
        self.size = size
        self.custom_dimensions = custom_dimensions

        logger.info(
            f"ProductPriceCalculator initialized - Product: {product.slug}, "
            f"Quantity: {quantity.min_quantity}-{quantity.max_quantity}, "
            f"Material: {material.name}, "
            f"Options count: {len(options)}, "
            f"Size: {size.name if size else 'Custom' if custom_dimensions else 'None'}"
        )

        if size and custom_dimensions:
            logger.error(
                f"Validation error - Both size and custom_dimensions provided for product: {product.slug}"
            )
            raise ValueError("نمی‌تواند یک محصول با سایز پیش‌فرض و ابعاد دلخواه همزمان داشته باشد.")
        
        if product.price_per_square_unit and not (size or custom_dimensions):
            logger.warning(
                f"Product {product.slug} has price_per_square_unit={product.price_per_square_unit} "
                f"but no size or custom_dimensions provided"
            )

    def _get_size_impact(self) -> Decimal:
        """محاسبه تأثیر قیمت بر اساس سایز استاندارد یا ابعاد دلخواه."""
        if self.size:
            logger.debug(
                f"Using standard size - Name: {self.size.name}, "
                f"Price impact: {self.size.price_impact}"
            )
            return self.size.price_impact
        
        if self.custom_dimensions and self.product.price_per_square_unit:
            width = Decimal(str(self.custom_dimensions.get('width', 0)))
            height = Decimal(str(self.custom_dimensions.get('height', 0)))
            area = width * height
            impact = area * self.product.price_per_square_unit
            
            logger.debug(
                f"Custom dimensions calculation - Width: {width}, Height: {height}, "
                f"Area: {area}, Price per unit: {self.product.price_per_square_unit}, "
                f"Total impact: {impact}"
            )
            return impact
        
        logger.debug("No size impact - returning 0.0")
        return Decimal('0.0')

    def calculate(self) -> Dict[str, Union[float, str]]:
        """
        الگوریتم اصلی محاسبه قیمت نهایی.
        یک دیکشنری با جزئیات کامل قیمت‌گذاری برمی‌گرداند.
        """
        logger.info(f"Starting price calculation for product: {self.product.slug}")
        
        # ===== استخراج قیمت پایه از تیراژ ===== #
        base_price = Decimal(str(self.quantity.price))
        logger.debug(f"Base price from quantity: {base_price}")
        
        # ===== جمع‌آوری قیمت‌ها ===== #
        impacts = []
        
        material_impact = Decimal(str(self.material.price_impact))
        impacts.append(material_impact)
        logger.debug(f"Material impact ({self.material.name}): {material_impact}")
        
        size_impact = self._get_size_impact()
        impacts.append(size_impact)
        logger.debug(f"Size impact: {size_impact}")
        
        for option in self.options:
            option_impact = Decimal(str(option.price_impact))
            impacts.append(option_impact)
            logger.debug(f"Option impact ({option.name}): {option_impact}")
        
        total_impacts = sum(impacts, Decimal('0.0'))
        logger.info(f"Total impacts calculated: {total_impacts}")

        # ===== محاسبه قیمت خام با قیمت ویژگی‌ها ===== #
        raw_price = base_price + total_impacts
        logger.debug(f"Raw price (base + impacts): {raw_price}")

        # ===== ضریب افزایش یا کاهش قیمت ===== #
        modifier_percent = Decimal(str(self.product.price_modifier_percent))
        modifier_factor = Decimal('1.0') + (modifier_percent / Decimal('100.0'))
        logger.debug(
            f"Price modifier - Percent: {modifier_percent}%, Factor: {modifier_factor}"
        )
        
        # ===== محاسبه قیمت نهایی ===== #
        final_price = raw_price * modifier_factor
        logger.info(
            f"Final price calculated: {final_price} "
            f"(raw: {raw_price} × modifier: {modifier_factor})"
        )

        # ===== گرد کردن و تبدیل به float برای JSON ===== #
        result = {
            "base_price": float(base_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "total_impacts": float(total_impacts.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "raw_price_before_modifier": float(raw_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            "modifier_percent": float(modifier_percent),
            "final_price": float(final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }
        
        logger.info(
            f"Price calculation completed for product {self.product.slug} - "
            f"Final price: {result['final_price']}"
        )
        logger.debug(f"Full calculation result: {result}")
        
        return result
