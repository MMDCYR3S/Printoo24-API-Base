from rest_framework import serializers
from core.models import Quotation, QuotationItem

class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['id', 'product_name', 'description', 'quantity', 'unit_price']

class QuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Quotation
        fields = '__all__'

class CreateQuotationInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    valid_until = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_blank=True)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    items = QuotationItemSerializer(many=True)

class ConvertQuotationInputSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=True)
