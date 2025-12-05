from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile
from api.v1.dashboard.serializers import CartItemAddSimpleSerializer

# ===== فایل‌های آیتم ===== #
class OrderFileSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)
    type_name = serializers.CharField(source='requirement.spec.name', read_only=True)
    
    class Meta:
        model = OrderItemFile
        fields = ['id', 'type_name', 'file_url', 'uploaded_at']

# ===== آیتم سفارش (Nested) ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    details = serializers.JSONField(source='items')
    files = OrderFileSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'details', 'files']

# ===== لیست سفارشات ===== #
class OrderListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    status_name = serializers.CharField(source='order_status.name')
    items_count = serializers.IntegerField(source='order_item_order.count', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'username', 'status_name', 'total_price', 'items_count', 'created_at']

# ===== سطح ۴: ساختار آپشن در سفارش (از JSON خوانده می‌شود) ===== #
class OrderItemOptionSnapshotSerializer(serializers.Serializer):
    """
    این سریالایزر وظیفه دارد دیکشنری داخل JSON را فرمت‌دهی کند.
    ساختار ذخیره شده: {'option_name': '...', 'value_label': '...', 'price_impact': ...}
    """
    option_id = serializers.IntegerField(source="id")
    name = serializers.CharField(source='title')
    value_option = serializers.CharField(source='value')
    price_impact = serializers.DecimalField(source='price', max_digits=14, decimal_places=0)

# ===== سطح ۳: ساختار کلی مشخصات آیتم (Specs) ===== #
class OrderItemSpecsSerializer(serializers.Serializer):
    """
    سریالایزر برای کل فیلد `items` در مدل.
    """
    width = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    material_name = serializers.SerializerMethodField()
    has_design = serializers.BooleanField(default=True)
    
    options = OrderItemOptionSnapshotSerializer(many=True, required=False)

    def get_material_name(self, obj):
        material_data = obj.get('material', {})
        if isinstance(material_data, dict):
            return material_data.get('name')
        return str(material_data)

# ===== سطح ۲: آیتم سفارش ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_slug = serializers.CharField(source='product.slug')
    
    specifications = serializers.SerializerMethodField()
    
    files = OrderFileSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_slug', 'quantity', 'price', 'specifications', 'files']

    def get_specifications(self, obj):
        """
        تبدیل JSON خام (obj.items) به ساختار استاندارد سریالایزر.
        """
        if not obj.items:
            return None
        return OrderItemSpecsSerializer(obj.items).data

# ===== سطح ۱: جزئیات سفارش ===== #
class OrderDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    items = OrderItemDetailSerializer(source='order_item_order', many=True)
    address_detail = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user_info', 'items', 'address_detail', 'status_info', 'total_price', 'created_at']

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': f"{obj.user.customer_profile.first_name} {obj.user.customer_profile.last_name}"
        }
        
    def get_address_detail(self, obj):
        if not obj.address: return None
        return f"{obj.address.province.name}, {obj.address.city.name}, {obj.address.address}"

    def get_status_info(self, obj):
        return {'id': obj.order_status.id, 'name': obj.order_status.name}

# ===== ایجاد سفارش (Input) ===== #
class AdminOrderCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False)
    items = serializers.ListField(child=CartItemAddSimpleSerializer())

# ===== ویرایش سفارش (Input) ===== #
class AdminOrderUpdateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=Order.ORDER_TYPE, required=False)
