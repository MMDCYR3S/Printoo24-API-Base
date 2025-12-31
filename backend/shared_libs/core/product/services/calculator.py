import logging
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
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
    موتور محاسبه قیمت محصول.
    
    Logic Change:
    - منطق تیراژ (Quantity) اکنون به price_per_unit وابسته است.
    - Multiplier تعداد "بسته‌های واحد" را مشخص می‌کند.
    - دسترسی به ویژگی‌ها (Options) ایمن‌سازی شده است.
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
        # متر مربع و محیط برای "یک واحد تکی" (Single Item)
        self.area_sqm_single = (self.width * self.height) / Decimal('10000')
        self.perimeter_m_single = (self.width + self.height) * Decimal('2') / Decimal('100')
        
        self.config = getattr(product, 'pricing_config', None)
        
        # ===== منطق واحد در بسته (Batch Logic) ===== #
        # اگر price_per_unit=1000 باشد و کاربر 2000 سفارش دهد، ضریب می‌شود 2.
        self.price_per_unit = getattr(product, 'price_per_unit', 1) or 1
        if self.price_per_unit < 1: 
            self.price_per_unit = 1
            
        # ضریب نهایی برای ضرب در قیمت پایه
        self.qty_multiplier = Decimal(self.quantity) / Decimal(self.price_per_unit)

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "breakdown": {}}

        # 1. محاسبه قیمت پایه (برای یک بلوک واحد)
        base_unit_cost, base_cost_breakdown = self._calculate_base_unit_cost()

        # 2. محاسبه هزینه آپشن‌ها (برای یک بلوک واحد)
        options_unit_cost, options_breakdown = self._calculate_options_unit_cost(base_unit_cost)

        # 3. محاسبه قیمت کل اقلام (تعداد بسته * قیمت هر بسته)
        # نکته: base_unit_cost و options_unit_cost قیمت "یک بسته" هستند.
        total_items_price = (base_unit_cost + options_unit_cost) * self.qty_multiplier

        # 4. هزینه‌های سربار (یکبار اعمال می‌شوند)
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        total_raw = total_items_price + setup_cost + design_cost

        # 5. اعمال مودیفایر درصدی (در صورت وجود)
        if hasattr(self.product, 'price_modifier_percent') and self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        # گرد کردن نهایی (مثلاً به نزدیک‌ترین 100 تومان)
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
        محاسبه قیمت "یک واحد مبنا" (Pricing Unit Block).
        واحد مبنا = تعداد price_per_unit از کالا.
        """
        breakdown = {}
        
        # الف) قیمت پایه محصول
        unit_price = self.product.price
        price_source = "Product Base Price"

        # ب) بررسی قیمت پلکانی (Tiered Pricing)
        # فرض: ProductQuantity فقط مشخص می‌کند که این تیراژ در دسترس است.
        # اما اگر قیمت داشته باشد، اولویت با آن است (طبق لاجیک Legacy).
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
        
        # ج) هزینه سایز
        size_cost_per_block = Decimal(0)
        
        # 1. سایز استاندارد
        if self.selected_size_id:
            try:
                ps = ProductSize.objects.get(
                    product=self.product,
                    size_id=self.selected_size_id
                )
                size_cost_per_block = ps.price_impact
                breakdown['size_type'] = "Standard"
            except ProductSize.DoesNotExist:
                pass

        # 2. سایز کاستوم (متری)
        elif self.config and self.config.accepts_custom_dimensions:
            price_per_sqm = getattr(self.product, 'price_per_square_unit', 0)
            if price_per_sqm and self.area_sqm_single > 0:
                # محاسبه مساحت کلِ "یک واحد مبنا"
                # مساحت یک عدد * تعداد در بسته (price_per_unit)
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                
                size_cost_per_block = area_of_one_block * price_per_sqm
                breakdown['size_type'] = "Custom Area"
        
        breakdown['size_cost_per_block'] = float(size_cost_per_block)
        
        # جمع نهایی برای یک بلوک
        total_unit_cost = unit_price + size_cost_per_block
        
        return total_unit_cost, breakdown

    def _calculate_options_unit_cost(self, current_base_unit_cost: Decimal):
        """
        محاسبه هزینه آپشن‌ها با ایمن‌سازی کامل در برابر Null بودن option.
        """
        total_option_cost = Decimal(0)
        details = []
        
        # ثابت‌های استراتژی
        STRAT_FIXED = OptionPricingStrategy.FIXED
        STRAT_PER_SQM = OptionPricingStrategy.PER_SQM
        STRAT_PER_METER = OptionPricingStrategy.PER_METER_PERIMETER
        STRAT_PERCENT = OptionPricingStrategy.PERCENTAGE
        STRAT_INPUT = OptionPricingStrategy.PER_UNIT_INPUT

        for val in self.selected_values:
            if not val.has_pricing:
                continue

            parent_config = val.product_option
            
            # ===== CRITICAL FIX: Safe Strategy Retrieval ===== #
            # اگر ویژگی کاستوم باشد، parent_config.option برابر None است.
            # در این صورت استراتژی پیش‌فرض FIXED در نظر گرفته می‌شود.
            strategy = STRAT_FIXED
            if parent_config.option:
                strategy = getattr(parent_config.option, 'pricing_strategy', STRAT_FIXED)
            
            rate = val.price_impact
            option_cost_per_block = Decimal(0)

            # ===== محاسبات بر اساس استراتژی ===== #
            if strategy == STRAT_FIXED:
                # هزینه ثابت به ازای هر "بسته واحد"
                option_cost_per_block = rate

            elif strategy == STRAT_PER_SQM:
                # مساحت کل بسته * نرخ
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                option_cost_per_block = area_of_one_block * rate

            elif strategy == STRAT_PER_METER:
                # محیط کل بسته * نرخ
                perimeter_of_one_block = self.perimeter_m_single * Decimal(self.price_per_unit)
                option_cost_per_block = perimeter_of_one_block * rate

            elif strategy == STRAT_PERCENT:
                # درصدی از قیمت پایه محاسبه شده تا الان
                option_cost_per_block = current_base_unit_cost * (rate / Decimal('100'))
                
            elif strategy == STRAT_INPUT:
                # ورودی کاربر (مثلاً تعداد لت اضافه)
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
                "cost": float(option_cost_per_block)
            })

        return total_option_cost, details
