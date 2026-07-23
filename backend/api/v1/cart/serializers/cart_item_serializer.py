from rest_framework import serializers
from core.models import Product, ProductImage
from apps.cart.models import Cart, CartItem, CartItemUpload

# ===== Product Serializer ===== #
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'has_quantity', 'image']

    def get_image(self, obj):
        first_img = obj.product_image.order_by('order', 'id').first()
        if first_img and first_img.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_img.image.url)
            return first_img.image.url
        return None

# ===== Uploaded Files Serializer ===== #
class CartItemUploadSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    class Meta:
        model = CartItemUpload
        fields = ['id', 'file_url', 'uploaded_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.file.url) if request and obj.file else None

class CartItemDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر هوشمند که داده‌های JSON را مستقیماً برای فرانت‌اند آماده می‌کند.
    """
    product = ProductSerializer(read_only=True)
    uploads = CartItemUploadSerializer(many=True, read_only=True)
    
    selections = serializers.JSONField(source='items', help_text="مشخصات فنی و انتخاب‌های کاربر")

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product',
            'name',
            'description',
            'quantity',
            'price',
            'selections',
            'uploads',
            'created_at'
        ]

# ===== Cart List Serializer ===== #
class CartListSerializer(serializers.ModelSerializer):
    items = CartItemDetailSerializer(source="cart_items", many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_items', 'updated_at']

    def get_total_price(self, obj):
        return sum(item.price for item in obj.cart_items.all())

    def get_total_items(self, obj):
        return obj.cart_items.count()