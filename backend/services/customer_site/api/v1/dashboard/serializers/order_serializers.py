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

# ===== لیست سفارشات ===== #
class OrderListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', allow_null=True)
    status_name = serializers.CharField(source='current_status.name', allow_null=True)
    items_count = serializers.IntegerField(source='order_item_order.count', read_only=True)
    type_name = serializers.CharField(source='get_type_display', allow_null=True)

    class Meta:
        model = Order
        fields = ['id', 'username', 'recipient_name', 'recipient_phone', 'status_name', 'type_name', 'total_price', 'items_count', 'created_at']

# ===== سطح ۴: ساختار آپشن در سفارش (از JSON خوانده می‌شود) ===== #
class OrderItemOptionSnapshotSerializer(serializers.Serializer):
    """
    این سریالایزر وظیفه دارد دیکشنری داخل JSON را فرمت‌دهی کند.
    ساختار ذخیره شده: {'option_name': '...', 'value_label': '...', 'price_impact': ...}
    """
    option_id = serializers.IntegerField(source="id")
    name = serializers.CharField(source='option_name')
    value_option = serializers.CharField(source='value_label')
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0)

# ===== سطح ۳: ساختار کلی مشخصات آیتم (Specs) ===== #
class OrderItemSpecsSerializer(serializers.Serializer):
    """
    سریالایزر برای کل فیلد `items` در مدل.
    """
    width = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    has_design = serializers.BooleanField(default=True)
    
    options = OrderItemOptionSnapshotSerializer(many=True, required=False)

# ===== سطح ۲: آیتم سفارش ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_slug = serializers.CharField(source='product.slug')
    
    
    specifications = serializers.SerializerMethodField()
    
    files = OrderFileSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product_name', 
            'product_slug', 
            'name',          
            'description',   
            'quantity', 
            'price', 
            'specifications', 
            'files'
        ]

    def get_specifications(self, obj):
        """
        تبدیل JSON ذخیره شده به فرمت خوانا برای فرانت ادمین.
        """
        raw_data = obj.items or {}
        meta = raw_data.get('meta', {})
        options = raw_data.get('options', [])
        # ===== لیست ویژگی ها ===== #
        readable_options = []
        for opt in options:
            val_data = opt.get('value', {})
            val_label = val_data if isinstance(val_data, str) else val_data.get('label', 'N/A')
            # ===== ایجاد در لیست ===== #
            readable_options.append({
                'name': opt.get('option_label', 'Unknown'),
                'value': val_label
            })
            
        return {
            'width': meta.get('width'),
            'height': meta.get('height'),
            'has_design': meta.get('has_design'),
            'options': readable_options
        }

# ===== سطح ۱: جزئیات سفارش ===== #
class OrderDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    items = OrderItemDetailSerializer(source='order_item_order', many=True)
    address_detail = serializers.SerializerMethodField()
    current_status= serializers.CharField(source='current_status.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user_info',
            "recipient_name", 'recipient_phone',
            'company_name', 'address_detail',
            'current_status', 'total_price',
            'created_at', 'items'
        ]

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': f"{obj.user.customer_profile.first_name} {obj.user.customer_profile.last_name}"
        }
        
    def get_address_detail(self, obj):
        if not obj.address: return None
        return f"{obj.address.province.name} - {obj.address.city.name} - {obj.address.address}"

# ===== ایجاد سفارش (Input) ===== #
class AdminOrderCreateSerializer(serializers.Serializer):
    """
    سریالایزر ایجاد سفارش توسط ادمین.d
    اصلاح شده: افزودن فیلدهای اطلاعات گیرنده و آدرس
    """
    user_id = serializers.IntegerField()
    items = serializers.ListField(child=CartItemAddSimpleSerializer())
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, allow_null=True)
    
    # ===== فیلدهای آدرس و گیرنده ===== #
    address_id = serializers.IntegerField(required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recipient_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recipient_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        """
        بررسی اینکه حداقل یکی از موارد (شناسه آدرس) یا (آدرس متنی کامل) وجود داشته باشد.
        """
        if not attrs.get('address_id') and not attrs.get('full_address'):
            raise serializers.ValidationError("وارد کردن 'address_id' یا 'full_address' الزامی است.")
        return attrs

# ===== ویرایش سفارش (Input) ===== #
class AdminOrderUpdateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=Order.ORDER_TYPE, required=False)
