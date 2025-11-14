from decimal import Decimal
from typing import List, Dict, Optional, Union

from core.models import (
    Product,
    ProductQuantity,
    ProductSize,
    ProductMaterial,
    ProductOption
)

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

        if size and custom_dimensions:
            raise ValueError("نمی تواند یک محصول با سایز  پیش فرض و ابعاد دلخواه همزمان داشته باشد.")
        
        if product.price_per_square_unit and not (size or custom_dimensions):
            pass

    def _get_size_impact(self) -> Decimal:
        """محاسبه تأثیر قیمت بر اساس سایز استاندارد یا ابعاد دلخواه."""
        if self.size:
            return self.size.price_impact
        
        if self.custom_dimensions and self.product.price_per_square_unit:
            width = Decimal(str(self.custom_dimensions.get('width', 0)))
            height = Decimal(str(self.custom_dimensions.get('height', 0)))
            area = width * height
            return area * self.product.price_per_square_unit
        
        return Decimal('0.0')

    def calculate(self) -> Dict[str, Union[Decimal, str]]:
        """
        الگوریتم اصلی محاسبه قیمت نهایی.
        یک دیکشنری با جزئیات کامل قیمت‌گذاری برمی‌گرداند.
        """
        # ===== استخراج قیمت پایه از تیراژ ===== #
        base_price = self.quantity.price
        
        # ===== جمع آوری قیمت ها ===== #
        impacts = []
        impacts.append(self.material.price_impact)
        impacts.append(self._get_size_impact())
        for option in self.options:
            impacts.append(option.price_impact)
        
        total_impacts = sum(impacts)

        # ===== محاسبه قیمت خام با قیمت ویژگی ها ===== #
        raw_price = base_price + total_impacts

        # ===== ضریب افزایش یا کاهش قیمت ===== #
        modifier_percent = self.product.price_modifier_percent
        modifier_factor = Decimal('1.0') + (modifier_percent / Decimal('100.0'))
        
        # ===== محاسبه قیمت نهایی ===== #
        final_price = raw_price * modifier_factor

        return {
            "base_price": base_price,
            "total_impacts": total_impacts,
            "raw_price_before_modifier": raw_price,
            "modifier_percent": modifier_percent,
            "final_price": final_price.quantize
        }
