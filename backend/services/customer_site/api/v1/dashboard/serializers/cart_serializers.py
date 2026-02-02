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
    username = serializers.CharField(source='user.username', allow_null=True)
    items = CartItemDetailSerializer(source='cart_items', many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'username', 'session_key', 'items', 'total_price', 'updated_at']

    def get_total_price(self, obj):
        return sum(item.price for item in obj.cart_items.all())

# ===== Cart Item Add Serializer ===== #
class CartItemSelectionSerializer(serializers.Serializer):
    """
    ساختار انتخاب‌های محصول (ساده‌سازی شده).
    """
    quantity = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    quantity_id = serializers.IntegerField(required=False, allow_null=True)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    custom_width = serializers.FloatField(required=False)
    custom_height = serializers.FloatField(required=False)
    
    options = serializers.DictField(required=False, default={})
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
    quantity = serializers.IntegerField(required=False, min_value=1)
    quantity_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    options = serializers.DictField(required=False, default={})
    has_design = serializers.BooleanField(required=False)
    
# ===== Cart List Serializer ===== #
class CartListSerializer(serializers.ModelSerializer):  
    """
    سریالایزر برای نمایش لیست سبدها در جدول داشبورد.
    """
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=0, read_only=True)
    last_update = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'username', 'full_name', 'items_count', 'total_amount', 'last_update']

    def get_user_id(self, obj):
        # ===== بازگردانی شناسه کاربر ===== #
        return obj.user.id if obj.user else None

    def get_username(self, obj):
        # ===== کاربر مهمان ===== #
        if obj.user:
            return obj.user.username
        return f"مهمان ({obj.session_key[:8]}...)" if obj.session_key else "ناشناس"

    def get_full_name(self, obj):
        # ===== ااگر کاربر دارای پروفایل بود ===== #
        if obj.user:
            try:
                profile = obj.user.customer_profile
                if profile.first_name and profile.last_name:
                    return f"{profile.first_name} {profile.last_name}"
            except Exception:
                pass
            # ===== در صورت نبود کاربر و مهمان بودن ===== #
            return obj.user.username 
        return f"مهمان ({obj.session_key[:8]}...)" if obj.session_key else "ناشناس"

# ===== Cart File Upload Serializer ===== #
class CartFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    requirement_id = serializers.IntegerField()
