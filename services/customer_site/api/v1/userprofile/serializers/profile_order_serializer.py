from rest_framework import serializers
from core.models import Order, OrderItemDesignFile, OrderItem

# ===== Order Summary Serialzier ===== #
class OrderSummarySerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='order_status.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'type', 'status', 'total_price', 'created_at'
        ]
        
# ===== Deisgn File Serialzier ===== #
class DesignFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemDesignFile
        fields = ['id', 'file_url', 'created_at']

    def get_file_url(self, obj):
        if obj.file and obj.file.file:
            return obj.file.file.url
        return None

# ===== Order Item Detail Serialzier ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    design_files = DesignFileSerializer(source='order_item_design_file_order_item', many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'items', 'design_files']

# ===== Order Detail Serialzier ===== #
class OrderDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='order_status.name', read_only=True)
    items = OrderItemDetailSerializer(source='order_item_order', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'type', 'status', 'total_price', 'address', 
            'created_at', 'items'
        ]
        