from rest_framework import serializers
from core.models import Invoice, InvoiceStatus, InvoiceStateLog

class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceStatus
        fields = ['name', 'internal_code', 'is_considered_paid']

class InvoiceLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    from_status = serializers.CharField(source='from_status.name', read_only=True)
    to_status = serializers.CharField(source='to_status.name', read_only=True)
    class Meta:
        model = InvoiceStateLog
        fields = ['timestamp', 'user_name', 'from_status', 'to_status', 'description']

class InvoiceDetailSerializer(serializers.ModelSerializer):
    status = InvoiceStatusSerializer(read_only=True)
    logs = InvoiceLogSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='order.user.username', read_only=True) 
    order_code = serializers.CharField(source='order.order_code', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'order_code', 'customer_name', 'status',
            'items_amount', 'services_amount', 'tax_amount', 'discount_amount', 'final_amount',
            'paid_amount', 'remaining_amount',
            'issued_at', 'due_date', 'description', 'logs'
        ]

class InvoiceUpdateInputSerializer(serializers.Serializer):
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)

class CreateInvoiceInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
