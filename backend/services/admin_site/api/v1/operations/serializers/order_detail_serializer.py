from rest_framework import serializers
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, OrderStatusGroup,
    OrderShipment, OrderPackage, Invoice
)
from .order_cost_serializer import OrderCostSheetSerializer

# ========== 1. Micro Serializers ========== #

class OrderStatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusGroup
        fields = ['name', 'code']

class OrderStatusSerializer(serializers.ModelSerializer):
    group = OrderStatusGroupSerializer(read_only=True)
    class Meta:
        model = OrderStatus
        fields = ['name', 'internal_code', 'group', 'status_type']

class FileSerializer(serializers.ModelSerializer):
    """ نمایش فایل‌های طراحی """
    file_url = serializers.CharField(source='file.url', read_only=True)
    filename = serializers.ReadOnlyField() 
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)
    
    class Meta:
        model = OrderItemFile
        fields = ['id', 'file_url', 'filename', 'version', 'is_latest', 'admin_feedback', 'requirement_name']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPackage
        fields = ['box_number', 'weight_grams', 'label_code', 'content_summary']

class ShipmentSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source='delivery_method.title', read_only=True)
    packages = PackageSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderShipment
        fields = ['id', 'method_name', 'tracking_code', 'status', 'delivery_method', 'packages', 'expected_delivery_date']

class InvoiceSimpleSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.name', read_only=True)
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'final_amount', 'paid_amount', 'status_name', 'is_pre_payment_done']

# ========== 2. Item Serializers =========== #

class BaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    
    features_summary = serializers.CharField(source='feature_summary', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_code', 'category_name', 
            'status_display', 'status', 'quantity', 
            'features_summary', 'admin_note', 'items'
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
    status = OrderStatusSerializer(source='current_status')
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'created_at', 'status', 'customer_info', 'description', 'type']

    def get_customer_info(self, obj):
        if not obj.user: return {"name": "Deleted User"}
        
        info = {"username": obj.user.username, "email": obj.user.email}
        if hasattr(obj.user, 'customer_profile'):
            profile = obj.user.customer_profile
            info.update({
                "full_name": f"{profile.first_name} {profile.last_name}",
                "company": getattr(profile, 'company', ''),
                "phone": profile.phone_number
            })
        return info

# ===== Role: Designer / Production ===== #
class DesignerOrderDetailSerializer(BaseOrderDetailSerializer):
    """ نمایش برای واحد طراحی و چاپ """
    items = DesignerOrderItemSerializer(source='order_item_order', many=True, read_only=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + ['items']

# ===== Role: Logistics ===== #
class LogisticsOrderDetailSerializer(BaseOrderDetailSerializer):
    """ نمایش برای انبار و لجستیک """
    shipping_info = serializers.SerializerMethodField()
    items = BaseOrderItemSerializer(source='order_item_order', many=True, read_only=True) 
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + ['items', 'shipping_info']

    def get_shipping_info(self, obj):
        address = obj.address
        return {
            "recipient_name": f"{address.user.username}" if address else "",
            "full_address": str(address),
            "postal_code": address.postal_code if address else "",
            "shipments": ShipmentSerializer(obj.shipments.all(), many=True).data
        }

# ===== Role: Finance ===== #
class FinanceOrderDetailSerializer(BaseOrderDetailSerializer):
    """ نمایش برای واحد مالی """
    cost_sheet = OrderCostSheetSerializer(read_only=True)
    invoice = InvoiceSimpleSerializer(source='related_invoice', read_only=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + [
            'invoice', 'cost_sheet', 'total_price', 'base_products_price'
        ]

# ===== Role: Admin (Super Detail) ===== #
class AdminOrderDetailSerializer(BaseOrderDetailSerializer):
    items = FullOrderItemSerializer(source='order_item_order', many=True, read_only=True)
    cost_sheet = OrderCostSheetSerializer(read_only=True)
    logistics = serializers.SerializerMethodField()
    
    # اصلاح: استفاده مستقیم از سریالایزر به جای SerializerMethodField ناقص
    invoice = InvoiceSimpleSerializer(source='related_invoice', read_only=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + [
            'items', 
            'cost_sheet',
            'invoice',
            'logistics',
            'total_price', 
            'base_products_price'
        ]
    
    def get_logistics(self, obj):
        return LogisticsOrderDetailSerializer(obj).data.get('shipping_info')
