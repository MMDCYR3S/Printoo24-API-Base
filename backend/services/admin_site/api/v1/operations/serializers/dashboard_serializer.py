from rest_framework import serializers

# ===== DESIGNER ===== #
class DesignerDashboardSerializer(serializers.Serializer):
    total_assigned = serializers.IntegerField()
    pending_review = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()

# ===== OPERATIONAL (Chart Data) ===== #
class CostChartItemSerializer(serializers.Serializer):
    month = serializers.DateTimeField(format="%Y-%m")
    category__title = serializers.CharField() # نام دسته‌بندی
    total_cost = serializers.DecimalField(max_digits=20, decimal_places=0)

class OperationalKpiSerializer(serializers.Serializer):
    current_queue = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()

class OperationalDashboardSerializer(serializers.Serializer):
    kpi = OperationalKpiSerializer()
    cost_chart = serializers.ListField(child=CostChartItemSerializer())

# ===== FINANCIAL SERIALIZERS ===== #
class FinancialMetricsSerializer(serializers.Serializer):
    total_sheets_all = serializers.IntegerField()
    total_revenue_all = serializers.DecimalField(max_digits=20, decimal_places=0)
    total_cost_all = serializers.DecimalField(max_digits=20, decimal_places=0)
    total_sheets_month = serializers.IntegerField()
    total_revenue_month = serializers.DecimalField(max_digits=20, decimal_places=0)
    total_cost_month = serializers.DecimalField(max_digits=20, decimal_places=0)
    avg_revenue_month = serializers.DecimalField(max_digits=20, decimal_places=0)
    total_reports_month = serializers.IntegerField()
    avg_reports_per_order = serializers.FloatField()

class DailyChartDataSerializer(serializers.Serializer):
    """ اصلاح: استفاده از DateField """
    date = serializers.DateField() # قبلا DateTimeField بود
    revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    cost = serializers.DecimalField(max_digits=20, decimal_places=0)

class AllTimeChartDataSerializer(serializers.Serializer):
    """ اصلاح: استفاده از DateField """
    month = serializers.DateField() # قبلا DateTimeField بود
    revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    cost = serializers.DecimalField(max_digits=20, decimal_places=0)
    profit = serializers.DecimalField(max_digits=20, decimal_places=0)

class OrderSummarySerializer(serializers.Serializer):
    order_code = serializers.CharField()
    revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    cost = serializers.DecimalField(max_digits=20, decimal_places=0)

class FinancialDashboardSerializer(serializers.Serializer):
    metrics = FinancialMetricsSerializer()
    top_selling_orders = serializers.ListField(child=OrderSummarySerializer())
    low_selling_orders = serializers.ListField(child=OrderSummarySerializer())
    daily_chart_data = serializers.ListField(child=DailyChartDataSerializer(), help_text="دیتای روزانه برای رسم نمودارهای خطی درآمد و هزینه در ماه جاری")
    all_time_chart_data = serializers.ListField(child=AllTimeChartDataSerializer(), help_text="دیتای ماهانه برای رسم نمودار میله‌ای/خطی مقایسه درآمد، هزینه و سود در کل ادوار")

# ===== ADMIN ===== #
class AdminFinancialSummarySerializer(serializers.Serializer):
    """ خلاصه مالی کل سیستم """
    system_revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    system_cost = serializers.DecimalField(max_digits=20, decimal_places=0)
    system_profit = serializers.DecimalField(max_digits=20, decimal_places=0)


# ===== ADMIN - CHARTS ===== #
class AdminAnnualChartItemSerializer(serializers.Serializer):
    """ ساختار دیتای نمودار سالانه ادمین """
    month = serializers.DateField()
    order_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    cost = serializers.DecimalField(max_digits=20, decimal_places=0)

class AdminDailyChartItemSerializer(serializers.Serializer):
    """ ساختار دیتای نمودار روزانه ادمین """
    date = serializers.DateField()
    order_count = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=20, decimal_places=0)
    cost = serializers.DecimalField(max_digits=20, decimal_places=0)

# ===== آپدیت سریالایزر اصلی داشبورد ادمین ===== #
class AdminDashboardSerializer(serializers.Serializer):
    entity_counts = serializers.DictField()
    status_distribution = serializers.ListField()
    financial_summary = AdminFinancialSummarySerializer()
    annual_chart = serializers.ListField(
        child=AdminAnnualChartItemSerializer(), 
        help_text="دیتای ۱۲ ماه گذشته برای رسم نمودار سالانه"
    )
    daily_chart = serializers.ListField(
        child=AdminDailyChartItemSerializer(), 
        help_text="دیتای روزانه برای رسم نمودار ماه جاری"
    )
