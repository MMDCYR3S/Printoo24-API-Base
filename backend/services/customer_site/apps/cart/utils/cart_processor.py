from typing import Dict, Any, Tuple, Optional
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.product.services.calculator import ProductPriceCalculator
from core.models import (
    ProductOption, Product, OptionInputType,
    ProductOptionValue, ProductSize,
    ProductQuantity, OptionValueQuantityPrice
)

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
        # 1. مدیریت تیراژ (اصلاح شده)
        final_qty, qty_label, matched_pq_id = self._handle_quantity_logic()
        self.result_quantity = final_qty

        # 2. بهینه‌سازی کوئری ماتریس قیمت
        self.matrix_overrides = {}
        if matched_pq_id:
            overrides = OptionValueQuantityPrice.objects.filter(product_quantity_id=matched_pq_id)
            self.matrix_overrides = {ov.option_value_id: ov.price for ov in overrides}

        # 3. پردازش ویژگی‌ها
        self._process_options()
        
        # 4. ابعاد و سایز
        width, height, size_label = self._resolve_dimensions()
        
        # 5. محاسبه قیمت نهایی
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
        calc_result = calculator.calculate()
        self.result_price = Decimal(str(calc_result['final_price']))
        
        # 6. ساختار JSON نهایی
        self.result_item_data = {
            "options": self.final_options_data,
            "meta": {
                "size_info": {
                    "size_id": self.selections.get('size_id', None),
                    "size_name": size_label,
                    "width": float(width),
                    "height": float(height),
                },
                "quantity_info": {
                    "product_quantity_id": matched_pq_id, # ذخیره آیدی واقعی رکورد واسط
                    "quantity_text": qty_label,
                    "quantity_value": final_qty
                },
                "has_design": self.selections.get('has_design', True),
                "price_breakdown": calc_result['breakdown']
            }
        }
        
        return self

    # ========== LOGIC METHODS ========== #
    def _handle_quantity_logic(self) -> Tuple[int, str, Optional[int]]:
        """
        [FIXED]: استفاده از ID خود ProductQuantity به جای آیدی گلوبال Quantity.
        """
        final_quantity = self.quantity_input
        quantity_label = str(final_quantity)
        matched_pq_id = None

        if self.product.has_quantity:
            pq_record_id = self.selections.get('quantity_id')
            if not pq_record_id:
                raise ValidationError(_("برای این محصول انتخاب 'تیراژ' الزامی است."))
            
            try:
                # جستجو براساس PK رکورد واسط و اطمینان از تعلق به این محصول
                pq = ProductQuantity.objects.select_related('quantity').get(
                    id=pq_record_id, 
                    product=self.product
                )
                final_quantity = pq.quantity.value
                quantity_label = str(pq.quantity.value)
                matched_pq_id = pq.id
            except ProductQuantity.DoesNotExist:
                raise ValidationError(_("تیراژ انتخابی نامعتبر است."))
        else:
            # منطق تیراژ دلخواه
            if self.config:
                if not self.config.allow_custom_quantity:
                     raise ValidationError(_("نمی‌توانید به صورت دلخواه تیراژ وارد کنید."))
                if self.quantity_input < self.config.min_quantity:
                    raise ValidationError(f"حداقل تعداد سفارش {self.config.min_quantity} عدد است.")
                if self.quantity_input > self.config.max_quantity:
                    raise ValidationError(f"حداکثر تعداد سفارش {self.config.max_quantity} عدد است.")
            
        return final_quantity, quantity_label, matched_pq_id

    def _process_options(self):
        """پردازش تمام آپشن‌های محصول"""
        product_options = self.product.options.all().prefetch_related('choices', 'choices__dependency_rules__required_value')
        incoming_options = self.selections.get('options', {})

        for prod_opt in product_options:
            str_opt_id = str(prod_opt.id)
            user_input = incoming_options.get(str_opt_id)
            
            # ===== چک کردن اجباری بودن ویژگی ===== #
            if prod_opt.is_required and user_input in [None, "", []]:
                raise ValidationError(f"انتخاب ویژگی '{prod_opt.label or prod_opt.name}' الزامی است.")
            
            if user_input in [None, "", []]:
                continue

            # ===== اعتبارسنجی نوع داده ===== #
            processed_data = self._handle_input_type(prod_opt, user_input)
            if processed_data:
                self.final_options_data.append(processed_data)
                
        self._validate_dependencies()

    def _resolve_dimensions(self) -> Tuple[Decimal, Decimal, Optional[str]]:
        """
        [FIXED]: استفاده از self.config به جای ارجاع اشتباه.
        """
        size_id = self.selections.get('size_id')
        custom_width = self.selections.get('width')
        custom_height = self.selections.get('height')

        # ۱. ابعاد ثابت (Fixed Size)
        if size_id:
            try:
                ps = ProductSize.objects.select_related('size').get(product=self.product, id=size_id)
                return Decimal(str(ps.size.width)), Decimal(str(ps.size.height)), ps.size.name
            except ProductSize.DoesNotExist:
                raise ValidationError(_("سایز انتخاب شده معتبر نیست."))

        # ۲. ابعاد دلخواه (Custom Dimensions)
        if custom_width and custom_height:
            if not self.config or not self.config.accepts_custom_dimensions:
                raise ValidationError(_("این محصول قابلیت سفارش با ابعاد دلخواه را ندارد."))

            width = Decimal(str(custom_width))
            height = Decimal(str(custom_height))

            # چک کردن محدوده مجاز
            if self.config.min_width and width < Decimal(str(self.config.min_width)):
                raise ValidationError(f"عرض نمی‌تواند کمتر از {self.config.min_width} باشد.")
            if self.config.max_width and width > Decimal(str(self.config.max_width)):
                raise ValidationError(f"عرض نمی‌تواند بیشتر از {self.config.max_width} باشد.")

            return width, height, f"ابعاد دلخواه ({width}x{height})"

        return Decimal('0'), Decimal('0'), None

    def _handle_input_type(self, prod_opt: ProductOption, user_input: Any) -> Dict:
        itype = prod_opt.input_type
        if itype in [OptionInputType.SELECT, OptionInputType.RADIO]:
            return self._process_single_selection(prod_opt, user_input)
        elif itype in [OptionInputType.CHECKBOX, OptionInputType.MULTI_SELECT]:
            return self._process_multi_selection(prod_opt, user_input)
        elif itype in [OptionInputType.TEXT, OptionInputType.TEXTAREA, OptionInputType.NUMBER]:
            return self._process_raw_input(prod_opt, user_input)
        return {}
    
    # ===== متد کمکی برای ساخت دیتای غنی هر آپشن ===== #
    def _build_rich_choice_data(self, choice: ProductOptionValue) -> Dict:
        """ استخراج اطلاعات کامل یک گزینه، از جمله قیمت ماتریسی و وابستگی‌ها """
        # قیمت پایه یا ماتریس رو درمیاریم
        base_price = float(choice.price_impact)
        applied_price = base_price
        is_matrix = False
        
        if choice.id in self.matrix_overrides:
            applied_price = float(self.matrix_overrides[choice.id])
            is_matrix = True

        # درآوردن لیست وابستگی‌ها برای نمایش به کاربر
        dependencies = []
        for rule in choice.dependency_rules.all():
            req_val = rule.required_value
            dependencies.append({
                "parent_option_name": req_val.product_option.label or req_val.product_option.name,
                "required_value_name": req_val.label or (req_val.global_source.label if req_val.global_source else "نامشخص")
            })

        return {
            "id": choice.id,
            "label": choice.label or (choice.global_source.label if choice.global_source else "نامشخص"),
            "applied_price": applied_price,
            "is_matrix_price": is_matrix,
            "dependencies": dependencies # این قسمت جادوی ماست که فرانت نشون میده!
        }

    def _process_single_selection(self, prod_opt, value_id):
        try:
            choice = prod_opt.choices.get(id=value_id)
        except ProductOptionValue.DoesNotExist:
            raise ValidationError(f"گزینه انتخاب شده برای '{prod_opt.label}' نامعتبر است.")
        
        self.selected_option_values.append(choice)
        
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "selection",
            "value": self._build_rich_choice_data(choice)
        }
        
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
        
    def _process_raw_input(self, prod_opt, raw_value):
        # ... (کد قبلی بدون تغییر) ...
        self.user_raw_inputs[str(prod_opt.id)] = str(raw_value)
        if prod_opt.input_type == OptionInputType.NUMBER:
            try:
                float(raw_value)
            except ValueError:
                raise ValidationError(f"مقدار باید عددی باشد.")
        
        choice = prod_opt.choices.first()
        if choice:
            self.selected_option_values.append(choice)
            
        return {
            "option_id": prod_opt.id,
            "option_label": prod_opt.label or prod_opt.name,
            "type": "raw",
            "value": str(raw_value)
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
                    raise ValidationError(
                        f"امکان انتخاب زیرویژگی '{val.label}' وجود ندارد، زیرا ویژگی پیش‌نیاز آن انتخاب نشده است."
                    )

            hide_conditions = val.dependency_rules.filter(action='hide')
            if hide_conditions.exists():
                for cond in hide_conditions:
                    if cond.required_value_id in selected_ids:
                        raise ValidationError(
                            f"انتخاب همزمان '{val.label}' و پیش‌نیاز متضاد آن امکان‌پذیر نیست."
                        )
