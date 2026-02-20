import logging
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import List, Dict, Union, Optional, Tuple

from ..models import (
    Product,
    ProductOptionValue,
    ProductQuantity,
    ProductSize,
    OptionPricingStrategy,
    OptionValueQuantityPrice # <--- اضافه شد
)

logger = logging.getLogger('shop.services.pricing')

class ProductPriceCalculator:
    """
    موتور محاسبه قیمت محصول (Hybrid Engine).
    
    پشتیبانی همزمان از:
    ۱. محصولات تیراژی (Tiered Pricing با ماتریس قیمت)
    ۲. محصولات تعدادی (Unit-Based با ضریب تعداد)
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
        
        # ===== تبدیل ایمن ابعاد ===== #
        try:
            self.width = Decimal(str(width)) if width else Decimal('0')
            self.height = Decimal(str(height)) if height else Decimal('0')
        except (ValueError, InvalidOperation):
            self.width = Decimal('0')
            self.height = Decimal('0')
            
        self.selected_values = selected_values or []
        self.user_input_data = user_input_data or {}
        self.selected_size_id = selected_size_id
        self.has_design = has_design
        
        # ===== محاسبات هندسی ===== #
        self.area_sqm_single = (self.width * self.height) / Decimal('10000')
        self.perimeter_m_single = (self.width + self.height) * Decimal('2') / Decimal('100')
        
        self.config = getattr(product, 'pricing_config', None)
        
        # ===== گام ۱: پیدا کردن تیراژ در صورت وجود (Tiered Logic) ===== #
        self.matched_pq = None
        if self.product.has_quantity:
            self.matched_pq = ProductQuantity.objects.filter(
                product=self.product,
                quantity__value=self.quantity
            ).first()

        # ===== گام ۲: تعیین ضریب ضرب (Multiplier) ===== #
        # اگر محصول تیراژی باشد و تیراژ هم پیدا شود، تمام قیمت‌های ماتریس 
        # به صورت "مبلغ کل" (Total) برای آن تیراژ هستند، پس ضریب ۱ می‌شود.
        if self.matched_pq:
            self.qty_multiplier = Decimal('1')
            self.price_per_unit = 1 # در حالت تیراژی کاربرد ندارد
        else:
            # اگر محصول تعدادی باشد، قیمت‌ها باید ضرب‌در تعداد (یا گام شمارش) شوند
            self.price_per_unit = getattr(product, 'price_per_unit', 1) or 1
            if self.price_per_unit < 1: 
                self.price_per_unit = 1
            self.qty_multiplier = Decimal(self.quantity) / Decimal(self.price_per_unit)

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "breakdown": {}}

        # 1. محاسبه قیمت پایه (یا قیمت کل تیراژ یا قیمت یک واحد)
        base_unit_cost, base_cost_breakdown = self._calculate_base_unit_cost()

        # 2. محاسبه هزینه آپشن‌ها
        options_unit_cost, options_breakdown = self._calculate_options_unit_cost(base_unit_cost)

        # 3. محاسبه قیمت کل اقلام
        total_items_price = (base_unit_cost + options_unit_cost) * self.qty_multiplier

        # 4. هزینه‌های سربار (Setup & Design)
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        total_raw = total_items_price + setup_cost + design_cost

        # 5. اعمال مودیفایر درصدی (مثلا تخفیف یا مالیات سطح محصول)
        if hasattr(self.product, 'price_modifier_percent') and self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        # گرد کردن نهایی به 100 تومان
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
        breakdown = {}
        
        if self.matched_pq and self.matched_pq.price > 0:
            unit_price = self.matched_pq.price
            price_source = f"Tiered Price (Qty: {self.quantity})"
        else:
            unit_price = self.product.price
            price_source = "Unit Base Price"

        breakdown['unit_base'] = float(unit_price)
        breakdown['price_source'] = price_source

        size_cost_per_block = Decimal(0)
        
        if self.selected_size_id:
            try:
                ps = ProductSize.objects.get(product=self.product, size_id=self.selected_size_id)
                size_cost_per_block = ps.price_impact
                breakdown['size_type'] = "Standard"
            except ProductSize.DoesNotExist:
                pass
        elif self.config and self.config.accepts_custom_dimensions:
            price_per_sqm = getattr(self.product, 'price_per_square_unit', 0)
            if price_per_sqm and self.area_sqm_single > 0:
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                size_cost_per_block = area_of_one_block * price_per_sqm
                breakdown['size_type'] = "Custom Area"
        
        breakdown['size_cost_per_block'] = float(size_cost_per_block)
        
        total_unit_cost = unit_price + size_cost_per_block
        return total_unit_cost, breakdown

    def _calculate_options_unit_cost(self, current_base_unit_cost: Decimal):
        total_option_cost = Decimal(0)
        details = []

        matrix_overrides = {}
        if self.matched_pq and self.selected_values:
            overrides = OptionValueQuantityPrice.objects.filter(
                product_quantity=self.matched_pq,
                option_value__in=self.selected_values
            )
            matrix_overrides = {ov.option_value_id: ov.price for ov in overrides}

        STRAT_FIXED = OptionPricingStrategy.FIXED
        STRAT_PER_SQM = OptionPricingStrategy.PER_SQM
        STRAT_PER_METER = OptionPricingStrategy.PER_METER_PERIMETER
        STRAT_PERCENT = OptionPricingStrategy.PERCENTAGE
        STRAT_INPUT = OptionPricingStrategy.PER_UNIT_INPUT

        for val in self.selected_values:
            if not val or not getattr(val, 'has_pricing', False):
                continue

            parent_config = val.product_option
            
            # ===== تصمیم‌گیری: قیمت ماتریس (Override) یا قیمت پیش‌فرض ===== #
            is_matrix_override = False
            if val.id in matrix_overrides:
                rate = matrix_overrides[val.id]
                is_matrix_override = True
            else:
                rate = val.price_impact

            strategy = STRAT_FIXED
            if parent_config.option:
                strategy = getattr(parent_config.option, 'pricing_strategy', STRAT_FIXED)

            if is_matrix_override:
                strategy = STRAT_FIXED

            option_cost_per_block = Decimal(0)

            # ===== محاسبات بر اساس استراتژی ===== #
            if strategy == STRAT_FIXED:
                option_cost_per_block = rate

            elif strategy == STRAT_PER_SQM:
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                option_cost_per_block = area_of_one_block * rate

            elif strategy == STRAT_PER_METER:
                perimeter_of_one_block = self.perimeter_m_single * Decimal(self.price_per_unit)
                option_cost_per_block = perimeter_of_one_block * rate

            elif strategy == STRAT_PERCENT:
                option_cost_per_block = current_base_unit_cost * (rate / Decimal('100'))
                
            elif strategy == STRAT_INPUT:
                input_key = str(parent_config.id) 
                try:
                    user_val = Decimal(self.user_input_data.get(input_key, 0))
                except (ValueError, InvalidOperation):
                    user_val = Decimal(0)
                option_cost_per_block = user_val * rate
            
            total_option_cost += option_cost_per_block
            
            # ===== تعیین نام برای نمایش ===== #
            option_label = parent_config.label or parent_config.name
            if not option_label and parent_config.option:
                option_label = parent_config.option.label

            details.append({
                "option": option_label,
                "value": val.label,
                "cost": float(option_cost_per_block),
                "is_matrix_price": is_matrix_override
            })

        return total_option_cost, details
