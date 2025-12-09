import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Union, Optional

from core.models import (
    Product,
    ProductOptionValue,
    ProductQuantity,
    ProductSize,
    OptionPricingStrategy
)

logger = logging.getLogger('shop.services.pricing')

class ProductPriceCalculator:
    """
    موتور محاسبه قیمت بر اساس مدل‌های اختصاصی (Quantity, Size, Options).
    
    اولویت محاسبه:
    1. قیمت پایه بر اساس تیراژ (ProductQuantity یا فرمول پایه).
    2. هزینه سایز (استاندارد یا دلخواه).
    3. هزینه آپشن‌ها.
    4. هزینه‌های سربار (طراحی، ستاپ).
    """

    def __init__(
        self,
        product: Product,
        quantity: int,
        width: float = 0,
        height: float = 0,
        selected_values: List[ProductOptionValue] = None,
        user_input_data: Dict[str, str] = None,
        selected_size_id: Optional[int] = None, # شناسه سایز استاندارد انتخاب شده
        has_design: bool = True
    ):
        self.product = product
        self.quantity = int(quantity)
        
        # تبدیل ابعاد به Decimal
        self.width = Decimal(str(width or 0))
        self.height = Decimal(str(height or 0))
        
        self.selected_values = selected_values or []
        self.user_input_data = user_input_data or {}
        self.selected_size_id = selected_size_id
        self.has_design = has_design
        
        # محاسبات هندسی
        self.area_sqm = (self.width * self.height) / Decimal(10000) # cm to m2
        self.perimeter_m = (self.width + self.height) * Decimal(2) / Decimal(100)
        
        self.config = getattr(product, 'pricing_config', None)

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        if self.quantity <= 0:
            return {"final_price": 0.0, "details": {}}

        # 1. محاسبه قیمت پایه (Base Price Logic)
        # منطق: آیا این تیراژ در جدول ProductQuantity تعریف شده؟
        base_total_cost = self._calculate_base_quantity_cost()

        # 2. محاسبه هزینه سایز (Size Logic)
        # منطق: سایز استاندارد (ProductSize) یا سایز دلخواه (Custom)?
        size_total_cost = self._calculate_size_cost()

        # 3. محاسبه هزینه آپشن‌ها (Options Logic)
        options_total_cost, options_breakdown = self._calculate_options_cost()

        # 4. هزینه‌های سربار (Fees)
        setup_cost = self.config.base_setup_price if self.config else Decimal(0)
        design_cost = Decimal(0)
        if self.config and self.config.design_service_available and not self.has_design:
            design_cost = self.config.design_fee

        # ===== تجمیع نهایی ===== #
        total_raw = base_total_cost + size_total_cost + options_total_cost + setup_cost + design_cost

        # اعمال Modifier (درصد تعدیل قیمت روی کل سفارش)
        if self.product.price_modifier_percent != 0:
            modifier = (total_raw * self.product.price_modifier_percent) / 100
            total_raw += modifier

        # رند کردن
        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        return {
            "final_price": float(final_price),
            "breakdown": {
                "base_quantity_price": float(base_total_cost),
                "size_cost": float(size_total_cost),
                "options_total": float(options_total_cost),
                "setup_fee": float(setup_cost),
                "design_fee": float(design_cost),
                "options_details": options_breakdown
            }
        }

    def _calculate_base_quantity_cost(self) -> Decimal:
        """
        محاسبه قیمت پایه بر اساس جدول ProductQuantity.
        اگر تیراژ دقیق پیدا شد، قیمت پکیج را برمی‌گرداند.
        اگر پیدا نشد (و مجاز بود)، قیمت پایه محصول را ضرب در تعداد می‌کند.
        """
        # تلاش برای پیدا کردن قیمت دقیق این تیراژ در جدول واسط
        # نکته: مدل ProductQuantity فیلد price دارد که معمولاً قیمت کلِ آن پکیج است
        try:
            pq = ProductQuantity.objects.filter(
                product=self.product,
                quantity__value=self.quantity
            ).first()
            
            if pq:
                # اگر قیمت در جدول ProductQuantity صفر بود، یعنی قیمت خاصی ندارد و باید محاسبه شود؟
                # فرض می‌کنیم اگر عدد داشت، همان قیمت کل است.
                if pq.price > 0:
                    return Decimal(pq.price)
        except Exception:
            pass

        # فال‌بک: اگر تیراژ در جدول نبود (مثلاً تیراژ دلخواه)، از قیمت پایه محصول استفاده کن
        # Product.price = قیمت واحد
        return self.product.price * self.quantity

    def _calculate_size_cost(self) -> Decimal:
        """
        محاسبه هزینه مربوط به سایز.
        دو حالت دارد:
        1. سایز استاندارد (از طریق ProductSize).
        2. سایز دلخواه (از طریق ابعاد و قیمت بر متر).
        """
        # حالت 1: سایز استاندارد انتخاب شده
        if self.selected_size_id:
            try:
                ps = ProductSize.objects.get(
                    product=self.product,
                    size_id=self.selected_size_id
                )
                # price_impact معمولاً قیمت اضافه به ازای هر واحد است
                return ps.price_impact * self.quantity
            except ProductSize.DoesNotExist:
                pass # اگر پیدا نشد، شاید کاستوم باشد

        # حالت 2: سایز دلخواه (Custom Dimension)
        if self.config and self.config.accepts_custom_dimensions:
            if self.product.price_per_square_unit and self.area_sqm > 0:
                # فرمول: مساحت کل × قیمت واحد سطح
                total_area = self.area_sqm * self.quantity
                return total_area * self.product.price_per_square_unit

        return Decimal(0)

    def _calculate_options_cost(self):
        """
        محاسبه هزینه آپشن‌ها.
        """
        total = Decimal(0)
        details = []

        for val in self.selected_values:
            if not val.has_pricing:
                continue

            parent_config = val.product_option
            strategy = parent_config.pricing_strategy
            rate = val.price_impact
            
            # هزینه ستاپ آپشن (اگر باشد)
            base_opt_price = parent_config.base_price
            
            variable_cost = Decimal(0)

            # --- استراتژی‌های محاسبه --- #
            if strategy == OptionPricingStrategy.FIXED:
                # مبلغ ثابت × (تعداد / گام)
                multiplier = self._get_step_multiplier(val)
                variable_cost = rate * multiplier

            elif strategy == OptionPricingStrategy.PER_SQM:
                # (مساحت کل) × نرخ
                # مناسب برای روکش، سلفون، یووی
                total_area = self.area_sqm * self.quantity
                variable_cost = total_area * rate

            elif strategy == OptionPricingStrategy.PER_METER_PERIMETER:
                # (محیط کل) × نرخ
                # مناسب برای دوردوزی
                total_perimeter = self.perimeter_m * self.quantity
                variable_cost = total_perimeter * rate

            elif strategy == OptionPricingStrategy.PERCENTAGE:
                # درصدی از قیمت پایه (تیراژ)
                base = self._calculate_base_quantity_cost()
                variable_cost = base * (rate / 100)

            elif strategy == OptionPricingStrategy.PER_UNIT_INPUT:
                # ورودی عددی کاربر
                input_key = str(parent_config.option.id)
                user_qty = int(self.user_input_data.get(input_key, 0))
                variable_cost = (user_qty * self.quantity) * rate

            line_cost = base_opt_price + variable_cost
            total += line_cost
            
            details.append({
                "option": parent_config.option.label,
                "value": val.label,
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
            return Decimal(math.ceil(qty / step))
        
        return qty / Decimal(step)
