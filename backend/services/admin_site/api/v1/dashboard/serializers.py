from rest_framework import serializers
from core.models import Order, OrderItem

class OrderItemCustomSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=0) # قیمت واحد
    features = serializers.JSONField(required=False) # جزئیات فنی
    note = serializers.CharField(required=False, allow_blank=True)

class CreateCustomOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    description = serializers.CharField(required=False)
    generate_invoice = serializers.BooleanField(default=True)
    items = serializers.ListField(child=OrderItemCustomSerializer())

class OrderDashboardListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'customer_name', 'total_price', 'status_name', 'type', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    status_name = serializers.CharField(source='status.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity', 'status_name', 'items', 'created_at']

class OrderDashboardDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    items = OrderItemSerializer(source="order_item_order" ,many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'customer_name', 'total_price', 'status_name', 'type', 'items', 'created_at']
