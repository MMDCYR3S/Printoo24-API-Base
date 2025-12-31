from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Order, OrderItem, OrderItemFile, Product, Address, City, Province

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
             'name',
             'description',
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
    سریالایزر هوشمند که هم ورودی‌های ترکیبی (آدرس جدید/قدیمی) را می‌گیرد
    و هم خروجی نهایی فاکتور را نمایش می‌دهد.
    """
    
    # ===== خروجی‌ها (Read Only) ===== #
    status = serializers.CharField(source='current_status.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)
    order_code = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    item_detail = serializers.SerializerMethodField()
    
    # ===== نمایش سفارش های داده شده ===== #
    recipient_name = serializers.CharField(read_only=True)
    recipient_phone = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)

    # ===== ورودی‌ها (Write Only) - مشخصات فردی ===== #
    first_name = serializers.CharField(write_only=True, required=False, label="نام")
    last_name = serializers.CharField(write_only=True, required=False, label="نام خانوادگی")
    phone_number = serializers.CharField(write_only=True, required=False, label="شماره تماس")
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True, label="نام شرکت")

    # ===== ورودی‌ها (Write Only) - آدرس دهی ===== #
    address_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True, 
        help_text="اگر کاربر لاگین است و از لیست انتخاب کرده"
    )
    
    # ===== آدرس جدید ===== #
    province_id = serializers.IntegerField(write_only=True, required=False, label="شناسه استان")
    city_id = serializers.IntegerField(write_only=True, required=False, label="شناسه شهر")
    address_text = serializers.CharField(write_only=True, required=False, label="نشانی دقیق")
    postal_code = serializers.CharField(write_only=True, required=False, label="کد پستی")

    type = serializers.ChoiceField(
        choices=Order.ORDER_TYPE, default='1', write_only=True
    )

    class Meta:
        model = Order
        fields = [
            # Outputs
            'id', 'order_code', 'status', 'type_display', 'total_price',
            'recipient_name', 'recipient_phone', 'full_address',
            'created_at', 'item_detail',
            
            # Inputs
            'type', 'address_id', 
            'first_name', 'last_name', 'phone_number', 'company_name',
            'province_id', 'city_id', 'address_text', 'postal_code'
        ]

    def get_item_detail(self, obj):
        item = obj.order_item_order.first()
        if item:
            return OrderItemDetailSerializer(item, context=self.context).data
        return None

    def validate(self, attrs):
        """
        اعتبارسنجی شرطی:
        ۱. مهمان: باید نام، تلفن و آدرس کامل را وارد کند.
        ۲. عضو: یا باید address_id بدهد یا آدرس کامل را پر کند.
        """
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        # ===== استخراج فیلدهای مورد نیاز ===== #
        addr_id = attrs.get('address_id')
        has_new_address = all([attrs.get('province_id'), attrs.get('city_id'), attrs.get('address_text')])
        has_profile_info = all([attrs.get('first_name'), attrs.get('last_name'), attrs.get('phone_number')])

        # ===== سناریو مهمان ===== #
        if not user:
            if not has_profile_info:
                raise ValidationError("برای سفارش مهمان، وارد کردن نام، نام خانوادگی و شماره تماس الزامی است.")
            if not has_new_address:
                raise ValidationError("برای سفارش مهمان، وارد کردن استان، شهر و آدرس دقیق الزامی است.")
            if addr_id:
                raise ValidationError("کاربر مهمان نمی‌تواند از آدرس‌های ذخیره شده استفاده کند.")

        # ===== برای کاربری که ثبت نام کرده ===== #
        else:
            if not addr_id and not has_new_address:
                raise ValidationError("لطفاً یا یک آدرس انتخاب کنید یا فرم آدرس جدید را کامل پر کنید.")

        # ===== دریافت استان و شهر ===== #
        if attrs.get('province_id'):
            try:
                attrs['province_name'] = Province.objects.get(pk=attrs['province_id']).name
            except Province.DoesNotExist:
                raise ValidationError({"province_id": "استان نامعتبر است."})
        
        if attrs.get('city_id'):
            try:
                attrs['city_name'] = City.objects.get(pk=attrs['city_id']).name
            except City.DoesNotExist:
                raise ValidationError({"city_id": "شهر نامعتبر است."})

        return attrs
