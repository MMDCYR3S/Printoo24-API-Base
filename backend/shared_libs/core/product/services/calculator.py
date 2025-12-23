import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Union, Optional, Tuple

from ..models import (
    Product,
    ProductOptionValue,
    ProductQuantity,
    ProductSize,
    OptionPricingStrategy
)

logger = logging.getLogger('shop.services.pricing')

class ProductPriceCalculator:
    """
    سرویس محاسبه قیمت محصول (نسخه ایمن برای ویژگی‌های کاستوم).
    """

    def __init__(
        self,
        product: Product,
        quantity: int,
        width: float = 0,
        height: float = 0,
        selected_values: List[ProductOptionValue] = None,
        user_input_data: Dict[str, str] = None,
        selected_size_id: Optional[int] = None,
        has_design: bool = True
    ):
        self.product = product
        self.quantity = int(quantity)
        self.width = Decimal(str(width or 0))
        self.height = Decimal(str(height or 0))
        self.selected_values = selected_values or []
        self.user_input_data = user_input_data or {}
        self.selected_size_id = selected_size_id
        self.has_design = has_design
        
        # محاسبات هندسی
        self.area_sqm_single = (self.width * self.height) / Decimal(10000)
        self.perimeter_m_single = (self.width + self.height) * Decimal(2) / Decimal(100)
        
        self.config = getattr(product, 'pricing_config', None)
        
        # محاسبه ضریب
        self.price_per_unit = getattr(product, 'price_per_unit', 1)
        if self.price_per_unit < 1: self.price_per_unit = 1
            
        self.qty_multiplier = Decimal(self.quantity) / Decimal(self.price_per_unit)

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "breakdown": {}}

        # 1. محاسبه قیمت پایه واحد
        base_unit_cost, base_cost_breakdown = self._calculate_base_unit_cost()

        # 2. محاسبه هزینه آپشن‌ها (جایی که ارور می‌داد)
        options_unit_cost, options_breakdown = self._calculate_options_unit_cost(base_unit_cost)

        # 3. جمع کل
        total_items_price = (base_unit_cost + options_unit_cost) * self.qty_multiplier

        # 4. سربار
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        total_raw = total_items_price + setup_cost + design_cost

        # 5. مودیفایر
        if hasattr(self.product, 'price_modifier_percent') and self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        return {
            "final_price": float(final_price),
            "breakdown": {
                "base_unit_cost": float(base_unit_cost),
                "options_unit_cost": float(options_unit_cost),
                "qty_multiplier": float(self.qty_multiplier),
                "total_items_price": float(total_items_price),
                "setup_fee": float(setup_cost),
                "design_fee": float(design_cost),
                "options_details": options_breakdown,
                "base_details": base_cost_breakdown
            }
        }

    def _calculate_base_unit_cost(self) -> Tuple[Decimal, Dict]:
        """
        محاسبه قیمت "یک واحد مبنا" (مثلاً قیمت یک بسته ۵۰۰ تایی).
        """
        breakdown = {}
        
        # الف) قیمت پایه محصول (برای یک واحد مبنا)
        # فرض: عددی که در ادمین وارد شده (Product.price) قیمت یک واحد مبنا (مثلاً ۵۰۰ تایی) است.
        # فرض: اگر قیمت پلکانی (Quantity) باشد، آن هم قیمت یک واحد مبنا در آن پله است.
        
        unit_price = self.product.price
        price_source = "Product Base Price"

        try:
            pq = ProductQuantity.objects.filter(
                product=self.product,
                quantity__value=self.quantity
            ).first()
            
            if pq and pq.price > 0:
                unit_price = Decimal(pq.price)
                price_source = f"Tiered Price (Qty {self.quantity})"
        except ProductQuantity.DoesNotExist:
            pass
            
        breakdown['unit_base'] = float(unit_price)
        breakdown['price_source'] = price_source
        
        # ب) محاسبه هزینه سایز (برای یک واحد مبنا)
        size_cost_per_block = Decimal(0)
        size_cost_type = "None"
        
        # حالت ۱: سایز استاندارد
        if self.selected_size_id:
            try:
                ps = ProductSize.objects.get(
                    product=self.product,
                    size_id=self.selected_size_id
                )
                # price_impact: قیمتی که به ازای "یک واحد مبنا" اضافه می‌شود
                size_cost_per_block = ps.price_impact
                size_cost_type = "Standard Size Impact"
            except ProductSize.DoesNotExist:
                pass

        # حالت ۲: سایز دلخواه (متری)
        elif self.config and self.config.accepts_custom_dimensions:
            price_per_sqm = getattr(self.product, 'price_per_square_unit', 0)
            if price_per_sqm and self.area_sqm_single > 0:
                # محاسبه مساحت کلِ "یک واحد مبنا"
                # مساحت یک عدد * تعداد در بسته (price_per_unit)
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                
                # قیمت سایز برای این بسته = مساحت بسته * قیمت متر
                size_cost_per_block = area_of_one_block * price_per_sqm
                size_cost_type = "Area Price (Per Block)"
        
        breakdown['size_cost_per_block'] = float(size_cost_per_block)
        
        # جمع نهایی برای یک بلوک
        total_unit_cost = unit_price + size_cost_per_block
        
        return total_unit_cost, breakdown


    def _calculate_options_unit_cost(self, current_base_unit_cost: Decimal):
        """
        محاسبه هزینه آپشن‌ها (اصلاح شده برای جلوگیری از ارور NoneType)
        """
        total_option_cost = Decimal(0)
        details = []
        
        STRAT_FIXED = OptionPricingStrategy.FIXED
        STRAT_PER_SQM = OptionPricingStrategy.PER_SQM
        STRAT_PER_METER = OptionPricingStrategy.PER_METER_PERIMETER
        STRAT_PERCENT = OptionPricingStrategy.PERCENTAGE
        STRAT_INPUT = OptionPricingStrategy.PER_UNIT_INPUT

        for val in self.selected_values:
            if not val.has_pricing:
                continue

            # والد (ProductOption)
            parent_config = val.product_option
            
            # [FIXED] دریافت استراتژی به صورت ایمن
            # اگر به بانک وصل بود، استراتژی را از آنجا بگیر، وگرنه پیش‌فرض FIXED
            strategy = STRAT_FIXED
            if parent_config.option:
                strategy = getattr(parent_config.option, 'pricing_strategy', STRAT_FIXED)
            
            rate = val.price_impact
            option_cost_per_block = Decimal(0)

            # [LOGIC] محاسبه بر اساس استراتژی
            if strategy == STRAT_FIXED:
                option_cost_per_block = rate

            elif strategy == STRAT_PER_SQM:
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                option_cost_per_block = area_of_one_block * rate

            elif strategy == STRAT_PER_METER:
                perimeter_of_one_block = self.perimeter_m_single * Decimal(self.price_per_unit)
                option_cost_per_block = perimeter_of_one_block * rate

            elif strategy == STRAT_PERCENT:
                option_cost_per_block = current_base_unit_cost * (rate / 100)
                
            elif strategy == STRAT_INPUT:
                # [FIXED] کلید دیکشنری باید ID خود ProductOption باشد نه Option
                # چون برای کاستوم‌ها Option نداریم.
                input_key = str(parent_config.id) 
                user_val = float(self.user_input_data.get(input_key, 0))
                option_cost_per_block = Decimal(user_val) * rate
            
            total_option_cost += option_cost_per_block
            
            # [FIXED] دریافت نام ویژگی به صورت ایمن
            option_label = parent_config.label
            if not option_label and parent_config.option:
                option_label = parent_config.option.label
            if not option_label:
                option_label = parent_config.name # Fallback نهایی

            details.append({
                "option": option_label, # اینجا قبلاً ارور می‌داد
                "value": val.label,
                "cost": float(option_cost_per_block)
            })

        return total_option_cost, details
