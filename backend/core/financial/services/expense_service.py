from typing import Optional, List
from decimal import Decimal
from django.db import transaction, models
from rest_framework.exceptions import ValidationError, NotFound

from core.models import Expense, Order, Invoice
from core.financial.models import FinancialLog


class ExpenseService:
    """
    سرویس مدیریت هزینه‌های سفارش و هزینه‌های عمومی
    """

    @transaction.atomic
    def create_expense(self, name: str, amount: Decimal,
                       order: Optional[Order] = None,
                       expense_type: str = 'other',
                       quantity: int = 1,
                       unit_price: Optional[Decimal] = None,
                       description: str = '',
                       receipt=None,
                       registered_by=None) -> Expense:
        """
        ثبت هزینه جدید.
        اگر `order` داده شود، هزینه به آن سفارش مرتبط می‌شود.
        """
        if amount <= 0:
            raise ValidationError("مبلغ هزینه باید بزرگ‌تر از صفر باشد.")

        # تعیین مبلغ کل از تعداد * قیمت واحد در صورت عدم ارسال amount صریح
        if unit_price is not None:
            amount = quantity * unit_price

        expense = Expense.objects.create(
            order=order,
            name=name,
            amount=amount,
            expense_type=expense_type,
            quantity=quantity,
            unit_price=unit_price or amount,
            description=description,
            receipt=receipt,
            registered_by=registered_by,
        )

        # ثبت لاگ مالی
        FinancialLog.log(
            action_type=FinancialLog.ActionType.EXPENSE_ADDED,
            order=order,
            user=order.user if order else None,
            description=f"ثبت هزینه '{expense.name}' به مبلغ {expense.amount:,} IQD",
            created_by=registered_by,
        )
        return expense

    @transaction.atomic
    def update_expense(self, expense_id: int, data: dict, actor=None) -> Expense:
        """
        ویرایش هزینه موجود.
        """
        expense = Expense.objects.filter(id=expense_id).first()
        if not expense:
            raise NotFound("هزینه مورد نظر یافت نشد.")

        old_values = {
            'name': expense.name,
            'amount': str(expense.amount),
            'order_id': expense.order_id,
        }

        for field, value in data.items():
            if field in ['name', 'amount', 'expense_type', 'quantity',
                         'unit_price', 'description', 'order', 'receipt']:
                setattr(expense, field, value)

        expense.save()

        new_values = {
            'name': expense.name,
            'amount': str(expense.amount),
            'order_id': expense.order_id,
        }

        FinancialLog.log(
            action_type=FinancialLog.ActionType.EXPENSE_ADDED,  # یا یک نوع ویرایش
            order=expense.order,
            user=expense.order.user if expense.order else None,
            field_name='expense',
            old_value=old_values,
            new_value=new_values,
            description=f"ویرایش هزینه '{expense.name}'",
            created_by=actor,
        )
        return expense

    @transaction.atomic
    def delete_expense(self, expense_id: int, actor=None):
        """
        حذف هزینه.
        """
        expense = Expense.objects.filter(id=expense_id).first()
        if not expense:
            raise NotFound("هزینه مورد نظر یافت نشد.")
        order = expense.order
        expense.delete()
        FinancialLog.log(
            action_type=FinancialLog.ActionType.EXPENSE_ADDED,  # یا نوع حذف
            order=order,
            user=order.user if order else None,
            description=f"حذف هزینه '{expense.name}'",
            created_by=actor,
        )

    def get_order_expenses(self, order_id: int) -> List[Expense]:
        return Expense.objects.get_order_expenses(order_id)

    def get_orders_with_unlocked_invoices(self):
        """
        سفارشاتی که فاکتور دارند ولی فاکتور آن‌ها نهایی (FINALIZE) نشده است.
        """
        return Order.objects.filter(
            invoice__isnull=False
        ).exclude(
            invoice__status=Invoice.Status.FINALIZE
        ).select_related('user__customer_profile').prefetch_related('order_item_order__product')

    def calculate_order_profit(self, order: Order) -> dict:
        """
        محاسبه سود/زیان یک سفارش.
        سود = مبلغ نهایی سفارش - مجموع هزینه‌های مرتبط
        درصد سود = (سود / مبلغ نهایی) * 100
        """
        total_expenses = order.expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        profit = order.final_price - total_expenses
        if order.final_price > 0:
            profit_percent = (profit / order.final_price) * 100
        else:
            profit_percent = 0
        return {
            'order_id': order.id,
            'order_code': order.order_code,
            'final_price': order.final_price,
            'total_expenses': total_expenses,
            'profit': profit,
            'profit_percent': round(profit_percent, 2),
        }