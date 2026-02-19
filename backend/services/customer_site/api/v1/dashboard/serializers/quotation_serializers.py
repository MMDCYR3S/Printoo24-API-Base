from rest_framework import serializers
from core.financial.models import Invoice, Quotation

class QuotationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = ['id', 'status', 'quotation_number']
        read_only_fields = ['id', 'quotation_number']