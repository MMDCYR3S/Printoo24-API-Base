from rest_framework import serializers
from core.models import Order, OrderItem

class OrderItemCustomSerializer(serializers.Serializer):
    product_slug = serializers.CharField(required=False, allow_null=True) # به جای ID از Slug استفاده کردیم (هماهنگ با سرویس)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=0, required=False) # قیمت واحد دستی (اختیاری)
    selections = serializers.DictField(required=False, default=dict, help_text="""
    {
        "quantity": 1000,
        "size_id": 5,
        "option_value_ids": [101, 205],
        "custom_width": 300,
        "custom_height": 100,
        "has_design": true
    }
    """)
    note = serializers.CharField(required=False, allow_blank=True)

class CreateCustomOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, help_text="قیمت کل سفارش (دستی)")
    items = serializers.ListField(child=OrderItemCustomSerializer())

class OrderDashboardListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'customer_name', 'total_price', 'status_name', 'type', 'items_count', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    specifications = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'specifications', 'created_at']

    def get_specifications(self, obj):
        """
        تبدیل JSON ذخیره شده (obj.items) به فرمت خوانا برای داشبورد.
        """
        raw_data = obj.items or {}
        meta = raw_data.get('meta', {})
        options = raw_data.get('options', [])

        readable_options = []
        for opt in options:
            val_data = opt.get('value', {})
            val_label = val_data if isinstance(val_data, str) else val_data.get('label', 'N/A')
            readable_options.append({
                'name': opt.get('option_label', 'Unknown'),
                'value': val_label
            })

        return {
            'width': meta.get('width'),
            'height': meta.get('height'),
            'size_id': meta.get('size_id'),
            'has_design': meta.get('has_design'),
            'options': readable_options
        }

class OrderDashboardDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    items = OrderItemSerializer(source="order_item_order", many=True, read_only=True)
    
    address_detail = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'customer_name', 'total_price', 
            'status_name', 'type', 'items', 'address_detail', 
            'description', 'created_at'
        ]

    def get_address_detail(self, obj):
        if obj.address:
            return f"{obj.address.province.name}, {obj.address.city.name}, {obj.address.address}"
        return "آدرس حذف شده"
