from rest_framework import serializers
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, OrderStatusGroup,
    Invoice
)
from apps.logistics.models import OrderPackage, OrderShipment
from .order_cost_serializer import OrderFinancialSheetSerializer

# ========== 1. Micro Serializers ========== #
class FileSerializer(serializers.ModelSerializer):
    """ نمایش فایل‌های طراحی """
    file_url = serializers.CharField(source='file.url', read_only=True)
    filename = serializers.ReadOnlyField() 
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)
    
    class Meta:
        model = OrderItemFile
        fields = ['id', 'file_url', 'filename', 'version', 'is_latest', 'admin_feedback', 'requirement_name']

# ========== 2. Item Serializers =========== #
class BaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    
    features_summary = serializers.CharField(source='feature_summary', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_code', 'category_name', 
            'quantity', 'features_summary', 'admin_note', 'items'
        ]

class DesignerOrderItemSerializer(BaseOrderItemSerializer):
    """ آیتم مخصوص طراح (شامل فایل‌ها) """
    files = FileSerializer(many=True, read_only=True)
    
    class Meta(BaseOrderItemSerializer.Meta):
        fields = BaseOrderItemSerializer.Meta.fields + ['files']

class FullOrderItemSerializer(DesignerOrderItemSerializer):
    """ آیتم کامل (شامل قیمت و جزئیات) """
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)
    
    class Meta(DesignerOrderItemSerializer.Meta):
        fields = DesignerOrderItemSerializer.Meta.fields + ['price', 'total_price']

# ========== 3. Main Order Serializers =========== #

class BaseOrderDetailSerializer(serializers.ModelSerializer):
    customer_info = serializers.SerializerMethodField()
    current_status_display = serializers.CharField(source="current_status.name", read_only=True)
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    order_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_name', 'order_code', 'recipient_name', 
            'recipient_phone', 'company_name', 'full_address', 'description',
            'current_status_display', 'customer_info', 'type_display',
            'created_at'
        ]

    def get_order_name(self, obj):
        first_item = obj.order_item_order.first()
        return first_item.name if first_item else _("بدون نام")

    def get_description(self, obj):
        """
        منطق سینیوری: چون سفارش چندین آیتم دارد، توضیحات اولین آیتم 
        که معمولا توضیحات اصلی مشتری است را برمی‌گردانیم.
        """
        first_item = obj.order_item_order.first()
        if first_item and first_item.description:
            return first_item.description
        return None


    def get_customer_info(self, obj):
        if not obj.user:
            return None
        
        info = {"username": obj.user.username, "email": obj.user.email}
        if hasattr(obj.user, 'customer_profile'):
            profile = obj.user.customer_profile
            info.update({
                "full_name": f"{profile.first_name} {profile.last_name}",
                "company": getattr(profile, 'company', ''),
                "phone": profile.phone_number
            })
        return info

class UniversalOrderDetailSerializer(BaseOrderDetailSerializer):
    """
    سریالایزر جامع برای نمایش تمام جزئیات به همه پرسنل.
    """
    items = FullOrderItemSerializer(source='order_item_order', many=True, read_only=True)
    class Meta(BaseOrderDetailSerializer.Meta):
        model = Order
        fields = BaseOrderDetailSerializer.Meta.fields + [
            'items',
            'total_price', 
            'base_products_price'
        ]