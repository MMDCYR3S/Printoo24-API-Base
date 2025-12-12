from rest_framework import serializers
from core.models import (
    OrderCostReport, OrderCostItem, OrderCostCatalog,
    OrderCostType, Invoice, InvoiceStateLog, InvoiceStatus,
    Transaction
)
from decimal import Decimal

# ========== Cost Catalogs (Master) ========== #
class CostCatalogSerializer(serializers.ModelSerializer):
    """ سریالایزر برای مدیریت لیست هزینه‌های استاندارد (CRUD) """
    type_name = serializers.CharField(source='cost_type.title', read_only=True)
    
    class Meta:
        model = OrderCostCatalog
        fields = ['id', 'cost_type', 'type_name', 'title', 'code', 'is_active']

class CostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCostType
        fields = ['id', 'title', 'code', 'category']

# ========== Cost Items (Details) ========== #
class CostItemInputSerializer(serializers.Serializer):
    """ ورودی برای ایجاد/ویرایش یک قلم هزینه """
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True, max_length=150)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, min_value=1)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('catalog_id') and not attrs.get('custom_title'):
            raise serializers.ValidationError("وارد کردن عنوان یا انتخاب از لیست کاتالوگ الزامی است.")
        return attrs

class CostItemOutputSerializer(serializers.ModelSerializer):
    """ خروجی نمایش قلم هزینه """
    final_title = serializers.CharField(read_only=True)
    type_name = serializers.CharField(source='catalog_item.cost_type.title', read_only=True, allow_null=True)
    
    class Meta:
        model = OrderCostItem
        fields = ['id', 'final_title', 'type_name', 'amount', 'description', 'created_at']

# ========== Cost Reports (Master) ========== #
class CostReportListSerializer(serializers.ModelSerializer):
    """ نمایش لیست خلاصه گزارشات """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = OrderCostReport
        fields = ['id', 'order', 'order_code', 'title', 'total_amount', 'is_approved_by_finance', 'created_by_name', 'created_at', 'items_count']

class CostReportDetailSerializer(serializers.ModelSerializer):
    """ نمایش جزئیات کامل گزارش به همراه اقلام """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    items = CostItemOutputSerializer(many=True, read_only=True)
    attachment_url = serializers.CharField(source='attachment.url', read_only=True, allow_null=True)

    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'order', 'title', 'description', 'total_amount', 
            'is_approved_by_finance', 'finance_note', 
            'created_by_name', 'created_at', 'attachment_url', 'items'
        ]

class CreateCostReportInputSerializer(serializers.Serializer):
    """ ورودی برای ایجاد گزارش جدید """
    order_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)
    items = CostItemInputSerializer(many=True, required=True, min_length=1)

class UpdateCostReportInputSerializer(serializers.Serializer):
    """ ورودی برای ویرایش هدر گزارش """
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)

class ApprovalInputSerializer(serializers.Serializer):
    """ ورودی برای اکشن تایید/رد """
    approve = serializers.BooleanField(required=True)

# --- Micro Serializers ---
class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceStatus
        fields = ['name', 'internal_code', 'color', 'is_considered_paid']

class InvoiceLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    from_status = serializers.CharField(source='from_status.name', read_only=True)
    to_status = serializers.CharField(source='to_status.name', read_only=True)
    class Meta:
        model = InvoiceStateLog
        fields = ['timestamp', 'user_name', 'from_status', 'to_status', 'description']

# --- Transaction Serializers ---
class TransactionInputSerializer(serializers.Serializer):
    """ ورودی ثبت تراکنش دستی """
    amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    method = serializers.ChoiceField(choices=Transaction.METHOD_CHOICES)
    tracking_code = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False)
    dest_account = serializers.CharField(required=False, allow_blank=True)
    receipt_image = serializers.ImageField(required=False)

class TransactionVerifySerializer(serializers.Serializer):
    """ ورودی تایید/رد """
    approved = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

class TransactionDetailSerializer(serializers.ModelSerializer):
    """ خروجی نمایش تراکنش """
    user_name = serializers.CharField(source='user.username', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

# --- Invoice Serializers ---
class InvoiceDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل فاکتور """
    status = InvoiceStatusSerializer(read_only=True)
    transactions = TransactionDetailSerializer(many=True, read_only=True)
    logs = InvoiceLogSerializer(many=True, read_only=True)
    # اطلاعات خلاصه مشتری
    customer_name = serializers.CharField(source='order.user.username', read_only=True) 
    order_code = serializers.CharField(source='order.order_code', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order_code', 'customer_name', 'status',
            'items_amount', 'services_amount', 'tax_amount', 'discount_amount', 'final_amount',
            'paid_amount', 'remaining_amount', 'invoice_type',
            'issued_at', 'due_date', 'transactions', 'logs'
        ]

class InvoiceUpdateInputSerializer(serializers.Serializer):
    """ ورودی ویرایش متادیتای فاکتور """
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)

class TransactionUpdateInputSerializer(serializers.Serializer):
    """ ورودی ویرایش تراکنش (شبیه ایجاد است اما همه فیلدها اختیاری) """
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    method = serializers.ChoiceField(choices=Transaction.METHOD_CHOICES, required=False)
    tracking_code = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False)
    dest_account = serializers.CharField(required=False, allow_blank=True)
    receipt_image = serializers.ImageField(required=False)
