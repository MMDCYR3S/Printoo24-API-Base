import math
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Union

from django.core.exceptions import ValidationError

# ایمپورت مدل‌های نهایی شده
from core.models import (
    Product,
    ProductMaterial,
    ProductOption,       # تنظیمات (استراتژی)
    ProductOptionValue,  # مقادیر انتخابی (نرخ و استپ)
    OptionPricingStrategy
)

logger = logging.getLogger('shop.services.pricing')

class ProductPriceCalculator:
    """
    موتور هسته محاسبه قیمت (Core Pricing Engine).
    
    این کلاس مسئول تبدیل "انتخاب‌های کاربر" و "ابعاد" به "مبلغ نهایی" است.
    از استراتژی‌های تعریف شده در دیتابیس (Per Sqm, Per Input, Step-based) پیروی می‌کند.
    """

    def __init__(
        self,
        product: Product,
        quantity: int,
        width: float,   # cm
        height: float,  # cm
        selected_values: List[ProductOptionValue], # لیست گزینه‌هایی که کاربر تیک زده
        product_material: Optional[ProductMaterial] = None,
        user_input_data: Dict[str, str] = None, # مقادیر متنی که کاربر تایپ کرده (برای آپشن‌های ورودی)
        has_design: bool = True
    ):
        self.product = product
        self.quantity = int(quantity)
        
        # تبدیل ابعاد به Decimal برای دقت محاسباتی
        self.width = Decimal(str(width))
        self.height = Decimal(str(height))
        
        self.selected_values = selected_values
        self.pm = product_material
        self.user_input_data = user_input_data or {}
        self.has_design = has_design
        
        # محاسبه متر مربع و متر محیط در لحظه شروع
        self.area_sqm = (self.width / 100) * (self.height / 100)
        self.perimeter_m = (self.width + self.height) * 2 / 100
        
        # دریافت کانفیگ قیمت‌گذاری محصول (اگر وجود داشته باشد)
        self.pricing_config = getattr(product, 'pricing_config', None)

        logger.info(f"Calc Init: Product={product.id}, Qty={quantity}, Area={self.area_sqm}m2")

    def calculate(self) -> Dict[str, Union[float, Dict]]:
        """
        متد اصلی اجرای محاسبه.
        خروجی شامل قیمت نهایی و ریز جزئیات برای فاکتور است.
        """
        if self.quantity <= 0:
            return {"final_price": 0.0, "details": {}}

        # 1. هزینه پایه محصول (Product Base Price)
        base_cost = self.product.price * self.quantity
        
        # 2. هزینه ستاپ اولیه (Setup Cost from Config)
        config_setup_cost = Decimal(0)
        config_design_cost = Decimal(0)
        
        if self.pricing_config:
            config_setup_cost = self.pricing_config.base_setup_price
            
            # هزینه طراحی (اگر فایل ندارد)
            if self.pricing_config.design_service_available and not self.has_design:
                config_design_cost = self.pricing_config.design_fee

        # 3. هزینه متریال (Material Cost)
        material_cost = self._calculate_material_cost()

        # 4. هزینه آپشن‌ها (Options Cost) - بخش پیچیده ماجرا
        options_cost, options_breakdown = self._calculate_options_total_cost()

        # ===== جمع نهایی ===== #
        # فرمول: (پایه + متریال + آپشن‌ها) + (سربارها)
        # نکته: برخی سربارها ضرب در تیراژ نمی‌شوند (مثل ستاپ)، برخی می‌شوند.
        # در اینجا فرض بر این است که متریال و آپشن‌ها قبلاً در تیراژ ضرب شده‌اند (اگر لازم بوده).
        
        total_raw = base_cost + material_cost + options_cost + config_setup_cost + config_design_cost
        
        # رند کردن به ۱۰۰ تومان (قانون بازار ایران)
        final_price = total_raw.quantize(Decimal('100'), rounding=ROUND_HALF_UP)

        result = {
            "final_price": float(final_price),
            "breakdown": {
                "base_product_price": float(base_cost),
                "material_cost": float(material_cost),
                "options_total": float(options_cost),
                "setup_cost": float(config_setup_cost),
                "design_cost": float(config_design_cost),
                "area_sqm": float(self.area_sqm),
                "options_details": options_breakdown
            }
        }
        
        logger.info(f"Calc Finished: {final_price} (Mat: {material_cost}, Opt: {options_cost})")
        return result

    def _calculate_material_cost(self) -> Decimal:
        """ محاسبه هزینه متریال بر اساس مساحت کل """
        if not self.pm:
            return Decimal(0)

        # قیمت واحد نهایی (شامل درصد سختی کار)
        unit_price = self.pm.final_material_price_per_sqm
        
        # هزینه ثابت متریال (مثلا هزینه برش ثابت)
        extra_fixed = self.pm.extra_price_per_unit * self.quantity
        
        # فرمول: (مساحت واحد × تعداد × قیمت واحد) + هزینه ثابت
        # Total Area = Area per unit * Quantity
        total_material_cost = (self.area_sqm * self.quantity * unit_price) + extra_fixed
        
        return total_material_cost

    def _calculate_options_total_cost(self):
        """
        محاسبه هوشمند هزینه آپشن‌ها بر اساس استراتژی تعریف شده در دیتابیس
        """
        total_opt_cost = Decimal(0)
        breakdown = []

        for val in self.selected_values:
            # 1. بررسی اعتبارسنجی‌های مالی
            # اگر گزینه یا والدش تیک "قیمت دارد" نداشته باشند، رد شو.
            if not val.has_pricing or not val.product_option.has_pricing:
                continue

            parent_option = val.product_option
            strategy = parent_option.pricing_strategy
            
            # هزینه ستاپ خودِ ویژگی (مثلا هزینه کلیشه طلاکوب) - یک بار حساب می‌شود یا در تیراژ؟
            # معمولا ستاپ یک بار است.
            option_setup = parent_option.base_price 
            
            # نرخ واحد (از رکورد Value می‌آید)
            rate = val.price_impact
            
            # محاسبه هزینه متغیر (Variable Cost) براساس استراتژی
            variable_cost = Decimal(0)

            # === Logic Switch === #
            if strategy == OptionPricingStrategy.FIXED:
                # مبلغ ثابت به ازای هر سفارش (مستقل از ابعاد)
                # اما آیا باید در تیراژ ضرب شود؟ 
                # اگر quantity_step داشته باشد یعنی به ازای تعداد است.
                count_multiplier = self._get_quantity_multiplier(val)
                variable_cost = rate * count_multiplier

            elif strategy == OptionPricingStrategy.PER_SQM:
                # (مساحت کل سفارش) × نرخ
                # مساحت کل = مساحت واحد × تیراژ
                total_area = self.area_sqm * self.quantity
                variable_cost = total_area * rate

            elif strategy == OptionPricingStrategy.PER_METER_PERIMETER:
                # (محیط کل سفارش) × نرخ
                # مثال: دوردوزی یا لیفه
                total_perimeter = self.perimeter_m * self.quantity
                variable_cost = total_perimeter * rate

            elif strategy == OptionPricingStrategy.PERCENTAGE:
                # درصدی از قیمت کل متریال
                # مثال: ۳۰٪ هزینه چاپ برای فوریت
                # نکته: باید دید درصد از "کل فاکتور" است یا "قیمت پایه". اینجا فرض بر هزینه متریال است.
                base_for_percent = self._calculate_material_cost() 
                variable_cost = base_for_percent * (rate / 100)

            elif strategy == OptionPricingStrategy.PER_UNIT_INPUT:
                # براساس ورودی عددی کاربر (مثلا تعداد پانچ)
                # ما باید ورودی کاربر رو از دیکشنری user_input_data پیدا کنیم
                # کلید دیکشنری معمولا ID آپشن هست.
                input_key = str(parent_option.option.id)
                user_qty = int(self.user_input_data.get(input_key, 0))
                # فرمول: تعداد ورودی × تیراژ سفارش × نرخ
                # مثال: ۴ تا پانچ × ۱۰۰۰ تا کارت × ۱۰۰ تومان
                variable_cost = (user_qty * self.quantity) * rate

            # جمع هزینه این خط
            line_cost = option_setup + variable_cost
            total_opt_cost += line_cost
            
            breakdown.append({
                "option": parent_option.option.label,
                "value": val.label,
                "strategy": strategy,
                "cost": float(line_cost)
            })

        return total_opt_cost, breakdown

    def _get_quantity_multiplier(self, val: ProductOptionValue) -> Decimal:
        """
        محاسبه ضریب تیراژ (Step-based Logic)
        مثال: قیمت هر ۱۰ عدد ۱۰۰۰ تومان. سفارش ۱۵ عدد.
        """
        step = val.quantity_step
        qty = Decimal(self.quantity)

        # حالت ساده: قیمت تکی
        if step == 1:
            return qty

        # حالت پله‌ای
        if val.is_step_ceiling:
            return Decimal(math.ceil(qty / step))
        else:
            return qty / Decimal(step)
    