from django.db import models
from django.db.models import Sum
from django.utils import timezone
from .base import BaseQuerySet

# ========== EXPENSE QUERYSET ========== #
class ExpenseQuerySet(BaseQuerySet):
    """کوئری‌های مربوط به هزینه‌ها"""
    
    def get_expenses_with_order(self):
        """لیست هزینه‌ها همراه با اطلاعات سفارش"""
        return self.select_related('order__user').order_by('-created_at')
    
    def get_order_expenses(self, order_id: int):
        """هزینه‌های مربوط به یک سفارش خاص"""
        return self.filter(order_id=order_id)
    
    def get_general_expenses(self):
        """هزینه‌های عمومی (بدون سفارش)"""
        return self.filter(order__isnull=True)
    
    def get_total_expenses(self) -> int:
        """مجموع کل هزینه‌ها"""
        result = self.aggregate(total=Sum('amount'))
        return int(result['total'] or 0)
    
    def get_expenses_by_date_range(self, start_date, end_date) -> int:
        """مجموع هزینه‌ها در بازه زمانی مشخص"""
        result = self.filter(
            created_at__range=(start_date, end_date)
        ).aggregate(total=Sum('amount'))
        return int(result['total'] or 0)
    
    def get_daily_expenses(self) -> int:
        """هزینه‌های امروز"""
        today = timezone.now().date()
        start = timezone.datetime.combine(today, timezone.datetime.min.time())
        end = timezone.datetime.combine(today, timezone.datetime.max.time())
        return self.get_expenses_by_date_range(start, end)
    
    def get_monthly_expenses(self) -> int:
        """هزینه‌های ماه جاری"""
        now = timezone.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_expenses_by_date_range(start, now)
    
    def get_yearly_expenses(self) -> int:
        """هزینه‌های سال جاری"""
        now = timezone.now()
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.get_expenses_by_date_range(start, now)

# ========== EXPENSE MANAGER ========== #
class ExpenseManager(models.Manager):
    def get_queryset(self):
        return ExpenseQuerySet(self.model, using=self._db)
    
    def get_expenses_with_order(self):
        return self.get_queryset().get_expenses_with_order()
    
    def get_order_expenses(self, order_id: int):
        return self.get_queryset().get_order_expenses(order_id)
    
    def get_general_expenses(self):
        return self.get_queryset().get_general_expenses()
    
    def get_total_expenses(self):
        return self.get_queryset().get_total_expenses()
    
    def get_expenses_by_date_range(self, start, end):
        return self.get_queryset().get_expenses_by_date_range(start, end)
    
    def get_daily_expenses(self):
        return self.get_queryset().get_daily_expenses()
    
    def get_monthly_expenses(self):
        return self.get_queryset().get_monthly_expenses()
    
    def get_yearly_expenses(self):
        return self.get_queryset().get_yearly_expenses()
    
    def create_expense(self, data):
        return self.create(**data)
