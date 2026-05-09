import ast
import operator
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Set

from django.db.models import Prefetch
from django.core.exceptions import ValidationError

from ..models import (
    Product, ProductField, ProductFieldChoice, 
    ProductFieldCondition, ProductFormula, 
    ConditionOperator, ConditionAction
)
from ..exceptions import InvalidProductDataException

# ======================================================= #
# 1. مفسر امن ریاضی (Safe AST Math Parser)
# ======================================================= #
class SafeMathEvaluator:
    """
    مفسر امن برای تبدیل رشته فرمول به خروجی ریاضی بدون استفاده از توابع خطرناک.
    """
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
    }

    @classmethod
    def evaluate(cls, expression: str, variables: Dict[str, Decimal]) -> Decimal:
        try:
            parsed_expr = expression
            # جایگذاری متغیرها از طولانی‌ترین نام به کوتاه‌ترین (برای جلوگیری از تداخل مثلا id 1 و id 12)
            for var_name, var_value in sorted(variables.items(), key=lambda x: len(x[0]), reverse=True):
                parsed_expr = parsed_expr.replace(var_name, str(var_value))
            
            tree = ast.parse(parsed_expr, mode='eval').body
            result = cls._eval_node(tree)
            return Decimal(str(result)).quantize(Decimal('0.00')) # فرمت دقیق پولی
            
        except ZeroDivisionError:
            raise InvalidProductDataException("خطای محاسباتی: تقسیم بر صفر در فرمول محصول وجود دارد.")
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
        else:
            raise TypeError("ساختار نامعتبر در فرمول ریاضی.")


# ======================================================= #
# 2. سرویس اصلی دامنه (Domain Service)
# ======================================================= #
class ProductPricingDomainService:
    
    @staticmethod
    def _evaluate_conditions(fields_map: Dict[int, ProductField], user_selections: Dict[str, Any]) -> Set[int]:
        """
        این متد بررسی می‌کند کدام فیلدها بر اساس شروط (Conditions) باید فعال/آشکار بمانند و کدام‌ها حذف شوند.
        خروجی: لیستی از ID فیلدهای فعال (Active/Visible)
        """
        active_field_ids = set(fields_map.keys())

        for field_id, field in fields_map.items():
            # بررسی شروطی که روی این فیلد اعمال شده (این فیلد هدف است)
            for condition in field.applied_conditions.all():
                trigger_id = str(condition.trigger_field_id)
                user_value = user_selections.get(trigger_id)

                is_condition_met = False

                # منطق بررسی عملگرها
                if condition.operator == ConditionOperator.IS_EMPTY:
                    is_condition_met = not bool(user_value)
                elif condition.operator == ConditionOperator.IS_NOT_EMPTY:
                    is_condition_met = bool(user_value)
                elif user_value is not None:
                    # اگر فیلد انتخابی است، مقایسه با ID زیرمجموعه
                    if condition.trigger_choice_id:
                        is_match = str(condition.trigger_choice_id) == str(user_value)
                    # اگر فیلد متنی/عددی است، مقایسه با مقدار تایپ شده
                    else:
                        is_match = str(condition.trigger_value_text) == str(user_value)

                    if condition.operator == ConditionOperator.EQUALS:
                        is_condition_met = is_match
                    elif condition.operator == ConditionOperator.NOT_EQUALS:
                        is_condition_met = not is_match

                # اعمال عملیات در صورت برقرار بودن شرط
                if is_condition_met:
                    if condition.action in [ConditionAction.HIDE, ConditionAction.DISABLE]:
                        active_field_ids.discard(field.id)
                    elif condition.action in [ConditionAction.SHOW, ConditionAction.ENABLE]:
                        active_field_ids.add(field.id)

        return active_field_ids

    @classmethod
    def calculate_final_price(cls, product_id: int, user_selections: Dict[str, Any], strict_validation: bool = True) -> Tuple[Decimal, Dict[str, Any]]:
        """
        متد اصلی محاسبه قیمت.
        user_selections: {'12': '45', '15': '1000'} -> {field_id: choice_id_or_typed_value}
        """
        # --- 1. واکشی سنگین اما بهینه (بدون N+1) ---
        try:
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
        
        # --- 2. پردازش شروط (Rule Engine) ---
        active_field_ids = cls._evaluate_conditions(fields_map, user_selections)

        formula_variables = {}
        configuration_summary = []

        # --- 3. استخراج مقادیر عددی برای فیلدهای فعال ---
        for f_id in active_field_ids:
            field = fields_map[f_id]
            str_f_id = str(f_id)
            var_name = f"field_{f_id}"
            
            numeric_val = field.numeric_value # عدد پایه فیلد (در صورت وجود)
            
            # اگر کاربر مقداری برای این فیلد فرستاده است:
            if str_f_id in user_selections and user_selections[str_f_id] not in [None, '', 'null']:
                user_val = user_selections[str_f_id]

                # حالت الف: فیلدهای انتخابی (یافتن آبجکت زیرمجموعه)
                if field.field_dict.field_type in ['dropdown', 'single_select', 'multi_select']:
                    choice = next((c for c in field.choices.all() if str(c.id) == str(user_val)), None)
                    if not choice:
                        raise InvalidProductDataException(f"مقدار انتخابی برای '{field.field_dict.title}' نامعتبر است.")
                    
                    numeric_val += choice.numeric_value
                    configuration_summary[field.field_dict.title] = choice.choice_dict.title

                # حالت ب: فیلدهای متنی یا عددی
                elif field.field_dict.field_type == 'number':
                    try:
                        numeric_val += Decimal(str(user_val))
                        configuration_summary[field.field_dict.title] = str(user_val)
                    except Exception:
                        raise InvalidProductDataException(f"مقدار فیلد '{field.field_dict.title}' باید عدد باشد.")
                else:
                    # فیلد متنی در محاسبات اثری ندارد اما در خلاصه سفارش ثبت می‌شود
                    configuration_summary[field.field_dict.title] = str(user_val)
            
            elif field.is_required and strict_validation:
                raise InvalidProductDataException(f"پر کردن فیلد '{field.field_dict.title}' الزامی است.")

            formula_variables[var_name] = numeric_val

        for f_id in fields_map.keys():
            var_name = f"field_{f_id}"
            if var_name not in formula_variables:
                formula_variables[var_name] = Decimal('0.0')

        # --- 4. یافتن فرمول و محاسبه خروجی ---
        active_formula = product.formulas.first() # در صورت نیاز به شروط روی خود فرمول‌ها، منطق اینجا قرار می‌گیرد
        
        if not active_formula:
            # اگر محصول فرمول ندارد، فرض می‌کنیم قیمت حاصل جمع جبری تمام فیلدهاست
            total = sum(formula_variables.values())
            return total, configuration_summary

        # --- 5. اجرای ماشین حساب امن ---
        final_price = SafeMathEvaluator.evaluate(
            expression=active_formula.calculation_expression,
            variables=formula_variables
        )

        return final_price, configuration_summary
