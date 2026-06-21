import ast
import operator
from decimal import Decimal, ROUND_HALF_UP
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
    مفسر امن برای تبدیل رشته فرمول به خروجی ریاضی بدون استفاده از eval().
    """
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Gt: operator.gt,
        ast.Lt: operator.lt,
        ast.GtE: operator.ge,
        ast.LtE: operator.le,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
    }

    @classmethod
    def evaluate(cls, expression: str, variables: Dict[str, Decimal]):
        """
        ارزیابی فرمول با جایگزینی امن متغیرها از طریق AST.
        از طولانی‌ترین نام به کوتاه‌ترین جایگزین می‌کند تا از تداخل جلوگیری شود.
        """
        if not expression or not expression.strip():
            return Decimal('0')

        try:
            parsed_expr = expression.strip()
            # جایگذاری متغیرها از طولانی‌ترین نام به کوتاه‌ترین
            for var_name, var_value in sorted(variables.items(), key=lambda x: len(x[0]), reverse=True):
                parsed_expr = parsed_expr.replace(var_name, str(var_value))

            tree = ast.parse(parsed_expr, mode='eval').body
            result = cls._eval_node(tree)

            if isinstance(result, bool):
                return result

            return Decimal(str(result)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        except ZeroDivisionError:
            raise InvalidProductDataException("هەڵەی ژمێریاری: دابەشکردن بەسەر سفر لە فۆرمۆڵای بەرهەمەکەدا هەیە.")
        except Exception as e:
            raise InvalidProductDataException(f"هەڵە لە شیکردنەوە و ئەژمارکردنی فۆرمۆڵادا: {str(e)}")

    @classmethod
    def _eval_node(cls, node):
        # اعداد ثابت (Python < 3.8)
        if isinstance(node, ast.Num):
            return node.n

        # اعداد ثابت (Python >= 3.8)
        elif isinstance(node, ast.Constant):
            return node.value

        # عملگرهای دوتایی (+, -, *, /, ...)
        elif isinstance(node, ast.BinOp):
            left = cls._eval_node(node.left)
            right = cls._eval_node(node.right)
            op_func = cls.allowed_operators.get(type(node.op))
            if not op_func:
                raise TypeError(f"کارپێکەری '{type(node.op).__name__}' پشتگیری ناکرێت")
            return op_func(left, right)

        # عملگرهای یکتایی (-, +)
        elif isinstance(node, ast.UnaryOp):
            operand = cls._eval_node(node.operand)
            op_func = cls.allowed_operators.get(type(node.op))
            if not op_func:
                raise TypeError(f"کارپێکەری '{type(node.op).__name__}' پشتگیری ناکرێت")
            return op_func(operand)

        # مقایسه‌ها (>, <, ==, !=, >=, <=)
        elif isinstance(node, ast.Compare):
            left = cls._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = cls._eval_node(comparator)
                op_func = cls.allowed_operators.get(type(op))
                if not op_func:
                    raise TypeError(f"کارپێکەری بەراوردکاری '{type(op).__name__}' پشتگیری ناکرێت")
                if not op_func(left, right):
                    return False
                left = right
            return True

        # عملگرهای منطقی (and, or)
        elif isinstance(node, ast.BoolOp):
            op_func = cls.allowed_operators.get(type(node.op))
            if not op_func:
                raise TypeError(f"کارپێکەری لۆجیکی '{type(node.op).__name__}' پشتگیری ناکرێت")
            values = [cls._eval_node(v) for v in node.values]
            result = values[0]
            for val in values[1:]:
                result = op_func(result, val)
            return result

        else:
            raise TypeError(f"پێکهاتەی نادروست لە فۆرمۆڵادا:{type(node).__name__}")


# ======================================================= #
# 2. سرویس اصلی دامنه (Domain Service)
# ======================================================= #
class ProductPricingDomainService:

    @staticmethod
    def _evaluate_conditions(
        fields_map: Dict[int, 'ProductField'],
        user_selections: Dict[str, Any]
    ) -> Set[int]:
        """
        موتور ارزیابی شروط (Rule Engine).
        بررسی می‌کند کدام فیلدها باید فعال/آشکار بمانند.
        خروجی: مجموعه‌ای از ID فیلدهای فعال
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
                    # پشتیبانی از چندانتخابی
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
    ) -> Tuple[Decimal, List[Dict[str, Any]]]:
        """
        متد اصلی محاسبه قیمت.

        user_selections نمونه:
            {'12': 45, '15': [88, 92], '20': 3.5}
            کلید = ProductField.id (به صورت string)
            مقدار = ProductFieldChoice.id یا مقدار عددی/متنی

        خروجی:
            (final_price: Decimal, configuration_summary: List[dict])
            هر آیتم configuration_summary:
            {
                "field_id": int,
                "field_title": str,
                "value": str,         ← عنوان فارسی گزینه انتخابی
                "choice_id": int|None
            }
        """

        # ===== ۱. واکشی بهینه بدون N+1 ===== #
        try:
            product = Product.objects.prefetch_related(
                Prefetch(
                    'fields',
                    queryset=ProductField.objects.filter(is_active=True)
                        .select_related('field_dict')
                        .prefetch_related(
                            'applied_conditions',
                            Prefetch(
                                'choices',
                                queryset=ProductFieldChoice.objects.select_related('choice_dict')
                            )
                        )
                ),
                'formulas'
            ).get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("بەرهەمی دیاریکراو نەدۆزرایەوە.")

        fields_map = {f.id: f for f in product.fields.all()}

        # ===== ۲. پردازش شروط (Rule Engine) ===== #
        active_field_ids = cls._evaluate_conditions(fields_map, user_selections)

        formula_variables: Dict[str, Decimal] = {}
        configuration_summary: List[Dict[str, Any]] = []  # ← LIST نه dict
        quantity_val = Decimal('1')

        # ===== ۳. استخراج مقادیر عددی برای فیلدهای فعال ===== #
        for f_id in active_field_ids:
            field = fields_map[f_id]
            field_dict = field.field_dict
            str_f_id = str(f_id)
            var_name = f"field_{f_id}"

            numeric_val = field.numeric_value  # مقدار پایه فیلد

            if str_f_id in user_selections and user_selections[str_f_id] not in [None, '', [], 'null']:
                user_val = user_selections[str_f_id]

                # -------- تک‌انتخابی (dropdown / single_select / radio) -------- #
                if field_dict.field_type in ['dropdown', 'single_select', 'radio']:
                    choice = next(
                        (c for c in field.choices.all() if str(c.id) == str(user_val)),
                        None
                    )
                    if not choice:
                        raise InvalidProductDataException(
                            f"بڕی دیاریکراو بۆ '{field_dict.title}' نادروستە."
                        )

                    numeric_val += choice.numeric_value
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": choice.choice_dict.title,
                        "choice_id": choice.id,
                    })

                # -------- چندانتخابی (multi_select / checkbox) -------- #
                elif field_dict.field_type in ['multi_select', 'checkbox']:
                    if not isinstance(user_val, list):
                        user_val = [user_val]

                    selected_choices = [
                        c for c in field.choices.all()
                        if str(c.id) in [str(v) for v in user_val]
                    ]
                    if not selected_choices:
                        raise InvalidProductDataException(
                            f"بڕە نێردراوەکان بۆ فیلدی '{field_dict.title}' دروست نین."
                        )

                    # اعمال عملگر چندانتخابی (add/sub/mul/div)
                    internal_result = selected_choices[0].numeric_value
                    multi_op = getattr(field_dict, 'multi_select_operator', 'add')

                    for c in selected_choices[1:]:
                        c_val = c.numeric_value
                        if multi_op == 'add':
                            internal_result += c_val
                        elif multi_op == 'sub':
                            internal_result -= c_val
                        elif multi_op == 'mul':
                            internal_result *= c_val
                        elif multi_op == 'div':
                            if c_val == 0:
                                raise InvalidProductDataException(
                                    f"خطا: تقسیم بر صفر در گزینه‌های '{field_dict.title}'."
                                )
                            internal_result /= c_val

                    numeric_val += internal_result
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": " ، ".join([c.choice_dict.title for c in selected_choices]),
                        "choice_id": [c.id for c in selected_choices],
                    })

                # -------- عددی (number) -------- #
                elif field_dict.field_type == 'number':
                    try:
                        typed_val = Decimal(str(user_val))
                        numeric_val += typed_val
                        configuration_summary.append({
                            "field_id": field.id,
                            "field_title": field_dict.title,
                            "value": str(user_val),
                            "choice_id": None,
                        })
                    except Exception:
                        raise InvalidProductDataException(
                            f"بڕی داخلکراو لە فیلدی '{field_dict.title}' دەبێت ژمارە بێت."
                        )

                # -------- متنی (text / textarea) -------- #
                else:
                    configuration_summary.append({
                        "field_id": field.id,
                        "field_title": field_dict.title,
                        "value": str(user_val),
                        "choice_id": None,
                    })

            elif field.is_required and strict_validation:
                raise InvalidProductDataException(
                    f"پڕکردنەوەی فیلدی '{field_dict.title}' پێویستە."
                )

            formula_variables[var_name] = numeric_val

            # شناسایی خودکار فیلد تیراژ
            if field_dict.is_quantity_field:
                quantity_val = numeric_val

        # ===== فیلدهای مخفی‌شده را با صفر مقداردهی کن ===== #
        for f_id in fields_map.keys():
            var_name = f"field_{f_id}"
            if var_name not in formula_variables:
                formula_variables[var_name] = Decimal('0')

        # ===== متغیرهای سیستمی ===== #
        formula_variables["base_price"] = Decimal(str(product.price))
        formula_variables["price_per_unit"] = Decimal(str(product.price_per_unit)) if product.price_per_unit else Decimal('1')
        formula_variables["quantity"] = quantity_val

        # ===== ۴. انتخاب فرمول مناسب ===== #
        formulas = list(product.formulas.all())

        # اگر محصول فرمول ندارد → fallback استاندارد
        if not formulas:
            fields_sum = sum(
                v for k, v in formula_variables.items()
                if k.startswith('field_')
            )
            fallback_price = (formula_variables["base_price"] + fields_sum)
            return max(fallback_price, Decimal('0')).quantize(Decimal('1'), rounding=ROUND_HALF_UP), configuration_summary

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

        # ===== ۵. اجرای فرمول نهایی ===== #
        final_price = SafeMathEvaluator.evaluate(
            expression=active_formula.calculation_expression,
            variables=formula_variables
        )

        if isinstance(final_price, bool) or final_price < 0:
            final_price = Decimal('0')

        return final_price.quantize(Decimal('1'), rounding=ROUND_HALF_UP), configuration_summary
