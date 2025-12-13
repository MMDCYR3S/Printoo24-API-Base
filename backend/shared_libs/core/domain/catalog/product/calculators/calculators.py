import math
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Union, Optional, Tuple

from core.models import (
    Product,
    ProductOptionValue,
    ProductQuantity,
    ProductSize,
    OptionPricingStrategy
)

logger = logging.getLogger('shop.services.pricing')

class ProductPriceCalculator:
    # ... (متد __init__ بدون تغییر می‌ماند) ...

    # ===== متد __init__ (بدون تغییر) ===== #
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
        
        self.area_sqm = (self.width * self.height) / Decimal(10000)
        self.perimeter_m = (self.width + self.height) * Decimal(2) / Decimal(100)
        self.config = getattr(product, 'pricing_config', None)
        logger.info(f"Calc Init: Product={product.id}, Qty={quantity}, Area={self.area_sqm}m2")
    # ==================================== #

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "details": {}}

        # 1. محاسبه قیمت پایه (Quantity + Size Base)
        # این قیمت شامل تیراژ و ابعاد اولیه است و مبنای محاسبه آپشن‌های درصدی قرار می‌گیرد.
        base_total_cost, base_cost_breakdown = self._calculate_base_price_and_size()

        # 2. محاسبه هزینه آپشن‌ها (Options Logic)
        options_total_cost, options_breakdown = self._calculate_options_cost(base_total_cost)

        # 3. هزینه‌های سربار (Fees)
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        # ===== تجمیع نهایی ===== #
        total_raw = base_total_cost + options_total_cost + setup_cost + design_cost

        # اعمال Modifier (درصد تعدیل قیمت روی کل سفارش)
        if self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        return {
            "final_price": float(final_price),
            "breakdown": {
                "base_price_initial": float(base_total_cost), # قیمت پایه ترکیب شده
                "options_total": float(options_total_cost),
                "setup_fee": float(setup_cost),
                "design_fee": float(design_cost),
                "options_details": options_breakdown,
                "base_details": base_cost_breakdown
            }
        }

    def _calculate_base_price_and_size(self) -> Tuple[Decimal, Dict]:
        """
        محاسبه قیمت پایه ترکیبی (تیراژ + سایز).
        این متد قیمت اولیه محصول را تعیین می‌کند.
        """
        breakdown = {}
        # 1. تلاش برای پیدا کردن قیمت تیراژ دقیق (پکیج قیمت)
        try:
            pq = ProductQuantity.objects.filter(
                product=self.product,
                quantity__value=self.quantity
            ).first()
            
            if pq and pq.price > 0:
                base_total_cost = Decimal(pq.price)
                base_cost_type = "Package Price"
            else:
                raise ProductQuantity.DoesNotExist # فال‌بک به قیمت واحد
        except ProductQuantity.DoesNotExist:
            base_total_cost = self.product.price
            base_cost_type = "Unit Price * Qty"
            
        breakdown['quantity_base'] = float(base_total_cost)
        
        # 2. محاسبه هزینه سایز (اضافی بر قیمت پایه)
        size_total_cost = Decimal(0)
        size_unit_cost = Decimal(0)
        size_cost_type = "None"
        
        # حالت 2.1: سایز استاندارد انتخاب شده
        if self.selected_size_id:
            try:
                ps = ProductSize.objects.get(
                    product=self.product,
                    size_id=self.selected_size_id
                )
                # price_impact قیمت اضافه به ازای هر واحد است
                size_unit_cost = ps.price_impact
                size_total_cost = size_unit_cost * self.quantity
                size_cost_type = "Standard Size Impact"
            except ProductSize.DoesNotExist:
                pass

        # حالت 2.2: سایز دلخواه (اگر پیکربندی مجاز باشد)
        elif self.config and self.config.accepts_custom_dimensions:
            if self.product.price_per_square_unit and self.area_sqm > 0:
                total_area = self.area_sqm * self.quantity
                size_unit_cost = self.product.price_per_square_unit
                size_total_cost = total_area * size_unit_cost
                size_cost_type = "Area Price"
        
        breakdown['size_cost'] = float(size_total_cost)
        breakdown['total_description'] = f"{base_cost_type} + {size_cost_type}"
        
        return base_total_cost + size_total_cost, breakdown


    def _calculate_options_cost(self, current_base_price: Decimal):
        """
        محاسبه هزینه آپشن‌ها.
        """
        total = Decimal(0)
        details = []
        
        # ... (تعریف ثابت‌ها) ...
        STRAT_FIXED = OptionPricingStrategy.FIXED
        STRAT_PER_SQM = OptionPricingStrategy.PER_SQM
        STRAT_PER_METER = OptionPricingStrategy.PER_METER_PERIMETER
        STRAT_PERCENT = OptionPricingStrategy.PERCENTAGE
        STRAT_INPUT = OptionPricingStrategy.PER_UNIT_INPUT

        for val in self.selected_values:
            if not val.has_pricing:
                continue

            parent_config = val.product_option
            strategy = parent_config.pricing_strategy
            rate = val.price_impact
            
            # هزینه ستاپ آپشن (یک بار در هر Order)
            base_opt_price = parent_config.base_price
            variable_cost = Decimal(0)

            # --- استراتژی‌های محاسبه --- #
            if strategy == STRAT_FIXED:
                multiplier = self._get_step_multiplier(val)
                variable_cost = rate * multiplier

            elif strategy == STRAT_PER_SQM:
                # مناسب برای روکش، سلفون، یووی (بر اساس مساحت کل)
                total_area = self.area_sqm * self.quantity
                variable_cost = total_area * rate

            elif strategy == STRAT_PER_METER:
                # (محیط کل) × نرخ
                total_perimeter = self.perimeter_m * self.quantity
                variable_cost = total_perimeter * rate

            elif strategy == STRAT_PERCENT:
                # 🚨 FIX: درصدی از قیمت پایه محاسبه شده (Quantity + Size)
                variable_cost = current_base_price * (rate / 100)
                
            # ... (بقیه استراتژی‌ها) ...
            elif strategy == STRAT_INPUT:
                input_key = str(parent_config.option.id)
                user_qty = int(self.user_input_data.get(input_key, 0))
                variable_cost = (user_qty * self.quantity) * rate
                
            else: # اگر استراتژی ناشناخته بود
                variable_cost = Decimal(0)

            line_cost = base_opt_price + variable_cost
            total += line_cost
            
            details.append({
                "option": parent_config.option.label,
                "value": val.label,
                "strategy": strategy,
                "cost": float(line_cost)
            })

        return total, details

    def _get_step_multiplier(self, val: ProductOptionValue) -> Decimal:
        """ منطق پله‌ای برای آپشن‌ها """
        step = val.quantity_step
        qty = Decimal(self.quantity)
        
        if step == 1:
            return qty
            
        if val.is_step_ceiling:
            import math
            print(Decimal(math.ceil(qty / step)))
            return Decimal(math.ceil(qty / step))
        
        return qty / Decimal(step)