from rest_framework import serializers
from core.models import (
    Order, OrderItem, OrderItemFile, OrderStatus, OrderStatusGroup, OrderCostReport,
    OrderStateLog, OrderCostItem, OrderInvoice, OrderTransaction, OrderShipment
)

# ========== 1. Micro Serializers ========== #
class OrderStatusGroupSerializer(serializers.ModelSerializer):
    """ نمایش خلاصه گروه وضعیت """
    class Meta:
        model = OrderStatusGroup
        fields = ['name', 'code']

class OrderStatusSerializer(serializers.ModelSerializer):
    """ نمایش وضعیت سفارش یا آیتم """
    # ===== Nested: نمایش اطلاعات گروه وضعیت =====
    group = OrderStatusGroupSerializer(read_only=True) 
    
    class Meta:
        model = OrderStatus
        fields = ['name', 'internal_code', 'group']

class FileSerializer(serializers.ModelSerializer):
    """ نمایش فایل‌های طراحی """
    file_url = serializers.CharField(source='file.url', read_only=True)
    filename = serializers.CharField(read_only=True)
    requirement_name = serializers.CharField(source='requirement.spec.name', read_only=True)
    
    class Meta:
        model = OrderItemFile
        fields = ['id', 'file_url', 'filename', 'version', 'status', 'admin_feedback', 'requirement_name']

class CostItemSerializer(serializers.ModelSerializer):
    """ نمایش اقلام ریز هزینه (زیرمجموعه گزارش) """
    type_name = serializers.CharField(source='catalog_item.cost_type.title', read_only=True)
    
    class Meta:
        model = OrderCostItem
        fields = ['id', 'final_title', 'amount', 'type_name', 'description', 'custom_title']
        
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTransaction
        fields = ['id', 'amount', 'transaction_type', 'status', 'payment_date', 'tracking_code', 'receipt_image']
        
class OrderCostReportSerializer(serializers.ModelSerializer):
    """ مدل گزارش هزینه (مدل بالادستی) """
    items = CostItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'title', 'description', 'is_approved_by_finance', 
            'total_amount', 'created_by_name', 'created_at', 'items'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)
    class Meta:
        model = OrderInvoice
        fields = ['invoice_number', 'items_total', 'services_total', 'tax_amount', 'discount_amount', 'final_payable_amount', 'paid_amount', 'remaining_amount', 'status']

class StateLogSerializer(serializers.ModelSerializer):
    """ تاریخچه تغییرات وضعیت """
    user_name = serializers.CharField(source='user.username', read_only=True)
    from_status = serializers.CharField(source='from_status.name', read_only=True)
    to_status = serializers.CharField(source='to_status.name', read_only=True)
    
    class Meta:
        model = OrderStateLog
        fields = ['timestamp', 'user_name', 'from_status', 'to_status', 'description', 'duration_in_previous_status']

class ShipmentSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source='delivery_method.title', read_only=True)
    class Meta:
        model = OrderShipment
        fields = ['id', 'method_name', 'tracking_code', 'status', 'delivery_method', 'shipping_cost_real']

# ========== 2. Item Serializers =========== #

class BaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    designer_name = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    features_summary = serializers.CharField(source='feature_summary', read_only=True)
    item_status = OrderStatusSerializer(source='status', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_code', 'designer_name', 'category_name', 'price', 'quantity', 'features_summary', 'admin_note', 'item_status']

class DesignerOrderItemSerializer(BaseOrderItemSerializer):
    """ آیتم مخصوص طراح (شامل فایل‌ها) """
    files = FileSerializer(many=True, read_only=True)
    
    class Meta(BaseOrderItemSerializer.Meta):
        fields = BaseOrderItemSerializer.Meta.fields + ['files']

class FullOrderItemSerializer(DesignerOrderItemSerializer):
    """ آیتم کامل (شامل قیمت و فایل) """
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    
    class Meta(DesignerOrderItemSerializer.Meta):
        fields = DesignerOrderItemSerializer.Meta.fields + ['price', 'total_price', 'assigned_to_name']

# ========== 3. Main Serializers =========== #

class BaseOrderDetailSerializer(serializers.ModelSerializer):
    """ سریالایزر پایه برای همه نقش‌ها """
    customer_info = serializers.SerializerMethodField()
    status = OrderStatusSerializer(source='current_status')
    
    class Meta:
        model = Order
        fields = ['id', 'order_code', 'created_at', 'status', 'customer_info', 'description']

    def get_customer_info(self, obj):
        """ نمایش اطلاعات مشتری (نام کاربری، ایمیل، نام کامل، شرکت، شماره تماس) """
        
        if not obj.user: return {"name": "Deleted User"}
        
        info = {"username": obj.user.username, "email": obj.user.email}
        if hasattr(obj.user, 'customer_profile'):
            profile = obj.user.customer_profile
            info.update({
                "full_name": f"{profile.first_name} {profile.last_name}",
                "company": profile.company,
                "phone": profile.phone_number
            })
        return info

# ===== Role: Designer ===== #
class DesignerOrderDetailSerializer(BaseOrderDetailSerializer):
    """ طراح و QC فقط آیتم‌های خودشان (یا آزاد) و فایل‌ها را می‌بینند """
    items = DesignerOrderItemSerializer(source='order_item_order', many=True, read_only=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + ['items']
        
# ===== Role: Finance ===== #
class FinanceOrderDetailSerializer(BaseOrderDetailSerializer):
    """ مالی همه اطلاعات پولی و گزارشات هزینه را می‌بیند """
    invoice = InvoiceSerializer(source='invoice_order', read_only=True)
    cost_reports = OrderCostReportSerializer(source='cost_reports', many=True, read_only=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + ['invoice', 'cost_reports', 'total_price', 'base_products_price']

# ===== Role: Logistics ===== #
class LogisticsOrderDetailSerializer(BaseOrderDetailSerializer):
    """ انباردار آدرس و مرسولات را می‌بیند """
    shipping_info = serializers.SerializerMethodField()
    items = BaseOrderItemSerializer(source='order_item_order', many=True, read_only=True) 
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + ['items', 'shipping_info']

    def get_shipping_info(self, obj):
        address = obj.address
        return {
            "recipient": str(address),
            "postal_code": address.postal_code if address else "",
            "shipments": ShipmentSerializer(obj.shipments.all(), many=True).data
        }

# ===== Role: Admin ===== #
class AdminOrderDetailSerializer(BaseOrderDetailSerializer):
    """ ادمین همه چیز را می‌بیند """
    # آیتم‌ها (با تمام جزئیات)
    items = FullOrderItemSerializer(source='order_item_order', many=True, read_only=True)
    # ترکیب اطلاعات مالی و لجستیک با source='*'
    financial = FinanceOrderDetailSerializer(source='*', read_only=True)
    logistics = LogisticsOrderDetailSerializer(source='*', read_only=True)
    logs = StateLogSerializer(source='state_logs', many=True)
    
    class Meta(BaseOrderDetailSerializer.Meta):
        fields = BaseOrderDetailSerializer.Meta.fields + [
            'items', 
            'financial', 
            'logistics', 
            'logs', 
            'total_price', 
            'base_products_price'
        ]
