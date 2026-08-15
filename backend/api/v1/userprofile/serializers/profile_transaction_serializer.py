from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction
from core.financial.models import Quotation, Payment

class QuotationCustomerSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'customer_name', 'product_name',
            'total_price', 'status', 'status_display', 'valid_until',
        ]

class QuotationApprovalSerializer(serializers.Serializer):
    """
    سریالایزر ورودی برای تأیید پیش‌فاکتور (بدون نیاز به فیلد)
    """
    pass

class WalletPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=0,
        required=False,
        allow_null=True,
        help_text="مبلغ پرداختی (در صورت ارسال نشدن، کل مانده حساب پرداخت می‌شود)"
    )


class PaymentCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_code', 'amount', 'method', 'status',
            'description', 'payment_date', 'approved_at',
        ]

class WalletSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'balance', 'total_deposits', 'total_withdrawals',
            'total_orders', 'credit_limit', 'is_credit_enabled',
            'total_orders_count', 'open_orders_count',
            'status', 'last_payment_date', 'last_invoice_date', 'updated_at',
        ]


class WalletTransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_code', 'transaction_type', 'type_display',
            'amount', 'balance_after', 'description', 'created_at',
        ]