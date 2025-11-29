from rest_framework import serializers

from core.models import (
    Order, 
    OrderItem, 
    Product, 
    DesignFile,
    OrderItemDesignFile,
    Address,
)

# ===== Product Serializer ===== # 
class ProductSerializer(serializers.ModelSerializer):
    """
    یک سریالایزر ساده فقط برای نمایش اطلاعات ضروری محصول در لیست آیتم‌های سفارش.
    """
    class Meta:
        model = Product
        fields = ['name', 'slug']

# ===== Design File Serializer ===== #
class DesignFileSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش URL فایل آپلود شده.
    """
    file_url = serializers.URLField(source='file.url', read_only=True)
    
    class Meta:
        model = DesignFile
        fields = ['id', 'file_url']

# ===== Order Item Serializer ===== #
class OrderItemSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش جزئیات یک آیتم در سفارش.
    این سریالایزر شامل اطلاعات محصول و فایل‌های طراحی مربوطه است.
    """
    product = ProductSerializer(read_only=True) 
    design_files = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product', 
            'quantity', 
            'price', 
            'items',
            'design_files'
        ]
        
    def get_design_files(self, obj):
        """
        دریافت اطلاعات فایل‌های طراحی مرتبط با این آیتم سفارش.
        """
        files_links = obj.order_item_design_file_order_item.all()
        return [
            {
                "id": link.file.id,
                "url": link.file.file.url if link.file.file else None
            } 
            for link in files_links
        ]

# ===== Order Serializers ===== #
class OrderSerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی برای نمایش یک سفارش کامل به همراه تمام آیتم‌های آن.
    """
    # ===== نمایش نام مشتری ===== #
    user = serializers.StringRelatedField(read_only=True)
    # ===== نمایش وضعیت سفارش مورد نظر ===== #
    order_status = serializers.StringRelatedField(read_only=True)
    # ===== نمایش نوع سفارش ===== #
    type = serializers.CharField(source='get_type_display', read_only=True)
    # ===== نمایش آیتم‌های سفارش ===== #
    items = OrderItemSerializer(many=True, read_only=True, source='order_item_order')
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source="address",
        required=False,
        allow_null=True
    )
    
    # ===== نمایش آدرس ===== #
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['address_id'].queryset = Address.objects.filter(user=request.user)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'order_status',
            'type',
            'total_price',
            'created_at',
            'items',
            'address_id'
        ]
