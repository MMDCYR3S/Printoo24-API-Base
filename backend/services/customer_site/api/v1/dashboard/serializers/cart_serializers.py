from rest_framework import serializers
from apps.cart.models import Cart, CartItem, CartItemUpload

# ===== سریالایزر نمایش فایل آپلود شده ===== #
class CartItemUploadDetailSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = CartItemUpload
        fields = ['id', 'file_url', 'uploaded_at']

# ===== نمایش کامل آیتم سبد خرید ===== #
class CartItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_slug = serializers.SerializerMethodField()
    details = serializers.JSONField(source='items')
    uploads = CartItemUploadDetailSerializer(many=True, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product_name', 'product_slug',
            'name', 'quantity', 'price',
            'details', 'uploads', 'created_at'
        ]

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return obj.name or None

    def get_product_slug(self, obj):
        if obj.product:
            return obj.product.slug
        return None

# ===== نمایش کامل سبد خرید ===== #
class UserCartDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    items = CartItemDetailSerializer(source='cart_items', many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'phone_number', 'session_key', 'items', 'total_price', 'updated_at']

    def get_phone_number(self, obj):
        if obj.user:
            return getattr(obj.user, 'phone_number', None)
        return f"مهمان ({obj.session_key[:8]}...)" if obj.session_key else "ناشناس"

    def get_total_price(self, obj):
        return sum(item.price for item in obj.cart_items.all())

# ===== انتخاب‌های آیتم (Selections) ===== #
class CartItemSelectionSerializer(serializers.Serializer):
    """
    ساختار selections متناسب با ProductField/ProductFieldChoice جدید.
    فیلدهای field_<id> به صورت داینامیک از فرانت‌اند می‌آیند.
    """
    quantity = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    has_design = serializers.BooleanField(default=True, required=False)

    # ===== نام و توضیحات (برای آیتم دستی یا override) ===== #
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def to_internal_value(self, data):
        """
        قبول فیلدهای داینامیک field_<id> که در schema ثابت نیستند.
        """
        result = super().to_internal_value(data)
        for key, value in data.items():
            if key.startswith('field_'):
                result[key] = value
        return result

# ===== افزودن آیتم به سبد ===== #
class CartItemAddSimpleSerializer(serializers.Serializer):
    """
    سریالایزر اصلی برای افزودن آیتم به سبد یا ثبت سفارش توسط ادمین.
    product_slug اختیاری است تا آیتم‌های کاملاً دستی هم پشتیبانی شوند.
    """
    product_slug = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # ===== قیمت‌گذاری دستی (ادمین) ===== #
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, allow_null=True)
    item_price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, allow_null=True)

    # ===== نام و توضیحات در سطح آیتم ===== #
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    selections = serializers.DictField(
        child=serializers.JSONField(), # به کلاینت اجازه می‌دهد عدد، رشته یا لیست (برای چک‌باکس‌ها) بفرستد
        help_text="""
        دیکشنری انتخاب‌های کاربر.
        - کلیدها: آیدی فیلدهای داینامیک (مثلاً "10")
        - مقادیر: مقدار تایپ شده یا آیدیِ گزینه انتخاب شده.
        - فیلدهای رزرو شده (اختیاری): "name" (نام پروژه) و "description" (توضیحات مشتری).
        """
    )

# ===== ویرایش آیتم سبد ===== #
class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=1)
    has_design = serializers.BooleanField(required=False)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    price = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, allow_null=True)

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        for key, value in data.items():
            if key.startswith('field_'):
                result[key] = value
        return result

# ===== لیست سبدها ===== #
class CartListSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=0, read_only=True)
    last_update = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'phone_number', 'full_name', 'items_count', 'total_amount', 'last_update']

    def get_user_id(self, obj):
        return obj.user.id if obj.user else None

    def get_phone_number(self, obj):
        if obj.user:
            return getattr(obj.user, 'phone_number', None)
        return f"مهمان ({obj.session_key[:8]}...)" if obj.session_key else "ناشناس"

    def get_full_name(self, obj):
        if obj.user:
            try:
                profile = obj.user.customer_profile
                name = f"{profile.first_name} {profile.last_name}".strip()
                if name:
                    return name
            except Exception:
                pass
            return getattr(obj.user, 'phone_number', obj.user.phone_number)
        return f"مهمان ({obj.session_key[:8]}...)" if obj.session_key else "ناشناس"

# ===== آپلود فایل ===== #
class CartFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    requirement_id = serializers.IntegerField()