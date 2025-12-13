from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address

# ===== Product Summary Serializer ===== #
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug']

# ===== Order Item File Serializer ===== #
class OrderItemFileSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying final order files.
    """
    file_url = serializers.SerializerMethodField()
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)

    class Meta:
        model = OrderItemFile
        fields = ['id', 'requirement_name', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

# ===== Order Item Detail Serializer ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for order item details, extracting specs from JSON.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    design_files = OrderItemFileSerializer(source='files', many=True, read_only=True)
    
    specs = serializers.SerializerMethodField()
    pricing_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
             'id', 
             'product_name', 
             'quantity', 
             'price', 
             'specs', 
             'design_files',
             'pricing_breakdown'
         ]
    
    def get_specs(self, obj):
        """
        خواند و ساختاردهی مجدد جزئیات (ابعاد و آپشن‌های انتخاب شده)
        """
        raw_data = obj.items or {}

        width = raw_data.get('width')
        height = raw_data.get('height')
        
        detailed_options = [
            {
                "id": opt.get('id'),
                "option_name": opt.get('option_name', 'N/A'),
                "value_label": opt.get('value_label', 'N/A'),
                "price_impact": float(opt.get('price_impact', 0.0))
            }
            for opt in raw_data.get('options', [])
        ]

        return {
            "dimensions": f"{width or 'N/A'} x {height or 'N/A'} cm",
            "has_design": raw_data.get('has_design', False),
            "options": detailed_options, # <--- ارسال لیست دیکشنری
            "breakdown_present": bool(raw_data.get('price_breakdown'))
        }
    
    def get_pricing_breakdown(self, obj):
        # ... (بدون تغییر) ...
        raw_data = obj.items or {}
        return raw_data.get('price_breakdown', {})

# ===== Order Serializer (Main) ===== #
class OrderSerializer(serializers.ModelSerializer):
    """
    Main serializer for creating and viewing orders (Single Item Logic).
    """
    user = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(source='current_status.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    item_detail = serializers.SerializerMethodField()
    
    # Input field for Address ID (Write Only)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True,
        required=True,
        allow_null=False
    )
    
    # آدرس نمایش
    address = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True) # Max_digits باید بزرگتر باشد

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)

    class Meta:
        model = Order
        fields = [
            'id', 
            'order_code', # اضافه شد
            'user', 
            'status', 
            'type_display', 
            'total_price', 
            'address', 
            'address_id', 
            'created_at', 
            'item_detail' # <--- آیتم تکی
        ]
        read_only_fields = ['order_code']

    def get_address(self, obj):
        if obj.address:
            return str(obj.address)
        return "آدرس یافت نشد"

    def get_item_detail(self, obj):
        """ 🚨 FIX 2: دریافت آبجکت Item تکی و سریالایز کردن آن. """
        # فرض می‌کنیم OrderItem.order از related_name='order_item_order' استفاده می‌کند.
        item = obj.order_item_order.first() 
        if item:
            # از سریالایزر آیتم برای نمایش جزئیات استفاده می‌کنیم
            return OrderItemDetailSerializer(item, context=self.context).data
        return None
