from typing import Dict, Any
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from core.domain.catalog.product import ProductRepository
from core.domain.commerce.order import OrderRepository
from core.domain.identity.users import UserRepository
from core.models import Order

# ========================================= #
# ======== Product Dashboard Logic ======== #
# ========================================= #
class ProductDashboardStateService:
    """
    همان کلاس قبلی برای محصولات (بدون تغییر)
    """
    def __init__(self):
        self._repo = ProductRepository()

    def get_all_products(self):
        """ دریافت تمامی محصولات """
        return self._repo.get_all()

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        """متد کمکی برای محاسبه درصد تغییر"""
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

        # ===== دریافت اطلاعات ===== #
        total_count = self._repo.get_total_count()
        status_counts = self._repo.get_status_breakdown()
        
        current_month_count = self._repo.get_count_by_date_range(start_of_current_month, now)
        last_month_count = self._repo.get_count_by_date_range(start_of_last_month, end_of_last_month)

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
            "configuration_breakdown": self._repo.get_quantity_status_breakdown()
        }
        
        return stats

# ========================================= #
# ========= Order Dashboard Logic ========= #
# ========================================= #
class OrderDashboardService:
    """
    سرویس اپلیکیشن داشبورد سفارشات.
    این سرویس حالا کاملاً به ریپازیتوری وابسته است و هیچ کوئری مستقیمی نمی‌پرسد.
    """
    # ===== کد وضعیتی که درخواستی برای سفارشات در انتظار تایید داریم ===== #
    PENDING_STATUS_CODE = 'PENDING_INITIAL_ADMIN' 

    def __init__(self):
        self._repo = OrderRepository()

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        """محاسبه درصد رشد/افت"""
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

        # ===== دریافت اطلاعات ===== #
        total_orders = self._repo.get_total_count()
        current_month_count = self._repo.get_count_by_date_range(start_of_current_month, now)
        last_month_count = self._repo.get_count_by_date_range(start_of_last_month, end_of_last_month)
        
        # ===== دریافت تعداد سفارشات در انتظار تایید ===== #
        pending_approval_count = self._repo.get_pending_initial_count(self.PENDING_STATUS_CODE)

        # ===== دریافت تغییرات ===== #
        raw_status_breakdown = self._repo.get_status_breakdown()
        
        # ===== تبدیل به شیء ===== #
        formatted_status_breakdown = [
            {"status": item['current_status__name'], "count": item['count']} 
            for item in raw_status_breakdown
        ]

        # ===== محاسبه منطق بیزینس ===== #
        growth_percentage = self._calculate_percentage_change(current_month_count, last_month_count)

        # ===== خروجی نهایی ===== #
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

# ========================================= #
# ========= User Dashboard Logic ========== #
# ========================================= #
class UserDashboardService:
    """
    سرویس اپلیکیشن مخصوص داشبورد کاربران.
    """
    def __init__(self):
        self._repo = UserRepository()

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        """متد کمکی برای محاسبه درصد رشد"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        دریافت آمار تجمیعی کاربران.
        """
        now = timezone.now()
        
        # ===== زمان ماهانه ===== #
        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== دریافت اطلاعات ===== #
        total_users = self._repo.get_total_count()
        
        # ===== دریافت اطلاعات کاربران جدید ماهانه ===== #
        new_users_this_month = self._repo.get_count_by_date_range(start_of_current_month, now)
        new_users_last_month = self._repo.get_count_by_date_range(start_of_last_month, end_of_last_month)
        
        # ===== آمار و وضعیت کاربران ===== #
        status_counts = self._repo.get_status_breakdown()
        role_counts_raw = self._repo.get_role_breakdown()
        type_counts = self._repo.get_customer_vs_staff_count()

        # ===== محاسبه تغییر ===== #
        growth_percentage = self._calculate_percentage_change(new_users_this_month, new_users_last_month)

        # ===== تبدیل به شیء ===== #
        formatted_role_breakdown = [
            {
                "role": item['role__name'],
                "slug": item['role__slug'],
                "count": item['count']
            } 
            for item in role_counts_raw
        ]

        # ===== خروجی نهایی ===== #
        return {
            "summary": {
                "total_users": total_users,
                "new_this_month": new_users_this_month,
                "new_last_month": new_users_last_month,
                "growth_percentage": growth_percentage,
                "growth_status": "positive" if growth_percentage >= 0 else "negative",
                "total_customers": type_counts['customer_count'],
                "total_staff": type_counts['staff_count']
            },
            "status_breakdown": {
                "active": status_counts['active'],
                "inactive": status_counts['inactive']
            },
            "role_breakdown": formatted_role_breakdown
        }

# ========================================= #
# ======= Financial Dashboard Logic ======= #
# ========================================= #
class FinancialDashboardService:
    """
    سرویس داشبورد مالی.
    وظیفه: محاسبات سود/زیان، رشد درآمد و فرمت‌دهی نمودارها.
    """
    def __init__(self):
        self._repo = OrderRepository()

    def _calculate_percentage_change(self, current: int, previous: int) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        change = ((current - previous) / previous) * 100
        return round(change, 2)

    def get_financial_statistics(self) -> Dict[str, Any]:
        now = timezone.now()
        
        # ===== بازه زمانی ماهانه ===== #
        start_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = start_of_current_month - relativedelta(months=1)
        end_of_last_month = start_of_current_month - relativedelta(seconds=1)

        # ===== دریافت اطلاعات ===== #
        total_revenue = self._repo.get_total_revenue()
        avg_order_value = self._repo.get_average_order_value()
        
        revenue_this_month = self._repo.get_revenue_by_date_range(start_of_current_month, now)
        revenue_last_month = self._repo.get_revenue_by_date_range(start_of_last_month, end_of_last_month)

        # ===== محاسبه تغییر ===== #
        revenue_growth = self._calculate_percentage_change(revenue_this_month, revenue_last_month)

        # ===== دریافت نمودار ===== #
        raw_chart_data = self._repo.get_daily_revenue_chart_data(days=30)
        
        # ===== تبدیل به شیء ===== #
        formatted_chart_data = [
            {
                "date": item['date'].strftime('%Y-%m-%d'),
                "amount": item['total'],
                "order_count": item['count']
            }
            for item in raw_chart_data
        ]

        # ===== خروجی نهایی ===== #
        return {
            "summary": {
                "total_revenue": total_revenue,
                "revenue_this_month": revenue_this_month,
                "revenue_last_month": revenue_last_month,
                "revenue_growth": revenue_growth,
                "revenue_status": "positive" if revenue_growth >= 0 else "negative",
                "average_order_value": avg_order_value
            },
            "chart_data": formatted_chart_data
        }
