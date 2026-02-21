from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Order, OrderItem, OrderItemFile, Product, City, Province, Address
from core.infrastructure.messages import msg_provider

# ===== Province List ===== #
class ProvinceSerialzier(serializers.ModelSerializer):
    """
    سریالایزر برای استان
    """
    class Meta:
        model = Province
        fields = ["id", "name"]

# ===== City List ===== #
class CitySerialzier(serializers.ModelSerializer):
    """
    سریالایزر برای استان
    """
    class Meta:
        model = City
        fields = ["id", "name", "province"]

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
    
    specs = serializers.SerializerMethodField()
    pricing_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'name', 'description',
            'quantity', 'price', 'specs', 'design_files',
            'pricing_breakdown'
        ]

    def get_specs(self, obj):
        """
        استخراج و فرمت‌دهی اطلاعات فنی از JSON Field (item.items)
        شامل ابعاد، تیراژ و تمامی ویژگی‌های انتخابی (حتی وابسته‌ها).
        """
        raw_data = obj.items or {}
        meta = raw_data.get('meta', {})
        
        # ۱. استخراج اطلاعات ابعاد
        size_info = meta.get('size_info', {})
        width = size_info.get('width')
        height = size_info.get('height')
        size_name = size_info.get('size_name', 'استاندارد')

        # ۲. استخراج اطلاعات تیراژ
        qty_info = meta.get('quantity_info', {})
        qty_text = qty_info.get('quantity_text', str(obj.quantity))

        # ۳. پردازش غنی ویژگی‌ها (Options)
        raw_options = raw_data.get('options', [])
        detailed_options = []

        for opt in raw_options:
            option_label = opt.get('option_label', 'N/A')
            type_ptr = opt.get('type')
            
            choices_list = []
            
            if type_ptr == 'selection':
                val_data = opt.get('value', {})
                choices_list.append(self._format_choice(val_data))
                
            elif type_ptr == 'multi_selection':
                for val_data in opt.get('values', []):
                    choices_list.append(self._format_choice(val_data))
                    
            elif type_ptr == 'raw':
                choices_list.append({
                    "label": str(opt.get('value', 'N/A')),
                    "price": 0.0,
                    "dependencies": []
                })

            detailed_options.append({
                "option_group": option_label,
                "selections": choices_list
            })

        return {
            "size": {
                "name": size_name,
                "dimensions": f"{width} x {height} cm" if width and height else "استاندارد"
            },
            "quantity_label": qty_text,
            "has_design": meta.get('has_design', False),
            "options_detail": detailed_options
        }

    def _format_choice(self, val_data: dict) -> dict:
        """ متد کمکی برای تمیز کردن داده‌های هر انتخاب """
        return {
            "label": val_data.get('label', 'N/A'),
            "price": val_data.get('applied_price', 0.0),
            "is_tiered": val_data.get('is_matrix_price', False),
            "dependency_text": [
                f"وابسته به: {d['parent_option_name']} ({d['required_value_name']})" 
                for d in val_data.get('dependencies', [])
            ]
        }

    def get_pricing_breakdown(self, obj):
        """ نمایش ریز محاسبات ماشین‌حساب (هزینه شیت، طراحی، خدمات و ...) """
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
                raise ValidationError(msg_provider.get("order.E7009"))
            if not has_new_address:
                raise ValidationError(msg_provider.get("order.E7010"))
            if addr_id:
                raise ValidationError(msg_provider.get("order.E7011"))

        # ===== برای کاربری که ثبت نام کرده ===== #
        else:
            if not addr_id and not has_new_address:
                raise ValidationError(msg_provider.get("order.E7012"))

        # ===== دریافت استان و شهر ===== #
        if attrs.get('province_id'):
            try:
                attrs['province_name'] = Province.objects.get(pk=attrs['province_id']).name
            except Province.DoesNotExist:
                raise ValidationError({"province_id": msg_provider.get("order.E7013")})
        
        if attrs.get('city_id'):
            try:
                attrs['city_name'] = City.objects.get(pk=attrs['city_id']).name
            except City.DoesNotExist:
                raise ValidationError({"city_id": msg_provider.get("order.E7014")})

        return attrs

# ===== سریالایزر استان (برای نمایش داخل آدرس) =====
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug']

# ===== سریالایزر شهر (برای نمایش داخل آدرس) =====
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'slug']

# ===== سریالایزر اصلی آدرس =====
class AddressListSerializer(serializers.ModelSerializer):
    """
    سریالایزر مخصوص نمایش لیست آدرس‌ها.
    استان و شهر به صورت آبجکت کامل نمایش داده می‌شوند.
    """
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 
            'province', 
            'city', 
            'postal_code', 
            'address', 
            'created_at'
        ]
