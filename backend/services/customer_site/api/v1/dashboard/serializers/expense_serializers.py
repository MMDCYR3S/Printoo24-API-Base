from rest_framework import serializers
from core.models import Expense, Order

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

class UnlockedInvoiceOrderSerializer(serializers.ModelSerializer):
    """سریالایزر خلاصه برای نمایش اطلاعات هویتی و اقلام سفارشات با فاکتور قفل‌نشده"""
    
    customer_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    product_names = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'order_code',
            'customer_name',
            'phone_number',
            'product_names',
        ]
        read_only_fields = fields

    def get_customer_name(self, obj):
        if obj.user and hasattr(obj.user, 'customer_profile') and obj.user.customer_profile:
            return obj.user.customer_profile.fullname()
        return obj.recipient_name or "کاربر مهمان"

    def get_phone_number(self, obj):
        return obj.recipient_phone or (obj.user.phone_number if obj.user else None)

    def get_product_names(self, obj):
        name = ''
        for item in obj.order_item_order.all():
            if item.name:
                name = item.name
            elif item.product:
                name = item.product.name
        return name
