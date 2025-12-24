from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, Product, Address

# ===== Product Summary Serializer ===== #
class ProductSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug']

# ===== Order Item File Serializer ===== #
class OrderItemFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(help_text="لینک دانلود فایل")
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
    product_name = serializers.CharField(source='product.name', read_only=True)
    design_files = OrderItemFileSerializer(source='files', many=True, read_only=True)
    
    # ===== فیلدهای محاسباتی ===== #
    specs = serializers.SerializerMethodField(help_text="مشخصات فنی استخراج شده از JSON (ابعاد، متریال، آپشن‌ها)")
    pricing_breakdown = serializers.SerializerMethodField(help_text="جزئیات ریز قیمت")

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
        استخراج و فرمت‌دهی اطلاعات فنی از JSON Field (item.items)
        """
        raw_data = obj.items or {}
        # ===== استخراج اطلاعات فنی ===== #
        meta = raw_data.get('meta', {})
        width = meta.get('width') or raw_data.get('width')
        height = meta.get('height') or raw_data.get('height')
        has_design = meta.get('has_design', raw_data.get('has_design', False))
        # ===== دریافت ویژگی ها ===== #
        raw_options = raw_data.get('options', [])
        detailed_options = []
        
        for opt in raw_options:
            label_display = "N/A"
            price_impact = 0.0
            # ===== اگر انتخاب تکی باشد ===== #
            if opt.get('type') == 'selection':
                val_data = opt.get('value', {})
                label_display = val_data.get('label', 'N/A')
                price_impact = val_data.get('price', 0.0)
            # ===== اگر انتخاب چندتایی باشد ===== #
            elif opt.get('type') == 'multi_selection':
                vals = opt.get('values', [])
                label_display = ", ".join([v.get('label', '') for v in vals])
                price_impact = sum([v.get('price', 0.0) for v in vals])
            # ===== اگر انتخاب عدد/متن باشد ===== #
            elif opt.get('type') == 'raw':
                label_display = str(opt.get('value', 'N/A'))
                price_impact = opt.get('price', 0.0)
            # ===== ایجاد مقادیر در لیست مورد نظر ===== #
            detailed_options.append({
                "option_name": opt.get('option_label', 'N/A'),
                "value_label": label_display,
                "price_impact": price_impact
            })
        # ===== بازگردانی لیست ===== #
        return {
            "dimensions": f"{width} x {height} cm" if width and height else "استاندارد",
            "has_design": has_design,
            "options": detailed_options
        }
    
    def get_pricing_breakdown(self, obj):
        raw_data = obj.items or {}
        return raw_data.get('meta', {}).get('price_breakdown', {})

# ===== Order Serializer (Main) ===== #
class OrderSerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی سفارش.
    هم برای ایجاد (Checkout) و هم برای نمایش استفاده می‌شود.
    """
    user = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(source='current_status.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    # ===== جزئیات آیتم (چون سفارشات فعلی تک آیتمی هستند) ===== #
    item_detail = serializers.SerializerMethodField()
    
    # ===== ورودی‌ها ===== #
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        write_only=True,
        required=True,
        help_text="شناسه آدرس انتخاب شده"
    )
    
    type = serializers.ChoiceField(
        choices=Order.ORDER_TYPE,
        default='2',
        write_only=True,
        help_text="نوع سفارش (۱: معمولی، ۲: اختصاصی)"
    )
    
    # ===== خروجی‌ها (Read Only) ===== #
    address = serializers.SerializerMethodField(read_only=True, help_text="متن آدرس برای نمایش")
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)

    class Meta:
        model = Order
        fields = [
            'id', 
            'order_code',
            'user', 
            'status', 
            'type', # ورودی
            'type_display', 
            'total_price', 
            'address', # خروجی
            'address_id', # ورودی
            'created_at', 
            'item_detail'
        ]
        read_only_fields = ['order_code', 'created_at']

    def get_address(self, obj):
        if obj.address:
            return str(obj.address) # یا استفاده از AddressSerializer برای جزئیات بیشتر
        return "آدرس حذف شده"

    def get_item_detail(self, obj):
        item = obj.order_item_order.first() 
        if item:
            return OrderItemDetailSerializer(item, context=self.context).data
        return None
