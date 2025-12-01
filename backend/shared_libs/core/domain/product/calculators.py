import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Union

from core.models import (
    Product,
    ProductMaterial,
    ProductOption,
    ProductSize,
    PricingType
)

# ====== Logger Configuration ====== #
logger = logging.getLogger('shop.services.price_calculator')

class ProductPriceCalculator:
    """
    سرویس پیشرفته محاسبه قیمت چاپ بر اساس متریال، مساحت و خدمات.
    منطق: (مساحت کل × قیمت متریال) + (هزینه آپشن‌ها) + (هزینه ثابت) + (هزینه طراحی)
    """
    def __init__(
        self,
        product: Product,
        product_material: ProductMaterial, # جایگزین Material و QuantityObj قدیمی
        quantity: int,
        options: List[ProductOption],
        width: float, # عرض به سانتی‌متر
        height: float, # ارتفاع به سانتی‌متر
        has_design: bool = True # آیا کاربر فایل دارد؟
    ):
        self.product = product
        self.pm = product_material # آبجکت ProductMaterial (رابط محصول و جنس)
        self.quantity = Decimal(quantity)
        self.options = options
        self.width = Decimal(str(width))
        self.height = Decimal(str(height))
        self.has_design = has_design
        
        # دسترسی به کانفیگ قیمت‌گذاری (از رابطه OneToOne)
        self.config = getattr(product, 'pricing_config', None)

        # ===== لاگ اولیه ===== #
        logger.info(
            f"Init Calculator: Product={product.slug}, Qty={quantity}, "
            f"Mat={self.pm.material.name}, WxH={width}x{height}, Design={has_design}"
        )

    def _calculate_total_area_sqm(self) -> Decimal:
        """محاسبه مساحت کل سفارش به متر مربع"""
        # تبدیل سانتی‌متر به متر: (w/100) * (h/100)
        area_per_unit = (self.width / 100) * (self.height / 100)
        total_area = area_per_unit * self.quantity
        return total_area

    def calculate(self) -> Dict[str, float]:
        """اجرای الگوریتم محاسبه قیمت"""
        
        if self.quantity <= 0:
            return {"final_price": 0.0}

        # 1. محاسبه مساحت کل (متر مربع)
        total_area_sqm = self._calculate_total_area_sqm()
        logger.debug(f"Total Area (sqm): {total_area_sqm}")

        # 2. محاسبه هزینه کاغذ/متریال (Paper Cost)
        # قیمت نهایی متریال (شامل هزینه پردازش) از پراپرتی مدل ProductMaterial خوانده می‌شود
        material_unit_price = self.pm.final_material_price_per_sqm 
        
        material_cost = total_area_sqm * material_unit_price 
        
        # هزینه اضافه ثابت متریال (اگر باشد)
        material_cost += (self.pm.extra_price_per_unit * self.quantity)
        
        logger.debug(f"Material Cost: {material_cost}")

        # 3. محاسبه هزینه آپشن‌ها (Options Cost)
        options_cost = Decimal(0)
        for opt in self.options:
            impact = opt.price_impact
            
            if opt.pricing_type == PricingType.FIXED:
                # مبلغ ثابت روی کل سفارش (مثل هزینه ارسال خاص یا بسته‌بندی ویژه)
                options_cost += impact
                
            elif opt.pricing_type == PricingType.PER_UNIT:
                # مبلغ به ازای هر عدد (مثل شماره‌زنی)
                options_cost += (impact * self.quantity)
                
            elif opt.pricing_type == PricingType.PER_SQM:
                # مبلغ به ازای متر مربع (مثل سلفون، لمینت، یووی)
                options_cost += (impact * total_area_sqm)
                
            elif opt.pricing_type == PricingType.PERCENTAGE:
                # درصدی از هزینه متریال (بیمه یا مالیات خاص)
                options_cost += (material_cost * (impact / 100))

        logger.debug(f"Options Cost: {options_cost}")

        # 4. هزینه‌های سربار و طراحی (Config Costs)
        setup_cost = Decimal(0)
        design_cost = Decimal(0)
        
        if self.config:
            # هزینه ثابت اولیه (زینک، کلیشه)
            setup_cost = self.config.base_setup_price
            
            # هزینه طراحی (اگر کاربر فایل نداشته باشد و سرویس فعال باشد)
            if self.config.design_service_available and not self.has_design:
                design_cost = self.config.design_fee

        # 5. جمع نهایی
        raw_price = material_cost + options_cost + setup_cost + design_cost
        
        # گرد کردن نهایی (مثلاً به 100 تومان)
        final_price = raw_price.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        result = {
            "material_cost": float(material_cost),
            "options_cost": float(options_cost),
            "setup_cost": float(setup_cost),
            "design_cost": float(design_cost),
            "final_price": float(final_price),
            "area_sqm": float(total_area_sqm) # برای نمایش به کاربر مفید است
        }
        
        logger.info(f"Calculation Done: {result['final_price']}")
        return result
