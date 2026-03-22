import ast
import operator
from decimal import Decimal
from typing import Dict, Any, Tuple, Set

from django.db.models import Prefetch
from django.core.exceptions import ValidationError

from core.product.models import (
    Product, ProductField, ProductFieldChoice, 
    ProductFieldCondition, ProductFormula, 
    ConditionOperator, ConditionAction
)
from core.product.exceptions import InvalidProductDataException

# ======================================================= #
# 1. مفسر امن ریاضی (توسعه‌یافته برای محاسبات و شروط)
# ======================================================= #
class SafeMathEvaluator:
    """
    مفسر کاملاً ایزوله که بدون استفاده از eval() رشته‌های ریاضی را اجرا می‌کند.
    """
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.Gt: operator.gt,
        ast.Lt: operator.lt,
        ast.GtE: operator.ge,
        ast.LtE: operator.le,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
    }

    @classmethod
    def evaluate(cls, expression: str, variables: Dict[str, Decimal]):
        if not expression:
            return Decimal('0.0')
        try:
            parsed_expr = expression
            for var_name, var_value in sorted(variables.items(), key=lambda x: len(x[0]), reverse=True):
                parsed_expr = parsed_expr.replace(var_name, str(var_value))
            
            tree = ast.parse(parsed_expr, mode='eval').body
            result = cls._eval_node(tree)
            
            if isinstance(result, bool):
                return result
                
            return Decimal(str(result)).quantize(Decimal('0.00'))
            
        except ZeroDivisionError:
            raise InvalidProductDataException("خطای محاسباتی: تقسیم بر صفر در فرمول رخ داده است.")
        except Exception as e:
            raise InvalidProductDataException(f"خطا در تجزیه و محاسبه فرمول: {str(e)}")

    @classmethod
    def _eval_node(cls, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            return cls.allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            return cls.allowed_operators[type(node.op)](operand)
        elif isinstance(node, ast.Compare):
            left = cls._eval_node(node.left)
            op = node.ops[0]
            right = cls._eval_node(node.comparators[0])
            return cls.allowed_operators[type(op)](left, right)
        else:
            raise TypeError(f"ساختار نامعتبر در فرمول: {type(node)}")

# ======================================================= #
# 2. موتور هوشمند قیمت‌گذاری و تجمیع ویژگی‌ها
# ======================================================= #
class ProductPricingDomainService:

    @staticmethod
    def _evaluate_field_conditions(fields_map: Dict[int, ProductField], user_selections: Dict[str, Any]) -> Set[int]:
        """
        موتور ارزیابی شروط (Rule Engine).
        """
        active_field_ids = set(fields_map.keys())

        for field_id, field in fields_map.items():
            for condition in field.applied_conditions.all():
                trigger_id = str(condition.trigger_field_id)
                user_value = user_selections.get(trigger_id)

                is_condition_met = False

                if condition.operator == ConditionOperator.IS_EMPTY:
                    is_condition_met = not bool(user_value)
                elif condition.operator == ConditionOperator.IS_NOT_EMPTY:
                    is_condition_met = bool(user_value)
                elif user_value is not None:
                    user_values_list = user_value if isinstance(user_value, list) else [user_value]
                    user_values_str = [str(v) for v in user_values_list]

                    if condition.trigger_choice_id:
                        is_match = str(condition.trigger_choice_id) in user_values_str
                    else:
                        is_match = str(condition.trigger_value_text) in user_values_str

                    if condition.operator == ConditionOperator.EQUALS:
                        is_condition_met = is_match
                    elif condition.operator == ConditionOperator.NOT_EQUALS:
                        is_condition_met = not is_match

                if is_condition_met:
                    if condition.action in [ConditionAction.HIDE, ConditionAction.DISABLE]:
                        active_field_ids.discard(field.id)
                    elif condition.action in [ConditionAction.SHOW, ConditionAction.ENABLE]:
                        active_field_ids.add(field.id)

        return active_field_ids

    @classmethod
    def calculate_final_price(
        cls, 
        product_id: int, 
        user_selections: Dict[str, Any],
        strict_validation: bool = True
    ) -> Tuple[Decimal, Dict[str, Any]]:
        """
        دریافت ورودی‌های کاربر، تجمیع مقادیر فیلدها و اجرای ماشین‌حساب ریاضی.
        """
        try:
            # ===== اصلاح کوئری برای واکشی جداول دیکشنری ===== #
            product = Product.objects.prefetch_related(
                Prefetch('fields', queryset=ProductField.objects.filter(is_active=True).select_related('field_dict').prefetch_related(
                    'applied_conditions',
                    Prefetch('choices', queryset=ProductFieldChoice.objects.select_related('choice_dict'))
                )),
                'formulas'
            ).get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("محصول مورد نظر یافت نشد.")

        fields_map = {f.id: f for f in product.fields.all()}
        
        # ===== پیدا کردن فیلدهای فعال براساس Rule Engine ===== #
        active_field_ids = cls._evaluate_field_conditions(fields_map, user_selections)

        formula_variables = {}
        configuration_summary = []
        
        # متغیر پیش‌فرض برای تیراژ
        quantity_val = Decimal('1.0') 

        # ===== استخراج مقادیر فیلدها ===== #
        for f_id in active_field_ids:
            field = fields_map[f_id]
            field_dict = field.field_dict  # دسترسی سریع به دیکشنری
            str_f_id = str(f_id)
            var_name = f"field_{f_id}"
            
            # خواندن مقدار عددی پیش‌فرض از دیکشنری در صورت وجود (وگرنه 0)
            numeric_val = getattr(field_dict, 'numeric_value', Decimal('0.0'))
            
            if str_f_id in user_selections and user_selections[str_f_id] not in [None, '', [], 'null']:
                user_val = user_selections[str_f_id]

                # -------- حالت اول: فیلدهای تک انتخابی -------- #
                if field_dict.field_type in ['dropdown', 'single_select', 'radio']:
                    choice = next((c for c in field.choices.all() if str(c.id) == str(user_val)), None)
                    if not choice:
                        raise InvalidProductDataException(f"مقدار انتخابی برای '{field_dict.title}' نامعتبر است.")
                    
                    numeric_val += getattr(choice.choice_dict, 'numeric_value', Decimal('0.0'))
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": choice.choice_dict.title,
                        "choice_id": choice.id
                    })

                # -------- حالت دوم: فیلدهای چند انتخابی -------- #
                elif field_dict.field_type in ['multi_select', 'checkbox']:
                    if not isinstance(user_val, list):
                        user_val = [user_val]
                    
                    selected_choices = [c for c in field.choices.all() if str(c.id) in map(str, user_val)]
                    if not selected_choices:
                        raise InvalidProductDataException(f"مقادیر ارسالی برای فیلد '{field_dict.title}' معتبر نیست.")
                    
                    internal_result = getattr(selected_choices[0].choice_dict, 'numeric_value', Decimal('0.0'))
                    operator_choice = getattr(field_dict, 'multi_select_operator', 'add')

                    for c in selected_choices[1:]:
                        c_val = getattr(c.choice_dict, 'numeric_value', Decimal('0.0'))
                        if operator_choice == 'add':
                            internal_result += c_val
                        elif operator_choice == 'sub':
                            internal_result -= c_val
                        elif operator_choice == 'mul':
                            internal_result *= c_val
                        elif operator_choice == 'div':
                            if c_val == 0:
                                raise InvalidProductDataException(f"خطا: تقسیم بر صفر در گزینه‌های '{field_dict.title}'.")
                            internal_result /= c_val

                    numeric_val += internal_result
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": " ، ".join([c.choice_dict.title for c in selected_choices]),
                        "choice_ids": [c.id for c in selected_choices]
                    })

                # -------- حالت سوم: فیلدهای عددی و تیراژ -------- #
                elif field_dict.field_type == 'number':
                    try:
                        numeric_val += Decimal(str(user_val))
                        configuration_summary.append({
                            "field_id": field.id,
                            "field_title": field_dict.title,
                            "value": str(user_val),
                            "choice_id": None
                        })
                    except Exception:
                        raise InvalidProductDataException(f"مقدار وارد شده در فیلد '{field_dict.title}' باید عدد باشد.")
                
                # -------- حالت چهارم: فیلدهای متنی -------- #
                else:
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": str(user_val),
                        "choice_id": None
                    })
            
            # ویژگی is_required معمولاً در خود جدول واسط (ProductField) نگه‌داری می‌شود تا بتواند برای هر محصول متفاوت باشد
            elif getattr(field, 'is_required', False) and strict_validation:
                raise InvalidProductDataException(f"تکمیل فیلد '{field_dict.title}' الزامی است.")
            
            # ذخیره ارزش عددی فیلد
            formula_variables[var_name] = numeric_val
            
            # 🌟 شناسایی خودکار فیلد تیراژ با خواندن از دیکشنری
            if getattr(field_dict, 'is_quantity_field', False):
                quantity_val = numeric_val

        # ===== مقداردهی فیلدهای مخفی شده با صفر (برای جلوگیری از کرش فرمول) ===== # 
        for f_id in fields_map.keys():
            var_name = f"field_{f_id}"
            if var_name not in formula_variables:
                formula_variables[var_name] = Decimal('0.0')

        # 🌟 ===== تزریق متغیرهای سیستمی حیاتی به مفسر فرمول ===== 🌟
        formula_variables["price_per_unit"] = Decimal(str(product.price_per_unit)) if product.price_per_unit else Decimal('1.0')
        formula_variables["base_price"] = Decimal(str(product.price))
        formula_variables["quantity"] = quantity_val

        # ===== پیدا کردن فرمول مناسب ===== #
        formulas = list(product.formulas.all())
        
        # 🌟 ===== اگر محصول فرمولی نداشت (رفتار دیفالت استاندارد صنعت چاپ) ===== 🌟
        if not formulas:
            fields_sum = sum(v for k, v in formula_variables.items() if k.startswith('field_'))
            fallback_price = (formula_variables["base_price"] + fields_sum) * (quantity_val / formula_variables["price_per_unit"])
            return fallback_price.quantize(Decimal('0.00')), configuration_summary

        active_formula = None
        default_formula = None

        for formula in formulas:
            if not formula.condition_expression:
                default_formula = formula
                continue
            
            try:
                is_condition_met = SafeMathEvaluator.evaluate(
                    expression=formula.condition_expression, 
                    variables=formula_variables
                )
                if is_condition_met:
                    active_formula = formula
                    break
            except Exception:
                pass
        
        if not active_formula:
            active_formula = default_formula

        if not active_formula:
            active_formula = formulas[-1]

        # ===== انتخاب و اجرای فرمول نهایی ===== #
        final_price = SafeMathEvaluator.evaluate(
            expression=active_formula.calculation_expression,
            variables=formula_variables
        )

        if final_price < 0:
            final_price = Decimal('0.00')

        return final_price, configuration_summary
