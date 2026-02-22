from typing import Dict, Any, Tuple, Optional
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import (
    Product
)
from core.infrastructure.messages import msg_provider

# ========== CART PROCESSOR ========== #
class CartProcessor:
    """
    مغز متفکر سبد خرید.
    مسئولیت‌ها:
    ۱. اعتبارسنجی ورودی‌های کاربر (Validation).
    ۲. فراخوانی ماشین‌حساب برای قیمت (Pricing).
    ۳. ساخت ساختار غنی و ساختاریافته‌ی JSON برای ذخیره در سبد خرید.
    """
    def __init__(self, product: Product, selections: Dict[str, Any], quantity_input: int):
        self.product = product
        self.selections = selections
        self.quantity_input = int(quantity_input)

        self.config = getattr(product, 'pricing_config', None)
        
        # خروجی‌ها
        self.final_options_data = [] # این همان لیستی است که در JSON ذخیره می‌شود
        self.selected_option_values = [] # لیست خام برای ارسال به ماشین‌حساب
        self.user_raw_inputs = {}
        
        # نتایج  
        self.result_price = Decimal(0)
        self.result_quantity = 0
        self.result_item_data = {}
        self.result_name = selections.get('name')
        self.result_description = selections.get('description')
        
    def process(self):
        return self




        
    def _process_multi_selection(self, prod_opt, value_ids):
        if not isinstance(value_ids, list):
            try:
                 value_ids = [int(value_ids)]
            except (ValueError, TypeError):
                 raise ValidationError(f"فرمت ورودی نامعتبر است.")
        
        choices = prod_opt.choices.filter(id__in=value_ids)
        if len(choices) != len(set(value_ids)):
            raise ValidationError(f"برخی گزینه‌ها نامعتبر هستند.")
        
        selected_items = []
        for choice in choices:
            self.selected_option_values.append(choice)
            selected_items.append(self._build_rich_choice_data(choice))
            
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "multi_selection",
            "values": selected_items
        }
        

    def _validate_dependencies(self):
        """
        گارد امنیتی بک‌اند: 
        بررسی می‌کند که آیا زیرویژگی‌های وابسته‌ای که کاربر انتخاب کرده، 
        واقعاً پیش‌نیازهایشان (ویژگی‌های والد) در سبد خرید موجود است یا خیر.
        """
        selected_ids = {val.id for val in self.selected_option_values}

        for val in self.selected_option_values:
            show_conditions = val.dependency_rules.filter(action='show')

            if show_conditions.exists():
                has_prerequisite = False
                
                for cond in show_conditions:
                    if cond.required_value_id in selected_ids:
                        has_prerequisite = True
                        break

                if not has_prerequisite:
                    raise ValidationError(msg_provider.get("cart.E4017", label=val.label))

            hide_conditions = val.dependency_rules.filter(action='hide')
            if hide_conditions.exists():
                for cond in hide_conditions:
                    if cond.required_value_id in selected_ids:
                        raise ValidationError(msg_provider.get("cart.E4018", label=val.label))
