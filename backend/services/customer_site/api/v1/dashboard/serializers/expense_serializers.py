from rest_framework import serializers
from core.financial.models import Expense

# ========== EXPENSE SERIALIZERS ========== #
class ExpenseSerializer(serializers.ModelSerializer):
    """سریالایزر پایه برای هزینه‌ها"""
    
    order_code = serializers.CharField(source='order.order_code', read_only=True, allow_null=True)
    
    class Meta:
        model = Expense
        fields = [
            'id',
            'order',
            'order_code',
            'name',
            'amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'order_code']

class ExpenseCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد هزینه"""
    
    class Meta:
        model = Expense
        fields = ['order', 'name', 'amount']
    
    def validate_amount(self, value):
        """اعتبارسنجی مبلغ"""
        if value <= 0:
            raise serializers.ValidationError("مبلغ باید بزرگتر از صفر باشد.")
        return value

class ExpenseUpdateSerializer(serializers.ModelSerializer):
    """سریالایزر بروزرسانی هزینه"""
    
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'order']

class ExpenseStatsSerializer(serializers.Serializer):
    """سریالایزر آمار هزینه‌ها"""
    
    total_expenses = serializers.IntegerField()
    daily_expenses = serializers.IntegerField()
    monthly_expenses = serializers.IntegerField()
    yearly_expenses = serializers.IntegerField()
    
    daily_profit = serializers.IntegerField()
    monthly_profit = serializers.IntegerField()
    yearly_profit = serializers.IntegerField()
