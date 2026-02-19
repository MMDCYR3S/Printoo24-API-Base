from typing import Dict, Any, Tuple, Optional
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.product.services.calculator import ProductPriceCalculator
from core.models import (
    ProductOption, Product, OptionInputType,
    ProductOptionValue, ProductSize,
    ProductQuantity,
)
# ========== CART PROCESSOR ========== #
class CartProcessor:
    """
    کلاس کمکی برای پردازش ورودی‌ها، اعتبارسنجی آپشن‌ها و محاسبه قیمت نهایی.
    این کلاس هیچ تغییری در دیتابیس (Insert/Update) ایجاد نمی‌کند.
    """
    def __init__(self, product: Product, selections: Dict[str, Any], quantity_input: int):
        self.product = product
        self.selections = selections
        self.quantity_input = int(quantity_input)
        
        # ===== خروجی ها ===== #
        self.final_options_data = []
        self.selected_option_values = []
        self.user_raw_inputs = {}
        
        # ===== نتایج ====== #  
        self.result_price = Decimal(0)
        self.result_quantity = 0
        self.result_item_data = {}
        self.result_name = selections.get('name')
        self.result_description = selections.get('description')
        
    def process(self):
        """
        اجرای تمام مراحل پردازش آپشن‌ها.
        """
        # ===== دریافت ویژگی های مربوط به محصول ===== #
        self._process_options()
        
        # ===== سایزهایی که فرد انجام داده ===== #
        width, height, size_label = self._resolve_dimensions()
        
        # ===== دریافت و اعتبارسنجی تیراژ ===== #
        final_qty, qty_label = self._handle_quantity_logic()
        self.result_quantity = final_qty
        # ===== انجام عملیات محاسبه ===== #
        calculator = ProductPriceCalculator(
            product=self.product,
            quantity=final_qty,
            width=width,
            height=height,
            selected_values=self.selected_option_values,
            user_input_data=self.user_raw_inputs,
            selected_size_id=self.selections.get('size_id', None),
            has_design=self.selections.get('has_design', True)
        )
        # ===== محاسبه قیمت نهایی ===== #
        calc_result = calculator.calculate()
        self.result_price = Decimal(str(calc_result['final_price']))
        # ===== ایجاد ساختار نهایی سبد خرید ===== #
        self.result_item_data = {
            "options": self.final_options_data,
            "meta": {
                "size_info": {
                    "size_id": self.selections.get('size_id', None),
                    "size_name": size_label,
                    "width": width,
                    "height": height,
                },
                "quantity_info": {
                    "quantity_id": self.selections.get('quantity_id'),
                    "quantity_text": qty_label,
                },
                "has_design": self.selections.get('has_design', True),
                "price_breakdown": calc_result['breakdown']
            }
        }
        
        # ===== ذخیره سایز در انتخاب های مشتری ===== #
        if 'size_id' in self.selections:
             self.result_item_data['size_id'] = self.selections['size_id']

        return self

    # ========== LOGIC METHODS ========== #
    # ========== OPTION LOGIC ========== #
    def _process_options(self):
        """پردازش تمام آپشن‌های محصول"""
        product_options = self.product.options.all().prefetch_related('choices')
        incoming_options = self.selections.get('options', {})

        for prod_opt in product_options:
            str_opt_id = str(prod_opt.id)
            user_input = incoming_options.get(str_opt_id)
            # ===== چک کردن اجباری بودن ویژگی ===== #
            if prod_opt.is_required and user_input in [None, "", []]:
                raise ValidationError(f"انتخاب ویژگی '{prod_opt.label or prod_opt.name}' الزامی است.")
            
            # ===== در صورت نبود، گذر ===== #
            if user_input in [None, "", []]:
                continue

            # ===== اعتبارسنجی نوع داده ===== #
            processed_data = self._handle_input_type(prod_opt, user_input)
            if processed_data:
                self.final_options_data.append(processed_data)

    # ========== DIMENSIONS LOGIC ========== #
    def _resolve_dimensions(self) -> Tuple[float, float, Optional[str]]:
        """تشخیص طول و عرض بر اساس سایز آماده یا کاستوم"""
        size_id = self.selections.get('size_id', None)
        custom_width = self.selections.get('width', None)
        custom_height = self.selections.get('height', None)

        if size_id:
            try:
                ps = ProductSize.objects.get(product=self.product, id=size_id)
                return float(ps.size.width), float(ps.size.height), ps.size.name
            except ProductSize.DoesNotExist:
                raise ValidationError(_("سایز انتخاب شده نامعتبر است."))
        
        if custom_width and custom_height:
            return float(custom_width), float(custom_height), f"{custom_width}x{custom_height}"
            
        return 0.0, 0.0, None

    # ========== QUANTITY LOGIC ========== #
    def _handle_quantity_logic(self) -> Tuple[int, str]:
        """مدیریت منطق تیراژ (بسته‌ای یا عددی)"""
        final_quantity = self.quantity_input
        quantity_label = str(final_quantity)

        if self.product.has_quantity:
            qty_id = self.selections.get('quantity_id')
            if not qty_id:
                raise ValidationError(_("برای این محصول انتخاب 'تیراژ' (بسته) الزامی است."))
            try:
                pq = ProductQuantity.objects.select_related('quantity').get(product=self.product, id=qty_id)
                final_quantity = self.quantity_input if self.selections.get("quantity") else pq.quantity.value
                quantity_label = str(pq.quantity.value)
            except ProductQuantity.DoesNotExist:
                raise ValidationError(_("تیراژ انتخابی نامعتبر است."))
        else:
            # ===== اعتبارسنجی حداقل و حداکثر تعداد تیراژ ===== #
            config = getattr(self.product, 'pricing_config', None)
            if config:
                if not config.allow_custom_quantity:
                     raise ValidationError(_("نمی‌توانید به صورت دلخواه این تیراژ را انتخاب کنید."))
                if self.quantity_input < config.min_quantity:
                    raise ValidationError(f"حداقل تعداد سفارش {config.min_quantity} عدد است.")
                if self.quantity_input > config.max_quantity:
                    raise ValidationError(f"حداکثر تعداد سفارش {config.max_quantity} عدد است.")
            
        return final_quantity, quantity_label

    # ========== INPUT TYPE LOGIC ========== #
    def _handle_input_type(self, prod_opt: ProductOption, user_input: Any) -> Dict:
        """تصمیم‌گیری بر اساس Input Type"""
        itype = prod_opt.input_type
        # ===== نوع انتخاب تکی ===== #
        if itype in [OptionInputType.SELECT, OptionInputType.RADIO]:
            return self._process_single_selection(prod_opt, user_input)
        # ===== نوع انتخاب چندتایی ===== #
        elif itype in [OptionInputType.CHECKBOX, OptionInputType.MULTI_SELECT]:
            return self._process_multi_selection(prod_opt, user_input)
        # ===== نوع انتخاب متنی/عددی ===== #
        elif itype in [OptionInputType.TEXT, OptionInputType.TEXTAREA, OptionInputType.NUMBER]:
            return self._process_raw_input(prod_opt, user_input)
        return {}
    
    
    def _process_single_selection(self, prod_opt, value_id):
        """ پردازش انتخاب تکی (باید ID معتبر باشد) """
        # ===== دریافت گزینه ها و اعتبارسنجی ===== #
        try:
            choice = prod_opt.choices.get(id=value_id)
        except ProductOptionValue.DoesNotExist:
            raise ValidationError(f"گزینه انتخاب شده برای '{prod_opt.label}' نامعتبر است.")
        
        # ===== ذخیره ویژگی برای محاسبه قیمت ===== #
        self.selected_option_values.append(choice)
        
        # ===== بازگردانی یک لیستی از ویژگی ها ===== #
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "selection",
            "value": {
                "id": choice.id,
                "label": choice.label,
                "price": float(choice.price_impact)
            }
        }
        
    def _process_multi_selection(self, prod_opt, value_ids):
        """ پردازش انتخاب چندگانه (لیست ID) """
        
        # ===== اعتبارسنجی انتخاب ها و در صورت نبود، خطا دادن ===== #
        if not isinstance(value_ids, list):
            raise ValidationError(f"فرمت ورودی برای '{prod_opt.label}' باید لیست باشد.")
        
        # ===== اعتبارسنجی انتخاب های مشتری ===== #
        choices = prod_opt.choices.filter(id__in=value_ids)
        if len(choices) != len(set(value_ids)):
            raise ValidationError(f"برخی گزینه‌های انتخاب شده برای '{prod_opt.label}' نامعتبر هستند.")
        
        # ===== افزودن انتخاب های مشتری به لیست ===== #
        selected_items = []
        for choice in choices:
            self.selected_option_values.append(choice)
            selected_items.append({
                "id": choice.id,
                "label": choice.label,
                "price": float(choice.price_impact)
            })
            
        # ===== بازگردانی لیست ===== #
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "multi_selection",
            "values": selected_items
        }
        
    def _process_raw_input(self, prod_opt, raw_value):
        """ پردازش ورودی متنی یا عددی """
        
        # ===== ذخیره ورودی کاربر ===== #
        self.user_raw_inputs[str(prod_opt.id)] = str(raw_value)
        
        # ===== بررسی اینکه آیا نوع آن عدد است یا خیر ===== #
        if prod_opt.input_type == OptionInputType.NUMBER:
            try:
                float(raw_value)
            except ValueError:
                raise ValidationError(f"مقدار وارد شده برای '{prod_opt.label}' باید عددی باشد.")
        
        # ===== اصلاح سینیوری ===== #
        choice = prod_opt.choices.first()
        if choice:
            self.selected_option_values.append(choice)
        
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "raw",
            "value": str(raw_value)
        }