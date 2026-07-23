from core.models import Order, Expense, Invoice
from django.db import models

class ExpenseService:
    """سرویس مدیریت هزینه‌ها"""
    
    @staticmethod
    def create_expense(name: str, amount: int, order=None) -> Expense:
        """
        ایجاد هزینه جدید.
        
        Args:
            name: عنوان هزینه
            amount: مبلغ
            order_id: شناسه سفارش (اختیاری)
        
        Returns:
            Expense: شیء هزینه ایجاد شده
        """
        return Expense.objects.create_expense({
            'name': name,
            'amount': amount,
            'order': order
        })
    
    @staticmethod
    def update_expense(expense_id: int, data: dict) -> Expense:
        """
        بروزرسانی هزینه موجود.
        
        Args:
            expense_id: شناسه هزینه
            data: دیکشنری حاوی فیلدهای قابل ویرایش
        
        Returns:
            Expense: شیء هزینه بروزرسانی شده
        """
        expense = Expense.objects.get(id=expense_id)
        
        for key, value in data.items():
            if hasattr(expense, key):
                setattr(expense, key, value)
        
        expense.save()
        return expense
    
    @staticmethod
    def delete_expense(expense_id: int) -> bool:
        """
        حذف هزینه.
        
        Args:
            expense_id: شناسه هزینه
        
        Returns:
            bool: True در صورت موفقیت
        """
        try:
            expense = Expense.objects.get(id=expense_id)
            expense.delete()
            return True
        except Expense.DoesNotExist:
            return False
    
    @staticmethod
    def get_expense_detail(expense_id: int) -> Expense:
        """
        دریافت جزئیات یک هزینه.
        
        Args:
            expense_id: شناسه هزینه
        
        Returns:
            Expense: شیء هزینه
        """
        return Expense.objects.select_related('order').get(id=expense_id)
    
    @staticmethod
    def get_order_total_expenses(order_id: int) -> int:
        """
        محاسبه مجموع هزینه‌های یک سفارش.
        
        Args:
            order_id: شناسه سفارش
        
        Returns:
            int: مجموع هزینه‌ها
        """
        expenses = Expense.objects.get_order_expenses(order_id)
        return expenses.aggregate(total=models.Sum('amount'))['total'] or 0


    @staticmethod
    def get_orders_with_unlocked_invoices() -> models.QuerySet:
        """
        دریافت تمامی سفارشاتی که فاکتور دارند و فاکتور آن‌ها قفل (نهایی) نشده است.
        """
        return Order.objects.filter(
            invoice__isnull=False
        ).exclude(
            invoice__status=Invoice.Status.FINALIZE
        ).select_related('invoice', 'current_status', 'user')
