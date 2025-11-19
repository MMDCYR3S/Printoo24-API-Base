from rest_framework import serializers
from core.models import Cart, CartItem, Product, ProductOption, CartItemUpload, ProductSize

# ======== Product Serializer ======== #
class ProductSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش یک محصول
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug']

# ======== Option Serializer ======== #
class OptionSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش ویژگی های یک محصول
    """
    option_value_name = serializers.CharField(source='option_value.name')
    class Meta:
        model = ProductOption
        fields = ['id', 'option_value_name', 'price_impact']

# ======== Cart Item Detail Serializer ======== #
class CartItemDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش تمام جزئیات یک آیتم سبد خرید
    """
    product = ProductSerializer(read_only=True)
    material_name = serializers.CharField(source='product_material.product.name', read_only=True)
    quantity_name = serializers.CharField(source='product_quantity.product.name', read_only=True)
    size_name = serializers.CharField(source='product_size.product.name', read_only=True, allow_null=True)
    selected_options = OptionSerializer(source='product_options', many=True, read_only=True)
    custom_width = serializers.FloatField(source='product_size.custom_width', allow_null=True)
    custom_height = serializers.FloatField(source='product_size.custom_height', allow_null=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product', 
            'material_name', 
            'quantity_name', 
            'size_name',
            'custom_width',
            'custom_height',
            'selected_options',
            'price', 
            'created_at'
        ]

# ======== Cart List Serializer ======== #
class CartListSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش لیست آیتم‌های سبد خرید کاربر.
    """
    items = CartItemDetailSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'updated_at']

    def get_total_price(self, obj):
        items = getattr(obj, 'prefetched_items', obj.cart_items.all())
        return sum(item.price for item in items)
