from rest_framework import serializers
from core.models import Order, OrderItem, OrderStatus

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    product_slug = serializers.CharField(source='product.slug', read_only=True, default=None)
    specifications = serializers.JSONField(source='items', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_slug', 'name', 
            'description', 'quantity', 'price', 'status', 'specifications'
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    address_detail = serializers.CharField(source='address.full_address', read_only=True, default=None)
    current_status = serializers.CharField(source='current_status.name', read_only=True)
    current_status_code = serializers.CharField(source='current_status.internal_code', read_only=True)
    # خروجی همچنان لیست میمونه چون فیلد Relation از نوع OneToMany هست، اما همیشه 1 دونه عضو داره
    items = OrderItemSerializer(source='order_item_order', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_code', 'user_info', 'recipient_name', 'recipient_phone', 
            'company_name', 'full_address', 'address_detail', 'current_status', 
            'current_status_code', 'total_price', 'base_products_price', 
            'type', 'created_at', 'items'
        ]

    def get_user_info(self, obj):
        if not obj.user:
            return None
        return {
            "id": obj.user.id,
            "phone_number": obj.user.phone_number,
            "full_name": f"{obj.user.first_name} {obj.user.last_name}".strip() if hasattr(obj.user, 'first_name') else obj.user.phone_number
        }

# ===== Input Serializers ===== #
class SelectedOptionInputSerializer(serializers.Serializer):
    field_id = serializers.IntegerField(required=True)
    choice_id = serializers.IntegerField(required=False, allow_null=True)
    choice_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True, allow_null=True
    )
    value = serializers.CharField(required=False, allow_null=True, allow_blank=True)

class OrderCreateSerializer(serializers.Serializer):
    """ سریالایزر ساخت سفارش (فقط یک آیتم) """
    user_id = serializers.IntegerField(required=False, allow_null=True)
    address_id = serializers.IntegerField(required=False, allow_null=True)
    recipient_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    recipient_phone = serializers.CharField(max_length=11, required=False, allow_null=True)
    company_name = serializers.CharField(max_length=150, required=False, allow_null=True)
    full_address = serializers.CharField(required=False, allow_null=True)
    total_price_override = serializers.DecimalField(max_digits=18, decimal_places=0, required=False, allow_null=True)
    type = serializers.CharField(max_length=50, default="1")
    
    # فیلدهای آیتمِ تکیِ سفارش
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(default=1)
    has_design = serializers.BooleanField(default=True)
    selected_options = SelectedOptionInputSerializer(many=True, required=False, default=list)

class OrderUpdateSerializer(serializers.Serializer):
    """ سریالایزر ویرایش سفارش (تکی) """
    recipient_name = serializers.CharField(max_length=255, required=False)
    recipient_phone = serializers.CharField(max_length=11, required=False)
    full_address = serializers.CharField(required=False)
    total_price_override = serializers.DecimalField(max_digits=18, decimal_places=0, required=False, allow_null=True)
    
    # ادمین در صورت نیاز می‌تونه محصول و آپشن‌ها رو هم ویرایش کنه
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, default=1)
    has_design = serializers.BooleanField(required=False, default=True)
    selected_options = SelectedOptionInputSerializer(many=True, required=False, default=list)

class ChangeStatusSerializer(serializers.Serializer):
    internal_code = serializers.CharField(required=True, help_text="کد سیستمی وضعیت (مثال: PENDING_INITIAL_ADMIN)")
    description = serializers.CharField(required=False, allow_blank=True)

class BulkActionIdsSerializer(serializers.Serializer):
    order_ids = serializers.ListField(child=serializers.IntegerField(), required=True, allow_empty=False)

class BulkChangeStatusSerializer(BulkActionIdsSerializer):
    internal_code = serializers.CharField(required=True)

# ===== سریالایزر جدید برای لیست وضعیت‌ها ===== #
class OrderStatusSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)
    
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'internal_code', 'status_type', 'group_name', 'sort_order']
