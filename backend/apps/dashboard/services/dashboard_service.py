from typing import Dict, Any
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from core.models import Product, Order, User, Invoice, Expense, Invoice

# ========== PRODUCT DASHBOARD SERVICE ========== #
class ProductDashboardStateService:
    """
    سرویس اپلیکیشن داشبورد محصولات.
    مستقیماً از ProductManager استفاده می‌کند.
    """
    # حذف init و _repo، چون مستقیم از مدل استفاده می‌کنیم

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_product_statistics(self) -> Dict[str, Any]:
        """
        دریافت آمار کامل محصولات برای داشبورد
        """
        now = timezone.now()
        
        # ===== محاسبه زمان ماهانه ===== #
        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== دریافت اطلاعات از ProductManager ===== #
        # استفاده از متدهای منیجر که در product/managers/product.py تعریف کردیم
        total_count = Product.objects.get_total_count()
        status_counts = Product.objects.get_status_breakdown()
        
        current_month_count = Product.objects.get_count_by_date_range(start_of_current_month, now)
        last_month_count = Product.objects.get_count_by_date_range(start_of_last_month, end_of_last_month)

        # ===== محاسبه درصد تغییر ===== #
        growth_percentage = self._calculate_percentage_change(current_month_count, last_month_count)

        # ===== ساختار خروجی نهایی ===== #
        stats = {
            "summary": {
                "total_products": total_count,
                "added_this_month": current_month_count,
                "added_last_month": last_month_count,
                "growth_percentage": growth_percentage,
                "growth_status": "positive" if growth_percentage >= 0 else "negative"
            },
            "status_breakdown": {
                "active": status_counts['active'],
                "inactive": status_counts['inactive'],
                "active_percentage": round((status_counts['active'] / total_count * 100), 1) if total_count > 0 else 0
            },
            "configuration_breakdown": Product.objects.get_quantity_status_breakdown()
        }
        
        return stats
    
# ========== ORDER DASHBOARD SERVICE ========== #
class OrderDashboardStateService:
    """
    سرویس اپلیکیشن داشبورد سفارشات.
    مستقیماً از OrderManager استفاده می‌کند.
    """
    PENDING_STATUS_CODE = 'PENDING_INITIAL_ADMIN' 

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_order_statistics(self) -> Dict[str, Any]:
        """
        دریافت آمار تجمیعی سفارشات.
        """
        now = timezone.now()
        
        # ===== زمان ماهانه ===== #
        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== دریافت اطلاعات از OrderManager ===== #
        total_orders = Order.objects.get_total_count()
        current_month_count = Order.objects.get_count_by_date_range(start_of_current_month, now)
        last_month_count = Order.objects.get_count_by_date_range(start_of_last_month, end_of_last_month)
        
        # تعداد سفارشات در انتظار تایید
        pending_approval_count = Order.objects.get_pending_initial_count(self.PENDING_STATUS_CODE)

        # تفکیک وضعیت‌ها
        raw_status_breakdown = Order.objects.get_status_breakdown()
        
        formatted_status_breakdown = [
            {"status": item['current_status__name'], "count": item['count']} 
            for item in raw_status_breakdown
        ]

        # محاسبه رشد
        growth_percentage = self._calculate_percentage_change(current_month_count, last_month_count)

        return {
            "summary": {
                "total_orders": total_orders,
                "pending_approval_count": pending_approval_count,
                "added_this_month": current_month_count,
                "added_last_month": last_month_count,
                "growth_percentage": growth_percentage,
                "growth_status": "positive" if growth_percentage >= 0 else "negative"
            },
            "status_breakdown": formatted_status_breakdown
        }

# ========== FINANCIAL DASHBOARD SERVICE ========== #
class FinancialDashboardStateService:

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_financial_statistics(self) -> Dict[str, Any]:
        now = timezone.now()

        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== همه داده‌های مالی از Invoice میان، نه Order ===== #
        total_revenue       = Invoice.objects.get_total_revenue()
        total_paid          = Invoice.objects.get_total_paid()
        avg_invoice_value   = Invoice.objects.get_average_invoice_value()

        revenue_this_month  = Invoice.objects.get_revenue_by_date_range(start_of_current_month, now)
        revenue_last_month  = Invoice.objects.get_revenue_by_date_range(start_of_last_month, end_of_last_month)
        paid_this_month     = Invoice.objects.get_paid_by_date_range(start_of_current_month, now)

        revenue_growth = self._calculate_percentage_change(revenue_this_month, revenue_last_month)

        # ===== نمودار روزانه ===== #
        raw_chart_data = Invoice.objects.get_daily_revenue_chart_data(days=30)
        formatted_chart_data = [
            {
                "date":        item['date'].strftime('%Y-%m-%d'),
                "amount":      item['total'],
                "paid":        item['paid'],
                "order_count": item['count']
            }
            for item in raw_chart_data
        ]

        return {
            "summary": {
                "total_revenue": total_revenue,
                "total_paid": total_paid,
                "outstanding": total_revenue - total_paid,
                "revenue_this_month": revenue_this_month,
                "revenue_last_month": revenue_last_month,
                "paid_this_month": paid_this_month,
                "revenue_growth": revenue_growth,
                "revenue_status": "positive" if revenue_growth >= 0 else "negative",
                "average_invoice_value": avg_invoice_value
            },
            "chart_data": formatted_chart_data
        }

# ========== USER DASHBOARD SERVICE ========== #
class UserDashboardStateService:
    """
    سرویس اپلیکیشن مخصوص داشبورد کاربران.
    مستقیماً از UserManager استفاده می‌کند.
    """

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_user_statistics(self) -> Dict[str, Any]:
        now = timezone.now()
        
        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== دریافت اطلاعات از UserManager ===== #
        total_users = User.objects.count() 
        
        new_users_this_month = User.objects.get_count_by_date_range(start_of_current_month, now)
        new_users_last_month = User.objects.get_count_by_date_range(start_of_last_month, end_of_last_month)

        dashboard_stats = User.objects.get_dashboard_stats()

        role_counts_raw = User.objects.get_role_breakdown()

        # محاسبه تغییر
        growth_percentage = self._calculate_percentage_change(new_users_this_month, new_users_last_month)

        formatted_role_breakdown = [
            {
                "role": item['role_name'],
                "slug": item['role_slug'],
                "count": item['count']
            } 
            for item in role_counts_raw
        ]

        return {
            "summary": {
                "total_users": dashboard_stats['total'],
                "new_this_month": new_users_this_month,
                "new_last_month": new_users_last_month,
                "growth_percentage": growth_percentage,
                "growth_status": "positive" if growth_percentage >= 0 else "negative",
                "total_customers": dashboard_stats['customer_count'],
                "total_staff": dashboard_stats['staff_count']
            },
            "status_breakdown": {
                "active": dashboard_stats['active'],
                "inactive": dashboard_stats['inactive']
            },
            "role_breakdown": formatted_role_breakdown
        }

# ========== EXPENSE SERVICE ========== #
class CombinedDashboardStateService:
    def get_combined_statistics(self):
        return {
            "products": ProductDashboardStateService().get_product_statistics(),
            "orders": OrderDashboardStateService().get_order_statistics(),
            "users": UserDashboardStateService().get_user_statistics(),
            "financial": FinancialDashboardStateService().get_financial_statistics(),
            "expenses": {
                "total_expenses": Expense.objects.get_total_expenses(),
                "daily_expenses": Expense.objects.get_daily_expenses(),
                "monthly_expenses": Expense.objects.get_monthly_expenses(),
                "yearly_expenses": Expense.objects.get_yearly_expenses(),
            },
            "profit": {
                "daily_profit": Invoice.objects.get_daily_profit(),
                "monthly_profit": Invoice.objects.get_monthly_profit(),
                "yearly_profit": Invoice.objects.get_yearly_profit(),
            }
        }