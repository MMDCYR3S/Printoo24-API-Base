from rest_framework import serializers
from core.models import Product, ProductImage
from apps.cart.models import Cart, CartItem, CartItemUpload

# ===== Product Serializer ===== #
class ProductSerializer(serializers.ModelSerializer):
    # ===== عکس مورد نظر  ===== #
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'has_quantity', 'image']

    def get_image(self, obj):
        # ===== دریافت اولین عکس ===== #
        first_img = obj.product_image.order_by('order', 'id').first()
        
        # ===== اگر عکس بود ===== #
        if first_img and first_img.image:
            request = self.context.get('request')
            
            # ===== نمایش آدرس آن ===== #
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
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

# ===== Cart Item Detail Serializer ===== #
class CartItemDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر هوشمند که داده‌های JSON ذخیره شده در آیتم را پارس می‌کند.
    """
    product = ProductSerializer(read_only=True)
    uploads = CartItemUploadSerializer(many=True, read_only=True)
    # ===== ریز جزئیات آیتم و محصول انتخابی ===== #
    items = serializers.SerializerMethodField(help_text="مشخصات فنی (سایز، متریال و ...)")

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product',
            'name',
            'description',
            'quantity',
            'price',
            'items',
            'uploads',
            'created_at'
        ]

    def get_items(self, obj):
        """
        استخراج داده‌های قابل نمایش از فیلد JSON `items`
        """
        raw = obj.items or {}
        meta = raw.get('meta', {})
        
        # تلاش برای ساخت یک دیکشنری تمیز
        return {
            "size_label": meta.get('size_info', {}).get('size_name') or "سایز اختصاصی",
            "quantity_label": meta.get('quantity_info', {}).get('quantity_text') or str(obj.quantity),
            "dimensions": f"{meta.get('size_info', {}).get('width')}x{meta.get('size_info', {}).get('height')}",
            "options": raw.get('options', []), # لیست آپشن‌های انتخاب شده
            "has_design": meta.get('has_design', True)
        }

# ===== Cart List Serializer ===== #
class CartListSerializer(serializers.ModelSerializer):
    items = CartItemDetailSerializer(source="cart_items", many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'updated_at']

    def get_total_price(self, obj):
        return sum(item.price for item in obj.cart_items.all())
