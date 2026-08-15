from rest_framework import serializers
from core.financial.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """
    سریالایزر کامل فاکتور برای نمایش و دریافت ورودی
    """
    remaining_amount = serializers.DecimalField(
        max_digits=18, decimal_places=0, read_only=True,
        help_text="مانده حساب فاکتور (final_amount - paid_amount)"
    )
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'order', 'invoice_number',
            'paid_amount', 'items_amount', 'services_amount',
            'tax_amount', 'discount_amount', 'final_amount',
            'description', 'status', 'issued_at', 'due_date', 'finalized_at',
            'remaining_amount', 'is_paid',
        ]
        read_only_fields = [
            'id', 'order', 'invoice_number', 'issued_at',
            'finalized_at', 'remaining_amount', 'is_paid',
        ]


class InvoiceStatusSerializer(serializers.ModelSerializer):
    """
    سریالایزر مخصوص تغییر وضعیت فاکتور
    """
    class Meta:
        model = Invoice
        fields = ['id', 'status', 'invoice_number', 'finalized_at']
        read_only_fields = ['id', 'invoice_number', 'finalized_at']