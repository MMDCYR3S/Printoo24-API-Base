from rest_framework import serializers
from core.models import Invoice, InvoiceStateLog

# ========== Invoice Log Serializer ========== #
class InvoiceLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = InvoiceStateLog
        fields = ['timestamp', 'user_name', 'from_status', 'to_status', 'description']

class InvoiceDetailSerializer(serializers.ModelSerializer):
    logs = InvoiceLogSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='order.user.username', read_only=True) 
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    # ===== نمایش وضعیت فاکتور ===== #
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order_code', 'customer_name', 
            'status', 'status_display',
            'items_amount', 'services_amount', 'tax_amount', 'discount_amount', 'final_amount',
            'paid_amount', 'remaining_amount',
            'issued_at', 'due_date', 'description', 'logs'
        ]

class InvoiceUpdateSerializer(serializers.ModelSerializer):
    """ ورودی ویرایش کامل فاکتور """
    class Meta:
        model = Invoice
        fields = [
            'items_amount', 'services_amount', 'tax_amount', 'discount_amount', 'final_amount',
            'due_date', 'description'
        ]
        extra_kwargs = {
            'items_amount': {'required': False},
            'services_amount': {'required': False},
            'tax_amount': {'required': False},
            'discount_amount': {'required': False},
            'final_amount': {'required': False},
        }

class CreateInvoiceInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
