from rest_framework import serializers
from core.models import Order, OrderItem, OrderItemFile, OrderStatus
from api.v1.dashboard.serializers import CartItemAddSimpleSerializer

# ===== فایل‌های آیتم ===== #
class OrderFileSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = OrderItemFile
        fields = ['id', 'file_url', 'version', 'is_latest', 'uploaded_at']

# ===== لیست سفارشات ===== #
class OrderListSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    status_name = serializers.CharField(source='current_status.name', allow_null=True)
    items_count = serializers.SerializerMethodField()
    type_name = serializers.CharField(source='get_type_display', allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'phone_number',
            'recipient_name', 'recipient_phone',
            'status_name', 'type_name',
            'total_price', 'items_count', 'created_at'
        ]

    def get_phone_number(self, obj):
        if obj.user:
            return getattr(obj.user, 'phone_number', None)
        return None

    def get_items_count(self, obj):
        return obj.order_item_order.count()

# ===== سطح ۲: آیتم سفارش ===== #
class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
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
            'status',
            'specifications',
            'files'
        ]

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return obj.name or None

    def get_product_slug(self, obj):
        if obj.product:
            return obj.product.slug
        return None

    def get_specifications(self, obj):
        """
        تبدیل JSON ذخیره شده (فیلد items) به فرمت خوانا برای فرانت ادمین.
        """
        raw_data = obj.items or {}
        if not isinstance(raw_data, dict):
            return {}

        # ===== فیلدهای سیستمی از JSON ===== #
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

        result = {
            'width': meta.get('width'),
            'height': meta.get('height'),
            'has_design': meta.get('has_design'),
            'options': readable_options
        }

        # ===== اگر meta وجود نداشت، کل raw_data را برگردان ===== #
        if not meta and not options:
            safe_data = {k: v for k, v in raw_data.items()}
            result.update(safe_data)

        return result

# ===== سطح ۱: جزئیات سفارش ===== #
class OrderDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    items = OrderItemDetailSerializer(source='order_item_order', many=True)
    address_detail = serializers.SerializerMethodField()
    current_status = serializers.CharField(source='current_status.name', read_only=True, allow_null=True)
    current_status_code = serializers.CharField(source='current_status.internal_code', read_only=True, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'user_info',
            'recipient_name', 'recipient_phone',
            'company_name', 'full_address', 'address_detail',
            'current_status', 'current_status_code',
            'total_price', 'base_products_price',
            'type', 'created_at', 'items'
        ]

    def get_user_info(self, obj):
        if not obj.user:
            return None
        user = obj.user
        full_name = user.phone_number
        try:
            profile = user.customer_profile
            full_name = f"{profile.first_name} {profile.last_name}".strip() or user.phone_number
        except Exception:
            pass
        return {
            'id': user.id,
            'phone_number': getattr(user, 'phone_number', None),
            'full_name': full_name
        }

    def get_address_detail(self, obj):
        if not obj.address:
            return obj.full_address or None
        try:
            return f"{obj.address.province.name} - {obj.address.city.name} - {obj.address.address}"
        except Exception:
            return None

# ===== ایجاد سفارش (Input) ===== #
class AdminOrderCreateSerializer(serializers.Serializer):
    """
    سریالایزر ایجاد سفارش توسط ادمین.
    user_id اختیاری است (None = مهمان).
    """
    user_id = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(child=CartItemAddSimpleSerializer(), min_length=1)

    total_price = serializers.DecimalField(
        max_digits=18,
        decimal_places=0,
        required=False,
        allow_null=True,
        help_text="اگر وارد شود، قیمت محاسبه‌شده آیتم‌ها نادیده گرفته می‌شود."
    )

    address_id = serializers.IntegerField(required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recipient_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recipient_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        if not attrs.get('address_id') and not attrs.get('full_address'):
            raise serializers.ValidationError("وارد کردن 'address_id' یا 'full_address' الزامی است.")
        return attrs

# ===== ویرایش سفارش (Input) ===== #
class AdminOrderUpdateSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=Order.ORDER_TYPE, required=False)
    total_price = serializers.DecimalField(
        max_digits=18,
        decimal_places=0,
        required=False,
        allow_null=True
    )
    recipient_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    recipient_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    full_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

# ===== لیست وضعیت‌ها ===== #
class OrderStatusListSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)

    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'internal_code', 'status_type', 'sort_order', 'group_name']

# ===== تغییر وضعیت (Input) ===== #
class OrderStatusChangeSerializer(serializers.Serializer):
    status_code = serializers.CharField(
        required=True,
        help_text="کد سیستمی وضعیت (internal_code) مثلا: CONFIRMED_PROGRESS_DESIGN"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="توضیحات اختیاری بابت تغییر وضعیت"
    )
