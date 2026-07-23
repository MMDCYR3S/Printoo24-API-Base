from rest_framework import serializers
from core.financial.models import Quotation, Invoice

# ================= QUOTATION SERIALIZERS ================= #

class QuotationSerializer(serializers.ModelSerializer):
    # ===== سریالایزر کامل برای نمایش و ساخت ===== #
    class Meta:
        model = Quotation
        fields = '__all__'
        read_only_fields = ['id', 'quotation_number', 'created_by', 'converted_order', 'status']

class QuotationStatusSerializer(serializers.ModelSerializer):
    # ===== سریالایزر مخصوص تغییر وضعیت ===== #
    class Meta:
        model = Quotation
        fields = ['id', 'status', 'quotation_number']
        read_only_fields = ['id', 'quotation_number']


# ================= INVOICE SERIALIZERS ================= #

class InvoiceSerializer(serializers.ModelSerializer):
    # ===== سریالایزر کامل برای فاکتور ===== #
    remaining_amount = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'order', 'invoice_number', 'issued_at', 'finalized_at', 'remaining_amount', 'is_paid']

class InvoiceStatusSerializer(serializers.ModelSerializer):
    # ===== سریالایزر مخصوص تغییر وضعیت ===== #
    class Meta:
        model = Invoice
        fields = ['id', 'status', 'invoice_number', 'finalized_at']
        read_only_fields = ['id', 'invoice_number', 'finalized_at']