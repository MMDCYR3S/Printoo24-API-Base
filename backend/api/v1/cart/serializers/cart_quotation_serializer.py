from rest_framework import serializers
from core.financial.models import Quotation


class CartQuotationListSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش پیش‌فاکتورهای مرتبط با سبد خرید.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    product_name = serializers.CharField(source='cart_item.product.name', read_only=True, default=None)
    cart_item_id = serializers.IntegerField(source='cart_item.id', read_only=True, default=None)

    class Meta:
        model = Quotation
        fields = [
            'id',
            'quotation_number',
            'product_name',
            'cart_item_id',
            'total_price',
            'quantity',
            'status',
            'status_display',
            'valid_until',
            'created_at',
        ]


class CartQuotationDetailSerializer(serializers.ModelSerializer):
    """
    نمایش جزئیات کامل پیش‌فاکتور مرتبط با یک آیتم سبد خرید.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    product_name = serializers.CharField(source='cart_item.product.name', read_only=True, default=None)
    cart_item_id = serializers.IntegerField(source='cart_item.id', read_only=True, default=None)
    product_snapshot = serializers.JSONField(read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id',
            'quotation_number',
            'product_name',
            'cart_item_id',
            'product_snapshot',
            'quantity',
            'total_price',
            'status',
            'status_display',
            'valid_until',
            'created_at',
            'updated_at',
        ]