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
        بررسی می‌کند کاربر چه مقادیری فرستاده، تا فیلدهایی که باید مخفی شوند را از چرخه محاسبه حذف کند.
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
                    # پشتیبانی از حالت چندانتخابی در trigger
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
    def calculate_final_price(cls, product_id: int, user_selections: Dict[str, Any]) -> Tuple[Decimal, Dict[str, Any]]:
        """
        دریافت ورودی‌های کاربر، تجمیع مقادیر فیلدها و اجرای فرمول.
        """
        try:
            product = Product.objects.prefetch_related(
                Prefetch('fields', queryset=ProductField.objects.filter(is_active=True).prefetch_related(
                    'choices', 'applied_conditions'
                )),
                'formulas'
            ).get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("محصول مورد نظر یافت نشد.")

        fields_map = {f.id: f for f in product.fields.all()}
        
        # ===== انتخاب فیلدهای انتخاب شده ===== #
        active_field_ids = cls._evaluate_field_conditions(fields_map, user_selections)

        formula_variables = {}
        configuration_summary = []

        # ===== انتخاب فیلدهای فعال ===== #
        for f_id in active_field_ids:
            field = fields_map[f_id]
            str_f_id = str(f_id)
            var_name = f"field_{f_id}"
            
            # ===== مقدار پایه هر فیلد ===== #
            numeric_val = field.numeric_value 
            
            if str_f_id in user_selections and user_selections[str_f_id] not in [None, '', [], 'null']:
                user_val = user_selections[str_f_id]

                # ===== حالت اول: فیلدهای تک انتخابی ===== #
                if field.field_type in ['dropdown', 'single_select', 'radio']:
                    choice = next((c for c in field.choices.all() if str(c.id) == str(user_val)), None)
                    if not choice:
                        raise InvalidProductDataException(f"مقدار انتخابی برای '{field.title}' نامعتبر است.")
                    
                    numeric_val += choice.numeric_value
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field.title,
                        "value": choice.title,
                        "choice_id": choice.id
                    })

                # ===== حالت دوم: فیلدهای چند انتخابی (پیاده‌سازی عملگر داخلی) ===== #
                elif field.field_type in ['multi_select', 'checkbox']:
                    if not isinstance(user_val, list):
                        user_val = [user_val]
                    
                    selected_choices = [c for c in field.choices.all() if str(c.id) in map(str, user_val)]
                    if not selected_choices:
                        raise InvalidProductDataException(f"مقادیر ارسالی برای فیلد '{field.title}' معتبر نیست.")
                    
                    # ===== انتخاب فیلدهایی که ادمین در نظر گرفته ===== #
                    internal_result = selected_choices[0].numeric_value
                    operator_choice = getattr(field, 'multi_select_operator', 'add')

                    for c in selected_choices[1:]:
                        if operator_choice == 'add':
                            internal_result += c.numeric_value
                        elif operator_choice == 'sub':
                            internal_result -= c.numeric_value
                        elif operator_choice == 'mul':
                            internal_result *= c.numeric_value
                        elif operator_choice == 'div':
                            if c.numeric_value == 0:
                                raise InvalidProductDataException(f"خطا: تقسیم بر صفر در گزینه‌های '{field.title}'.")
                            internal_result /= c.numeric_value

                    numeric_val += internal_result
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field.title,
                        "value": " ، ".join([c.title for c in selected_choices]),
                        "choice_ids": [c.id for c in selected_choices]
                    })

                # ===== حالت سوم: فیلدهای عددی و تیراژ ===== #
                elif field.field_type == 'number':
                    try:
                        numeric_val += Decimal(str(user_val))
                        configuration_summary.append({
                            "field_id": field.id,
                            "field_title": field.title,
                            "value": str(user_val),
                            "choice_id": None
                        })
                    except Exception:
                        raise InvalidProductDataException(f"مقدار وارد شده در فیلد '{field.title}' باید عدد باشد.")
                
                # ===== حالت چهارم: فیلدهای متنی ===== #
                else:
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field.title,
                        "value": str(user_val),
                        "choice_id": None
                    })
            
            elif field.is_required:
                raise InvalidProductDataException(f"تکمیل فیلد '{field.title}' الزامی است.")
            
            formula_variables[var_name] = numeric_val

        # ===== در نظر نگرفتن فیلدهای مخفی ===== # 
        for f_id in fields_map.keys():
            var_name = f"field_{f_id}"
            if var_name not in formula_variables:
                formula_variables[var_name] = Decimal('0.0')

        formula_variables["price_per_unit"] = Decimal(str(product.price_per_unit))

        # ===== پیدا کردن فرمول مناسب ===== #
        formulas = list(product.formulas.all())
        if not formulas:
            return sum(formula_variables.values()), configuration_summary

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

            if SafeMathEvaluator.evaluate(formula.condition_expression, formula_variables):
                active_formula = formula
                break
        
        if not active_formula:
            active_formula = default_formula

        if not active_formula:
            active_formula = formulas[-1]

        # ===== انتخاب و اجرای فرمول انتخاب شده ===== #
        final_price = SafeMathEvaluator.evaluate(
            expression=active_formula.calculation_expression,
            variables=formula_variables
        )

        if final_price < 0:
            final_price = Decimal('0.00')

        return final_price, configuration_summary
