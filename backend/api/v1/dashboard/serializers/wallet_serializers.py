from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    full_name = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)  # پراپرتی status در مدل

    class Meta:
        model = Wallet
        fields = [
            'id', 'user_id', 'phone_number', 'full_name',
            'balance', 'total_deposits', 'total_withdrawals',
            'total_orders', 'credit_limit', 'is_credit_enabled',
            'total_orders_count', 'open_orders_count',
            'status', 'last_payment_date', 'last_invoice_date', 'updated_at',
        ]

    def get_full_name(self, obj):
        try:
            profile = obj.user.customer_profile
            return f"{profile.first_name} {profile.last_name}".strip()
        except Exception:
            return "-"


class WalletAdjustmentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=0,  # هماهنگ با مدل
        min_value=1,
        help_text="مبلغ تراکنش (عدد صحیح دینار)"
    )
    action_type = serializers.ChoiceField(
        choices=[('deposit', 'واریز (افزایش)'), ('debit', 'برداشت (کاهش)')],
        help_text="نوع عملیات"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="توضیحات تراکنش (اختیاری)"
    )


class WalletTransactionSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)

    class Meta:
        model = WalletTransaction
        fields = [
            'id', 'transaction_code', 'transaction_type', 'type_display',
            'amount', 'balance_before', 'balance_after',
            'description', 'created_at',
        ]
