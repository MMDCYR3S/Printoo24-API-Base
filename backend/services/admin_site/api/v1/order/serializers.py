from rest_framework import serializers
from core.models import Order, OrderItem

class OrderItemCustomSerializer(serializers.Serializer):
    product_slug = serializers.CharField(required=False, allow_null=True)
    
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text="نام آیتم (در صورت عدم محصول الزامی است)")
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    quantity = serializers.IntegerField(default=1, min_value=1)
    item_price = serializers.DecimalField(
        max_digits=14, 
        decimal_places=0, 
        required=False, 
        allow_null=True, 
        help_text="قیمت واحد یا کل این آیتم (در صورت عدم محصول الزامی است)"
    )
    selections = serializers.JSONField(
        required=False, 
        default=dict,
        help_text=(
            "داده‌های فنی و اضافه آیتم. "
            "برای محصولی: گزینه‌های انتخابی (مثلاً سایز، رنگ). "
            "برای دستی: هر اطلاعات متنی/فنی که ادمین مد نظر دارد (مثلاً جنس کاغذ، لینک فایل، توضیحات فنی)."
        )
    )
    note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        product_slug = attrs.get('product_slug')
        name = attrs.get('name')
        price = attrs.get('item_price')

        # ===== اعتبارسنجی شرطی ===== #
        if not product_slug:
            if not name:
                raise serializers.ValidationError({"name": "زمانی که محصول انتخاب نمی‌شود، وارد کردن نام آیتم الزامی است."})
            if price is None:
                raise serializers.ValidationError({"item_price": "زمانی که محصول انتخاب نمی‌شود، وارد کردن قیمت آیتم الزامی است."})
        if 'selections' in attrs and not isinstance(attrs['selections'], dict):
             raise serializers.ValidationError({"selections": "باید فرمت آبجکت/دیکشنری باشد."})
        return attrs

class CreateCustomOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False, allow_null=True)
    address_id = serializers.IntegerField(required=False, allow_null=True)
    recipient_name = serializers.CharField(required=False, allow_null=True)
    recipient_phone = serializers.CharField(required=False, allow_null=True)
    company_name = serializers.CharField(required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, help_text="قیمت کل سفارش (دستی)")
    items = serializers.ListField(child=OrderItemCustomSerializer())

class OrderDashboardListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='current_status.name', read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'recipient_name', 'recipient_phone',
            'total_price', 'status_display', 'type_display',
            'items_count', 'created_at'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    # ===== تغییر ۱: هندل کردن نام محصول برای حالت دستی ===== #
    name_display = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'name_display', 'quantity', 'price', 'specifications', 'created_at']

    def get_name_display(self, obj):
        """ اولویت با نام محصول است، اگر نبود از نام دستی استفاده می‌کند """
        if obj.product:
            return obj.product.name
        return obj.name or "آیتم بدون نام"
    
    def get_specifications(self, obj):
        """
        هوشمندسازی خروجی: هم برای ساختار محصول (system) و هم ساختار دستی (admin) کار می‌کند.
        """
        raw_data = obj.items or {}
        
        # ===== ساختار پیش فرض ===== #
        response = {
            'dimensions': {}, 
            'options': [], 
            'attributes': [] 
        }
        
        # ===== سایز دلخواه محصولات ===== #
        width = raw_data.get('width') or raw_data.get('meta', {}).get('width')
        height = raw_data.get('height') or raw_data.get('meta', {}).get('height')
        
        if width or height:
            response['dimensions'] = {'width': width, 'height': height}

        # ===== ویژگی های مربوط به محصولات ===== #
        system_options = raw_data.get('options', [])
        if isinstance(system_options, list):
            for opt in system_options:
                if isinstance(opt, dict):
                    val_data = opt.get('value', {})
                    val_label = val_data if isinstance(val_data, str) else val_data.get('label', 'N/A')
                    
                    response['options'].append({
                        'name': opt.get('option_label', opt.get('name', 'Unknown')),
                        'value': val_label
                    })

        # ===== استخراج داده های سمت ادمین به صورت دستی و اختصاصی ===== #
        ignored_keys = {'width', 'height', 'options', 'meta', 'size_id', 'has_design', 'file_info'}
        
        # ===== اگر دیتای متا وجود داشت ===== #
        meta_data = raw_data.get('meta', {})
        if isinstance(meta_data, dict):
            for k, v in meta_data.items():
                if k not in ['width', 'height']: 
                    pass 

        for key, value in raw_data.items():
            if key in ignored_keys:
                continue
            
            display_value = value
            if isinstance(value, (dict, list)):
                display_value = str(value)
            
            response['attributes'].append({
                'label': key.replace('_', ' ').title(),
                'value': display_value
            })

        return response

class OrderDashboardDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_name = serializers.CharField(read_only=True)
    recipient_phone = serializers.CharField(read_only=True)
    company_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    status_name = serializers.CharField(source='current_status.name', read_only=True)
    items = OrderItemSerializer(source="order_item_order", many=True, read_only=True)
    
    address_detail = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'customer_name',
            'recipient_name', 'recipient_phone', 'company_name',
            'full_address' ,'total_price',  'status_name',
            'type', 'items', 'address_detail', 'created_at'
        ]

    def get_address_detail(self, obj):
        if obj.address:
            return f"{obj.address.province.name}, {obj.address.city.name}, {obj.address.address}"
        else:
            return None

# ===== UPDATE SERIALIZER ===== #
class OrderDashboardUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = [
            'type', 'full_address', 'total_price'
        ]
