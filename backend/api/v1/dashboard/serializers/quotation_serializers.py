from rest_framework import serializers
from core.financial.models import Quotation


class QuotationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_phone = serializers.CharField(source='created_by.phone_number', read_only=True, default=None)
    order_code = serializers.CharField(source='converted_order.order_code', read_only=True, default=None)
    # اتصال به سبد خرید (پیش از تبدیل به سفارش)
    cart_item_id = serializers.IntegerField(source='cart_item.id', read_only=True, default=None)

    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'customer_name', 'product_name',
            'product_image', 'product_snapshot', 'quantity',
            'estimated_delivery_date', 'total_price',
            'status', 'status_display', 'valid_until',
            'created_by', 'created_by_phone', 'converted_order', 'order_code',
            'cart_item_id',
            'created_at', 'updated_at',
        ]


class QuotationCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    customer_name = serializers.CharField(max_length=255, required=False)
    product_name = serializers.CharField(max_length=255, required=False)
    quantity = serializers.IntegerField(required=False, default=1)
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    valid_until = serializers.DateField(required=False, allow_null=True)
    estimated_delivery_date = serializers.DateField(required=False, allow_null=True)
    product_snapshot = serializers.JSONField(required=False, default=dict)


class QuotationUpdateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=255, required=False)
    product_name = serializers.CharField(max_length=255, required=False)
    quantity = serializers.IntegerField(required=False)
    total_price = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    valid_until = serializers.DateField(required=False, allow_null=True)
    estimated_delivery_date = serializers.DateField(required=False, allow_null=True)
    product_snapshot = serializers.JSONField(required=False)


class QuotationStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Quotation.Status.choices, required=True)