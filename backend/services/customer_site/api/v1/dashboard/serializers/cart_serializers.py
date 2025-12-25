from rest_framework import serializers
from apps.cart.models import Cart, CartItem, CartItemUpload

# ===== سریالایزر نمایش فایل آپلود شده ===== #
class CartItemUploadDetailSerializer(serializers.ModelSerializer):
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)
    file_url = serializers.FileField(source='file', read_only=True)
    
    class Meta:
        model = CartItemUpload
        fields = ['id', 'requirement_name', 'file_url', 'uploaded_at']

# ===== نمایش کامل سبد خرید (Nested) ===== #
class CartItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    details = serializers.JSONField(source='items') 
    
    uploads = CartItemUploadDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_name', 'quantity', 'price', 'details', 'uploads', 'created_at']

# ===== User Cart Detail Serializer ===== #
class UserCartDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    items = CartItemDetailSerializer(source='cart_items', many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'username', 'items', 'total_price', 'updated_at']

    def get_total_price(self, obj):
        return sum(item.price for item in obj.cart_items.all())

# ===== Cart Item Add Serializer ===== #
class CartItemSelectionSerializer(serializers.Serializer):
    """
    ساختار انتخاب‌های محصول (ساده‌سازی شده).
    """
    quantity = serializers.IntegerField(min_value=1)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    custom_width = serializers.FloatField(required=False)
    custom_height = serializers.FloatField(required=False)
    
    option_value_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    has_design = serializers.BooleanField(default=True)

# ===== Cart Item Add Simple Serializer ===== #
class CartItemAddSimpleSerializer(serializers.Serializer):
    """
    سریالایزر اصلی برای افزودن آیتم به سبد خرید ادمین.
    """
    product_slug = serializers.CharField() 
    selections = CartItemSelectionSerializer()

# ===== Cart Item Update Serializer ===== #
class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=False)
    specs = serializers.DictField(required=False)
    
# ===== Cart List Serializer ===== #
class CartListSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش لیست سبدها در جدول داشبورد.
    """
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    full_name = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=0, read_only=True)
    last_update = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'username', 'full_name', 'items_count', 'total_amount', 'last_update']

    def get_full_name(self, obj):
        try:
            profile = obj.user.customer_profile
            return f"{profile.first_name} {profile.last_name}"
        except Exception:
            return "ناشناس"

# ===== Cart File Upload Serializer ===== #
class CartFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    requirement_id = serializers.IntegerField()
