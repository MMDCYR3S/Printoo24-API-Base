from rest_framework import serializers
from core.models import Order, OrderItem, OrderStatus, Address, OrderItemFile, FinancialStatus
from core.financial.models import (
    Payment, Invoice, Quotation, FinancialLog, Expense
)


class PaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_code', 'amount', 'method', 'method_display',
            'status', 'status_display', 'reference_number', 'receipt',
            'description', 'payment_date', 'approved_at', 'created_at'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_amount = serializers.DecimalField(
        max_digits=18, decimal_places=0, read_only=True
    )

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'items_amount', 'services_amount',
            'tax_amount', 'discount_amount', 'final_amount',
            'paid_amount', 'remaining_amount', 'status', 'status_display',
            'issued_at', 'due_date', 'finalized_at'
        ]


class QuotationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'customer_name', 'product_name',
            'product_image', 'product_snapshot', 'quantity',
            'total_price', 'status', 'status_display', 'valid_until', 'created_at'
        ]


class FinancialLogSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    created_by_phone = serializers.CharField(source='created_by.phone_number', read_only=True, default=None)

    class Meta:
        model = FinancialLog
        fields = [
            'id', 'action_type', 'action_type_display', 'field_name',
            'old_value', 'new_value', 'description', 'reason',
            'created_by', 'created_by_phone', 'created_at'
        ]


class ExpenseSerializer(serializers.ModelSerializer):
    expense_type_display = serializers.CharField(source='get_expense_type_display', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'expense_code', 'expense_type', 'expense_type_display',
            'name', 'amount', 'quantity', 'unit_price',
            'description', 'expense_date'
        ]


# ===== Upload & Delete Item File of Order ===== #
class OrderItemFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemFile
        fields = ['id', 'file']

class OrderItemUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    product_slug = serializers.CharField(source='product.slug', read_only=True, default=None)
    specifications = serializers.JSONField(source='items', read_only=True)
    files = OrderItemFileSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_slug', 'name',
            'description', 'quantity', 'price', 'status', 'specifications', 'files'
        ]
class OrderDetailSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address_detail = serializers.SerializerMethodField()
    current_status = serializers.CharField(source='current_status.name', read_only=True)
    current_status_code = serializers.CharField(source='current_status.internal_code', read_only=True)
    financial_status_display = serializers.CharField(source='get_financial_status_display', read_only=True)
    items = OrderItemSerializer(source='order_item_order', many=True, read_only=True)

    # ===== ارتباطات مالی ===== #
    payments = PaymentSerializer(many=True, read_only=True)
    invoice = InvoiceSerializer(read_only=True)  # reverse one-to-one
    quotation = QuotationSerializer(source='origin_quotation', read_only=True)
    financial_logs = FinancialLogSerializer(many=True, read_only=True)
    expenses = ExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            # اطلاعات عمومی سفارش (قبلی)
            'id', 'order_code', 'user_info', 'recipient_name', 'recipient_phone',
            'company_name', 'city', 'province', 'full_address', 'address_detail',
            'current_status', 'current_status_code',
            'type', 'created_at', 'items',

            # ===== فیلدهای مالی مستقیم از مدل Order ===== #
            'subtotal', 'discount_amount', 'tax_amount', 'shipping_cost',
            'final_price', 'paid_amount', 'remaining_amount',
            'deposit_required', 'deposit_paid',
            'financial_status', 'financial_status_display',
            'payment_deadline', 'invoice_date', 'settlement_date',
            'total_price', 'base_products_price',

            # ===== ارتباطات مالی مستقیم ===== #
            'payments', 'invoice', 'quotation', 'financial_logs', 'expenses',
        ]

    def get_user_info(self, obj):
        if not obj.user:
            return None
        return {
            "id": obj.user.id,
            "phone_number": obj.user.phone_number,
            "full_name": obj.user.customer_profile.fullname() or obj.user.phone_number
        }

    def get_province(self, obj):
        if obj.address:
            return obj.address.province.name
        return None

    def get_city(self, obj):
        if obj.address:
            return obj.address.city.name
        return None

    def get_address_detail(self, obj):
        if obj.address:
            return obj.address.address
        return obj.full_address

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
    company_name = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
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
    recipient_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    recipient_phone = serializers.CharField(max_length=11, required=False, allow_null=True)
    company_name = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    full_address = serializers.CharField(required=False, allow_null=True)
    address_id = serializers.IntegerField(required=False, allow_null=True)
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, required=False, allow_null=True)
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, default=1)
    selected_options = SelectedOptionInputSerializer(many=True, required=False, default=list)

class ChangeStatusSerializer(serializers.Serializer):
    status_code = serializers.CharField(required=True, help_text="کد سیستمی وضعیت (مثال: PENDING_INITIAL_ADMIN)")
    description = serializers.CharField(required=False, allow_blank=True)

class BulkActionIdsSerializer(serializers.Serializer):
    order_ids = serializers.ListField(child=serializers.IntegerField(), required=True, allow_empty=False)

class BulkChangeStatusSerializer(BulkActionIdsSerializer):
    status_code = serializers.CharField(required=True)

# ===== سریالایزر جدید برای لیست وضعیت‌ها ===== #
class OrderStatusSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True, default=None)
    
    class Meta:
        model = OrderStatus
        fields = ['id', 'name', 'internal_code', 'status_type', 'group_name', 'sort_order']


class UserAddressSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source="province.name", read_only=True, default=None)
    city_name = serializers.CharField(source="city.name", read_only=True, default=None)
    class Meta:
        model = Address
        fields = ['id', 'address', 'province', 'province_name', 'city', 'city_name'] 

# ===== سریالایزر لیست مشتریان برای سفارش دستی ===== #
class CustomerListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField()
    company = serializers.CharField(source='customer_profile.company', read_only=True, default='', allow_null=True)
    
    addresses = UserAddressSerializer(many=True, read_only=True) 
    
    def get_full_name(self, obj):
        if hasattr(obj, 'customer_profile') and obj.customer_profile:
            return obj.customer_profile.fullname()
        return obj.phone_number

    def get_full_name(self, obj):
        if hasattr(obj, 'customer_profile') and obj.customer_profile:
            return obj.customer_profile.fullname()
        return obj.phone_number

class OrderFinancialSerializer(serializers.ModelSerializer):
    financial_status_display = serializers.CharField(
        source='get_financial_status_display', read_only=True
    )

    class Meta:
        model = Order
        fields = [
            # شناسه و کد سفارش
            'id', 'order_code',

            # فیلدهای مالی اصلی سفارش
            'subtotal', 'discount_amount', 'tax_amount', 'shipping_cost',
            'final_price', 'paid_amount', 'remaining_amount',
            'deposit_required', 'deposit_paid',
            'financial_status', 'financial_status_display',
            'payment_deadline', 'invoice_date', 'settlement_date',

            # مبالغ قدیمی/جایگزین
            'total_price', 'base_products_price',
        ]


class OrderFinancialUpdateSerializer(serializers.Serializer):
    subtotal = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    shipping_cost = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    deposit_required = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    payment_deadline = serializers.DateTimeField(required=False, allow_null=True)
    invoice_date = serializers.DateTimeField(required=False, allow_null=True)
    settlement_date = serializers.DateTimeField(required=False, allow_null=True)
    financial_status = serializers.ChoiceField(
        choices=FinancialStatus.choices,
        required=False,
        help_text="وضعیت مالی جدید (در صورت عدم ارسال، به‌صورت خودکار محاسبه می‌شود)"
    )
