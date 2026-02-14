from rest_framework import serializers
from core.models import OrderStateLog

# ===== LOG ROW SERIALIZER ===== #
class OrderStateLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)
    from_status_title = serializers.CharField(source='from_status.name', read_only=True, allow_null=True)
    to_status_title = serializers.CharField(source='to_status.name', read_only=True)
    
    class Meta:
        model = OrderStateLog
        fields = [
            'id', 
            'actor_name', 
            'from_status_title', 
            'to_status_title', 
            'description',
            'created_at'
        ]

# ===== MAIN RESPONSE SERIALIZER ===== #
class OrderHistoryResponseSerializer(serializers.Serializer):
    """
    ساختار خروجی برای نمایش تاریخچه سفارش به ادمین.
    شامل خلاصه سفارش و لیست لاگ‌ها.
    """
    order_id = serializers.IntegerField(source='order.id')
    order_code = serializers.CharField(source='order.order_code')
    current_status = serializers.CharField(source='order.current_status.name')
    
    logs = OrderStateLogSerializer(many=True)

# ===== GLOBAL LOG LIST SERIALIZER ===== #
class GlobalOrderLogSerializer(OrderStateLogSerializer):
    """
    سریالایزر برای لیست کلی لاگ‌ها.
    تفاوت با قبلی: شامل اطلاعات خلاصه سفارش است (چون در لیست کلی نمی‌دانیم لاگ مال کدام سفارش است)
    """
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    order_title = serializers.CharField(source='order.__str__', read_only=True)

    class Meta(OrderStateLogSerializer.Meta):
        fields = OrderStateLogSerializer.Meta.fields + ['order_id', 'order_code', 'order_title']
