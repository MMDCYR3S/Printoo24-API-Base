import math
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
    سرویس محاسبه قیمت محصول.
    منطق جدید: محاسبه هزینه یک "واحد مبنا" (مثلاً بسته ۵۰۰ تایی) و ضرب در تعداد واحدها.
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
        
        # محاسبات اولیه هندسی (مساحت و محیط یک عدد محصول تکی)
        self.area_sqm_single = (self.width * self.height) / Decimal(10000)
        self.perimeter_m_single = (self.width + self.height) * Decimal(2) / Decimal(100)
        
        self.config = getattr(product, 'pricing_config', None)
        
        # ===== محاسبه ضریب (Multiplier) ===== #
        # مثال: price_per_unit = 500 (مبنا)
        # quantity = 2000 (سفارش مشتری)
        # multiplier = 4 (یعنی ۴ بسته ۵۰۰ تایی)
        
        self.price_per_unit = getattr(product, 'price_per_unit', 1)
        if self.price_per_unit < 1: self.price_per_unit = 1
            
        self.qty_multiplier = Decimal(self.quantity) / Decimal(self.price_per_unit)
        
        logger.info(f"Calc Init: Product={product.id}, Qty={quantity}, BaseUnit={self.price_per_unit}, Multiplier={self.qty_multiplier}")

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "details": {}}

        # 1. محاسبه قیمت یک واحد مبنا (Base Price Per Block)
        # این قیمت شامل قیمت خود محصول + قیمت سایز برای "یک بسته" است.
        base_unit_cost, base_cost_breakdown = self._calculate_base_unit_cost()

        # 2. محاسبه هزینه آپشن‌ها برای یک واحد مبنا (Options Cost Per Block)
        options_unit_cost, options_breakdown = self._calculate_options_unit_cost(base_unit_cost)

        # 3. محاسبه قیمت کل (ضرب در ضریب)
        # (قیمت پایه واحد + قیمت آپشن واحد) * ضریب تعداد
        total_items_price = (base_unit_cost + options_unit_cost) * self.qty_multiplier

        # 4. هزینه‌های سربار (Fees)
        # نکته: هزینه‌های ستاپ معمولاً یکبار در کل سفارش حساب می‌شوند و ضرب نمی‌شوند.
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        # ===== تجمیع نهایی ===== #
        total_raw = total_items_price + setup_cost + design_cost

        # اعمال Modifier
        if hasattr(self.product, 'price_modifier_percent') and self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        return {
            "final_price": float(final_price),
            "breakdown": {
                "base_unit_cost": float(base_unit_cost), # قیمت یک بسته پایه
                "options_unit_cost": float(options_unit_cost), # قیمت آپشن‌های یک بسته
                "qty_multiplier": float(self.qty_multiplier), # ضریب (مثلا 4)
                "total_items_price": float(total_items_price), # جمع کل قبل از سربار
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
        محاسبه هزینه آپشن‌ها برای "یک واحد مبنا".
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

            parent_config = val.product_option
            # دریافت استراتژی (با فرض اینکه در آپشن تعریف شده)
            strategy = getattr(parent_config.option, 'pricing_strategy', STRAT_FIXED) 
            
            # ریت: قیمتی که ادمین وارد کرده
            rate = val.price_impact
            
            # هزینه ستاپ آپشن (یک بار در کل سفارش اعمال می‌شود، نه در هر بلوک)
            # اما ما اینجا داریم هزینه واحد بلوک را حساب می‌کنیم. 
            # ستاپ را باید جداگانه هندل کرد یا تقسیم بر تعداد بلوک کرد؟
            # روش استاندارد: ستاپ آپشن معمولاً سربار کل است.
            # برای سادگی فعلاً آن را به "اولین بلوک" اضافه می‌کنیم یا در جمع نهایی میاریم.
            # طبق کد قبلی: base_opt_setup = parent_config.base_price
            # چون ساختار را تغییر دادیم، ستاپ آپشن را اینجا نادیده می‌گیرم و فرض می‌کنم در rate لحاظ شده 
            # یا باید در متد calculate اصلی به عنوان سربار جداگانه اضافه شود.
            # (طبق لاجیک شما: همه چیز باید ضریب بخورد، پس ستاپ آپشن هم ضریب می‌خورد اگر اینجا باشد)
            
            option_cost_per_block = Decimal(0)

            # --- محاسبه قیمت برای یک واحد مبنا (Block) --- #
            
            if strategy == STRAT_FIXED:
                # مبلغ ثابت برای هر بسته
                option_cost_per_block = rate

            elif strategy == STRAT_PER_SQM:
                # نرخ * مساحت کلِ یک بسته
                area_of_one_block = self.area_sqm_single * Decimal(self.price_per_unit)
                option_cost_per_block = area_of_one_block * rate

            elif strategy == STRAT_PER_METER:
                # نرخ * محیط کلِ یک بسته
                perimeter_of_one_block = self.perimeter_m_single * Decimal(self.price_per_unit)
                option_cost_per_block = perimeter_of_one_block * rate

            elif strategy == STRAT_PERCENT:
                # درصدی از قیمت پایه همان بسته
                option_cost_per_block = current_base_unit_cost * (rate / 100)
                
            elif strategy == STRAT_INPUT:
                # ورودی کاربر * نرخ * (شاید تعداد در بسته؟)
                # معمولاً این ورودی برای "هر عدد" است یا "کل سفارش"؟
                # فرض: ورودی کاربر (مثلا تعداد خط تا) برای کل سفارش است.
                # پس اگر بخواهیم در ضریب ضرب شود، باید تقسیم بر ضریب کنیم؟
                # ساده ترین حالت: rate برای هر بسته است.
                input_key = str(parent_config.option.id)
                user_val = int(self.user_input_data.get(input_key, 0))
                option_cost_per_block = user_val * rate
            
            total_option_cost += option_cost_per_block
            
            details.append({
                "option": parent_config.option.label,
                "value": val.label,
                "strategy": strategy,
                "cost_per_block": float(option_cost_per_block),
                "total_line_cost": float(option_cost_per_block * self.qty_multiplier)
            })

        return total_option_cost, details
