from rest_framework import serializers
from core.models import Cart, CartItem, CartItemUpload

# ======== Cart Item Upload Serializer ======== #
class CartItemUploadSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش فایل‌های آپلود شده مرتبط با یک آیتم سبد خرید."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CartItemUpload
        fields = ('id', 'file', 'file_url', 'requirement')

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None

# ======== Cart Item Serializer ======== #
class CartItemSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش یک آیتم در سبد خرید."""
    uploads = CartItemUploadSerializer(many=True, read_only=True)
    
    class Meta:
        model = CartItem
        fields = (
            'id',
            'product',
            'quantity',
            'price',
            'items',
            'uploads',
            'updated_at'
        )

# ======== Cart Detail Serializer ======== #
class CartDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش کامل سبد خرید کاربر."""

    class Meta:
        model = Cart
        fields = ('id', 'user', 'updated_at', 'cart_items')
