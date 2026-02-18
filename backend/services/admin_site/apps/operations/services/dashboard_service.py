from typing import Dict, Any
from datetime import timedelta

from django.db.models import Count, Sum, Q, F, Avg, Value, DecimalField
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
from django.utils import timezone

from core.models import User, Order
from apps.order.models import OrderFinancialItem, OrderFinancialSheet, OrderFinancialReport
from apps.permissions import AppPermissionChecker

# ===== DASHBOARD SERVICE ===== #
class DashboardAppService:
    """
    سرویس متمرکز برای تولید آمار و ارقام داشبوردهای مدیریتی.
    """

    def __init__(self):
        self.now = timezone.now()
        self.start_of_month = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ============ DESIGNER DASHBOARD ============ #
    def get_designer_stats(self, user: User) -> Dict[str, Any]:
        """
        آمار مخصوص طراح: تمرکز روی وضعیت فایل‌ها و سفارشات منتسب شده.
        """
        base_qs = Order.objects.all()

        stats = base_qs.aggregate(
            total_assigned=Count('id'), 
            pending_review=Count('id', filter=Q(current_status__group__code='design', current_status__status_type='progress')),
            approved=Count('id', filter=Q(current_status__group__code='design', current_status__status_type='approve')),
            rejected=Count('id', filter=Q(current_status__group__code='design', current_status__status_type='reject')),
        )
        
        return stats
    
    # ============ OPERATIONS DASHBOARD (Print/Warehouse) ============ #
    def get_operational_stats(self, user: User, group_code: str, operation_type: str) -> Dict[str, Any]:
        """
        داشبورد مشترک برای انبار (Logistics) و چاپ (Production).
        group_code: کد گروه وضعیت (مثلا 'logistics') برای فیلتر سفارشات.
        operation_type: نوع عملیات مالی (مثلا 'logistics') برای فیلتر نمودار هزینه‌ها.
        """
        # ===== آمار وضعیت سفارشات ===== #
        active_orders = Order.objects.filter(current_status__group__code=group_code)
        
        kpi_stats = active_orders.aggregate(
            current_queue=Count('id', filter=Q(current_status__status_type='progress')),
            approved_count=Count('id', filter=Q(current_status__status_type='approve')),
            rejected_count=Count('id', filter=Q(current_status__status_type='reject')),
        )

        # ===== نمودار هزینه‌ها (Monthly Cost by Category) ===== #
        six_months_ago = self.now - timedelta(days=180)
        
        chart_data = OrderFinancialItem.objects.filter(
            report__sheet__is_locked=False,
            category__operation_type=operation_type,
            report__nature='cost',
            created_at__gte=six_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month', 'category__title').annotate(
            total_cost=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).order_by('month')

        return {
            "kpi": kpi_stats,
            "cost_chart": list(chart_data)
        }

    # ============ 3. FINANCIAL DASHBOARD (FIXED) ============ #
    def get_financial_stats(self, user: User) -> Dict[str, Any]:
        """
        رفع باگ KeyError: اطمینان از وجود کلیدها در aggregate.
        """
        AppPermissionChecker.check_has_permission(user, 'view_orderfinancialsheet')

        sheets_qs = OrderFinancialSheet.objects.all()
        
        # ===== KPI Aggregation ===== #
        # دقت کنید که نام کلیدها (مثل total_sheets_all) دقیقاً همان چیزی باشد که فراخوانی می‌کنیم
        aggregates = sheets_qs.aggregate(
            # ===== آمار کلی (All Time) ===== #
            total_sheets_all=Count('id'),
            total_revenue_all=Coalesce(Sum('total_revenue'), Value(0), output_field=DecimalField()),
            total_cost_all=Coalesce(Sum('final_total_cost'), Value(0), output_field=DecimalField()),
            
            # ===== آمار این ماه (This Month) ===== #
            total_sheets_month=Count('id', filter=Q(created_at__gte=self.start_of_month)),
            total_revenue_month=Coalesce(Sum('total_revenue', filter=Q(created_at__gte=self.start_of_month)), Value(0), output_field=DecimalField()),
            total_cost_month=Coalesce(Sum('final_total_cost', filter=Q(created_at__gte=self.start_of_month)), Value(0), output_field=DecimalField()),
            total_profit_month=Coalesce(Sum('net_profit', filter=Q(created_at__gte=self.start_of_month)), Value(0), output_field=DecimalField()),
            
            # ===== میانگین فروش ماه ===== #
            avg_revenue_month=Coalesce(Avg('total_revenue', filter=Q(created_at__gte=self.start_of_month)), Value(0), output_field=DecimalField()),
        )

        # ===== CHART 1 & 2: Daily Trend (اصلاح فیلتر nature روی report) ===== #
        daily_trend_qs = OrderFinancialReport.objects.filter(
            created_at__gte=self.start_of_month,
            is_approved=True
        ).annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            # report__nature استفاده می‌شود چون nature داخل خود مدل Report است
            revenue=Coalesce(Sum('items__amount', filter=Q(nature='revenue')), Value(0), output_field=DecimalField()),
            cost=Coalesce(Sum('items__amount', filter=Q(nature='cost')), Value(0), output_field=DecimalField())
        ).order_by('date')

        # ===== CHART 3: All Time Trend ===== #
        all_time_trend_qs = OrderFinancialReport.objects.filter(
            is_approved=True
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Coalesce(Sum('items__amount', filter=Q(nature='revenue')), Value(0), output_field=DecimalField()),
            cost=Coalesce(Sum('items__amount', filter=Q(nature='cost')), Value(0), output_field=DecimalField()),
            profit=Coalesce(Sum('items__amount', filter=Q(nature='revenue')), Value(0), output_field=DecimalField()) - 
                   Coalesce(Sum('items__amount', filter=Q(nature='cost')), Value(0), output_field=DecimalField())
        ).order_by('month')

        # ===== Top/Low Orders ===== #
        top_selling = sheets_qs.filter(created_at__gte=self.start_of_month).select_related('order').order_by('-total_revenue')[:5]
        worst_selling = sheets_qs.filter(created_at__gte=self.start_of_month, total_revenue__gt=0).select_related('order').order_by('total_revenue')[:5]

        # ===== Calculations for Reports ===== #
        total_reports_month = OrderFinancialReport.objects.filter(created_at__gte=self.start_of_month).count()
        
        total_sheets = aggregates.get('total_sheets_all', 0)
        total_reports_all = OrderFinancialReport.objects.count()
        
        avg_reports = round(total_reports_all / total_sheets, 1) if total_sheets > 0 else 0

        def serialize_sheet_list(qs):
            return [{'order_code': s.order.order_code, 'revenue': s.total_revenue, 'cost': s.final_total_cost} for s in qs]

        return {
            "metrics": {
                **aggregates,
                "total_reports_month": total_reports_month,
                "avg_reports_per_order": avg_reports
            },
            "top_selling_orders": serialize_sheet_list(top_selling),
            "low_selling_orders": serialize_sheet_list(worst_selling),
            "daily_chart_data": list(daily_trend_qs),
            "all_time_chart_data": list(all_time_trend_qs)
        }

    # ============ ADMIN DASHBOARD ============ #
    def get_admin_stats(self, user: User) -> Dict[str, Any]:
        """
        دید هلیکوپتری برای ادمین کل.
        اصلاحات: اضافه شدن هزینه کلی + ریز وضعیت‌ها.
        """
        if not user.is_superuser:
            return {} 

        # ===== آمار موجودیت‌ها ===== #
        counts = {
            "total_staff": User.objects.filter(is_staff=True).count(),
            "total_customers": User.objects.filter(is_staff=False).count(),
            "total_orders": Order.objects.count(),
            "total_orders_month": Order.objects.filter(created_at__gte=self.start_of_month).count(),
        }

        # ===== توزیع دقیق وضعیت سفارشات (Status Counts) ===== #
        status_distribution = Order.objects.values(
            'current_status__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # ===== خلاصه مالی کل سیستم (All Time) ===== #
        fin_aggregate = OrderFinancialReport.objects.filter(is_approved=True).aggregate(
            sys_rev=Coalesce(Sum('items__amount', filter=Q(nature='revenue')), Value(0), output_field=DecimalField()),
            sys_cost=Coalesce(Sum('items__amount', filter=Q(nature='cost')), Value(0), output_field=DecimalField())
        )
        system_revenue = fin_aggregate['sys_rev']
        system_cost = fin_aggregate['sys_cost']

        financials = {
            "system_revenue": system_revenue,
            "system_cost": system_cost,
            "system_profit": system_revenue - system_cost
        }

        # ===== نمودار سالانه (۱۲ ماه گذشته) ===== #
        twelve_months_ago = self.now - timedelta(days=365)
        twelve_months_ago = self.now - timedelta(days=365)
        annual_chart_qs = Order.objects.filter(
            created_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            order_count=Count('id', distinct=True),
            revenue=Coalesce(
                Sum('financial_sheet__reports__items__amount', 
                    filter=Q(financial_sheet__reports__nature='revenue', financial_sheet__reports__is_approved=True)
                ), 
                Value(0), output_field=DecimalField()
            ),
            cost=Coalesce(
                Sum('financial_sheet__reports__items__amount', 
                    filter=Q(financial_sheet__reports__nature='cost', financial_sheet__reports__is_approved=True)
                ), 
                Value(0), output_field=DecimalField()
            )
        ).order_by('month')

        # ===== نمودار ماه جاری ===== #
        daily_chart_qs = Order.objects.filter(
            created_at__gte=self.start_of_month
        ).annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            order_count=Count('id', distinct=True),
            revenue=Coalesce(
                Sum('financial_sheet__reports__items__amount', 
                    filter=Q(financial_sheet__reports__nature='revenue', financial_sheet__reports__is_approved=True)
                ), 
                Value(0), output_field=DecimalField()
            ),
            cost=Coalesce(
                Sum('financial_sheet__reports__items__amount', 
                    filter=Q(financial_sheet__reports__nature='cost', financial_sheet__reports__is_approved=True)
                ), 
                Value(0), output_field=DecimalField()
            )
        ).order_by('date')

        return {
            "entity_counts": counts,
            "status_distribution": list(status_distribution),
            "financial_summary": financials,
            "annual_chart": list(annual_chart_qs),
            "daily_chart": list(daily_chart_qs),
        }
