from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile
from api.v1.dashboard.serializers import CartItemAddSimpleSerializer

# ===== فایل‌های آیتم ===== #
class OrderFileSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)
    
    class Meta:
        model = OrderItemFile
        fields = ['id', 'file_url', 'uploaded_at']

class ItemSelectionInputSerializer(serializers.Serializer):
    """
    مشخصات فنی آیتم سفارش.
    نکته: یا باید size_id ارسال شود (سایز استاندارد) 
    یا custom_width/height (سایز دلخواه).
    """
    # ===== انتخاب سایز استاندارد ===== #
    size_id = serializers.IntegerField(required=False, allow_null=True, help_text="شناسه سایز استاندارد (ProductSize ID)")
    
    # ===== سایز دلخواه (اگر محصول اجازه دهد) ===== #
    custom_width = serializers.FloatField(required=False, help_text="عرض دلخواه (cm)")
    custom_height = serializers.FloatField(required=False, help_text="ارتفاع دلخواه (cm)")
    
    # ===== سایر آپشن‌ها ===== #
    option_value_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        help_text="لیست شناسه مقادیر آپشن (ProductOptionValue ID)"
    )
    
    # ===== فیلدهای متنی آیتم ===== #
    name = serializers.CharField(required=False, help_text="نام اختصاصی برای این آیتم (مثلا: کارت ویزیت آقای ...)")
    description = serializers.CharField(required=False, help_text="توضیحات تکمیلی")
    
    # ===== تیراژ (می‌تواند اینجا یا در سطح بالاتر باشد) ===== #
    quantity = serializers.IntegerField(required=False, default=1)

    def validate(self, attrs):
        """
        قانون: نمی‌توان همزمان سایز استاندارد و سایز دلخواه داشت.
        """
        if attrs.get('size_id') and (attrs.get('custom_width') or attrs.get('custom_height')):
            raise serializers.ValidationError("انتخاب همزمان سایز استاندارد و سایز دلخواه مجاز نیست.")
        return attrs

# ===== لیست سفارشات ===== #
class OrderListSerializer(serializers.ModelSerializer):
    """ لیست خلاصه برای جدول دیتاگرید """
    username = serializers.CharField(source='user.username', allow_null=True)
    status_name = serializers.CharField(source='current_status.name', allow_null=True)
    items_count = serializers.IntegerField(source='order_item_order.count', read_only=True)
    type_display = serializers.CharField(source='get_type_display', allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'username', 
            'recipient_name', 'recipient_phone', 
            'status_name', 'type_display', 
            'total_price', 'items_count', 'created_at'
        ]

class AdminItemInputSerializer(serializers.Serializer):
    """
    ساختار ورودی برای آیتم‌ها (هم در ایجاد و هم در ویرایش).
    """
    id = serializers.IntegerField(required=False, help_text="برای ویرایش آیتم موجود الزامی است")
    product_slug = serializers.CharField(required=False, help_text="برای ایجاد آیتم جدید الزامی است")
    
    # ===== استفاده از سریالایزر تو در تو برای داکیومنت بهتر ===== #
    selections = ItemSelectionInputSerializer(required=False, help_text="مشخصات فنی و سایز")

    item_price = serializers.DecimalField(required=False, max_digits=14, decimal_places=0, help_text="قیمت دستی (Override)")
    
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    admin_note = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get('id') and not attrs.get('product_slug'):
            raise serializers.ValidationError("برای آیتم جدید، ارسال product_slug الزامی است.")
        return attrs
    
class AdminOrderCreateSerializer(serializers.Serializer):
    """ ایجاد سفارش جدید """
    user_id = serializers.IntegerField(required=False, allow_null=True)
    # ===== اطلاعات مشتری===== #
    recipient_name = serializers.CharField(required=False, allow_blank=True, max_length=255, help_text="نام تحویل گیرنده")
    recipient_phone = serializers.CharField(required=False, allow_blank=True, max_length=20, help_text="شماره تماس گیرنده")
    company_name = serializers.CharField(required=False, allow_blank=True, max_length=150, help_text="نام شرکت/مجموعه")
    # ===== آدرس و آیتم ها ===== #
    address_id = serializers.IntegerField(required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    items = serializers.ListField(child=AdminItemInputSerializer())
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False)
    
    def validate(self, attrs):
        user_id = attrs.get('user_id')
        addr_id = attrs.get('address_id')
        full_addr = attrs.get('full_address')
        rec_name = attrs.get('recipient_name')
        rec_phone = attrs.get('recipient_phone')

        # ===== باید نام باشه اگر که کاربر مهمانه ===== #
        if not user_id:
            if not rec_name or not rec_phone:
                raise serializers.ValidationError("برای سفارش مهمان (بدون کاربر)، وارد کردن نام و شماره تماس گیرنده الزامی است.")
            
            # ===== نباید همزمان دوتاش باشه ===== #
            if addr_id:
                raise serializers.ValidationError("سفارش مهمان نمی‌تواند آدرس ذخیره شده (address_id) داشته باشد. لطفاً از full_address استفاده کنید.")

        # ===== حداقل یک آدرس باید باشه ===== #
        if not addr_id and not full_addr:
            raise serializers.ValidationError("وارد کردن آدرس (full_address) یا انتخاب آدرس (address_id) الزامی است.")
            
        return attrs

class AdminOrderUpdateSerializer(serializers.Serializer):
    """
    ویرایش جامع سفارش.
    تمام فیلدها اختیاری هستند تا Partial Update ممکن شود.
    """
    # ===== اطلاعات تماس و آدرس ===== #
    recipient_name = serializers.CharField(required=False)
    recipient_phone = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    address_id = serializers.IntegerField(required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_blank=True)
    
    # ===== اطلاعات مالی ===== #
    total_price = serializers.DecimalField(required=False, max_digits=14, decimal_places=0, allow_null=True)
    type = serializers.ChoiceField(choices=Order.ORDER_TYPE, required=False)
    
    # ===== مدیریت آیتم ها ===== #
    items = serializers.ListField(child=AdminItemInputSerializer(), required=False)

class OrderStatusUpdateSerializer(serializers.Serializer):
    """ فقط برای تغییر وضعیت """
    status_id = serializers.IntegerField()

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
    """
    نمایش جزئیات آیتم برای ادمین.
    """
    product_name = serializers.CharField(source='product.name')
    product_slug = serializers.CharField(source='product.slug')
    specifications = serializers.SerializerMethodField()
    files = OrderFileSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(source='price', max_digits=15, decimal_places=0)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_slug', 
            'name', 'description', 'admin_note',
            'quantity', 'total_price',
            'specifications', 'files', 'status'
        ]

    def get_specifications(self, obj):
        """ تبدیل JSON به فرمت خوانا """
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
            'size_info':{
                "size_name": meta.get('size_name'),
                'width': meta.get('width'),
                'height': meta.get('height'),
            },
            'has_design': meta.get('has_design'),
            'options': readable_options
        }

# ===== سطح ۱: جزئیات سفارش ===== #
class OrderDetailSerializer(serializers.ModelSerializer):
    """
    نمایش کامل سفارش برای صفحه Edit/Detail داشبورد.
    """
    user_info = serializers.SerializerMethodField()
    items = OrderItemDetailSerializer(source='order_item_order', many=True)
    address_detail = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'type',
            'user_info', 'items', 'address_detail', 'status_info', 
            'recipient_name', 'recipient_phone', 'company_name', 'full_address',
            'total_price', 'created_at'
        ]

    def get_user_info(self, obj):
        if not obj.user:
            return None
            
        full_name = obj.user.username
        if hasattr(obj.user, 'customer_profile'):
            full_name = f"{obj.user.customer_profile.first_name} {obj.user.customer_profile.last_name}"
            
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': full_name
        }
        
    def get_address_detail(self, obj):
        if obj.address:
            return f"{obj.address.province.name}, {obj.address.city.name}, {obj.address.address}"
        return obj.full_address

    def get_status_info(self, obj):
        if not obj.current_status: return None
        return {
            'id': obj.current_status.id, 
            'name': obj.current_status.name,
        }
