from rest_framework import serializers

# ========== PRODUCT SERIALIZERS ========== #
class DashboardSummarySerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    added_this_month = serializers.IntegerField()
    added_last_month = serializers.IntegerField()
    growth_percentage = serializers.FloatField()
    growth_status = serializers.CharField()

class StatusBreakdownSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    active_percentage = serializers.FloatField()

class ConfigBreakdownSerializer(serializers.Serializer):
    with_quantity = serializers.IntegerField()
    without_quantity = serializers.IntegerField()

class ProductDashboardStatsSerializer(serializers.Serializer):
    """
    سریالایزر اصلی که کل ساختار جیسون را شکل می‌دهد
    """
    summary = DashboardSummarySerializer()
    status_breakdown = StatusBreakdownSerializer()
    configuration_breakdown = ConfigBreakdownSerializer()
    
# ========== ORDER SERIALIZERS ========== #
class OrderSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    pending_approval_count = serializers.IntegerField(help_text="تعداد سفارشات در انتظار تایید اولیه")
    added_this_month = serializers.IntegerField()
    added_last_month = serializers.IntegerField()
    growth_percentage = serializers.FloatField()
    growth_status = serializers.CharField()

class OrderStatusBreakdownItemSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()

class OrderDashboardStatsSerializer(serializers.Serializer):
    """
    سریالایزر اصلی آمار داشبورد سفارشات
    """
    summary = OrderSummarySerializer()
    status_breakdown = OrderStatusBreakdownItemSerializer(many=True)

# ========== USER SERIALIZERS ========== #
class UserSummarySerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    new_this_month = serializers.IntegerField()
    new_last_month = serializers.IntegerField()
    growth_percentage = serializers.FloatField()
    growth_status = serializers.CharField()
    total_customers = serializers.IntegerField()
    total_staff = serializers.IntegerField()

class UserStatusBreakdownSerializer(serializers.Serializer):
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()

class UserRoleBreakdownSerializer(serializers.Serializer):
    role = serializers.CharField()
    slug = serializers.CharField()
    count = serializers.IntegerField()

class UserDashboardStatsSerializer(serializers.Serializer):
    """
    سریالایزر اصلی آمار داشبورد کاربران
    """
    summary = UserSummarySerializer()
    status_breakdown = UserStatusBreakdownSerializer()
    role_breakdown = UserRoleBreakdownSerializer(many=True)
    
# ========= FINANCIAL SERIALIZERS ========== #
class FinancialSummarySerializer(serializers.Serializer):
    total_revenue = serializers.IntegerField()
    total_paid = serializers.IntegerField()
    outstanding = serializers.IntegerField()
    revenue_this_month = serializers.IntegerField()
    revenue_last_month = serializers.IntegerField()
    paid_this_month = serializers.IntegerField()
    revenue_growth = serializers.FloatField()
    revenue_status = serializers.CharField()
    average_invoice_value = serializers.IntegerField()

class FinancialChartItemSerializer(serializers.Serializer):
    date = serializers.CharField(help_text="Format: YYYY-MM-DD")
    amount = serializers.IntegerField()
    paid = serializers.IntegerField()
    order_count = serializers.IntegerField()
class FinancialDashboardStatsSerializer(serializers.Serializer):
    summary = FinancialSummarySerializer()
    chart_data = FinancialChartItemSerializer(many=True, help_text="داده‌های ۳۰ روز گذشته برای نمودار")
    

# ========== EXPENSE SERIALIZERS ========== #
class ExpenseSummarySerializer(serializers.Serializer):
    total_expenses = serializers.IntegerField()
    daily_expenses = serializers.IntegerField()
    monthly_expenses = serializers.IntegerField()
    yearly_expenses = serializers.IntegerField()

class ProfitSummarySerializer(serializers.Serializer):
    daily_profit = serializers.IntegerField()
    monthly_profit = serializers.IntegerField()
    yearly_profit = serializers.IntegerField()

class CombinedDashboardStatsSerializer(serializers.Serializer):
    products = ProductDashboardStatsSerializer()
    orders = OrderDashboardStatsSerializer()
    users = UserDashboardStatsSerializer()
    financial = FinancialDashboardStatsSerializer()
    expenses = ExpenseSummarySerializer()
    profit = ProfitSummarySerializer()
