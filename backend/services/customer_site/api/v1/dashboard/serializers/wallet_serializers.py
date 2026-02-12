from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction

# ===== سریالایزر لیست کیف پول ===== #
class WalletListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = ['id', 'user_id', 'username', 'full_name', 'balance', 'updated_at']

    def get_full_name(self, obj):
        try:
            profile = obj.user.customer_profile
            return f"{profile.first_name} {profile.last_name}"
        except Exception:
            return "-"

# ===== سریالایزر تغییر موجودی (Action) ===== #
class WalletAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=0.01,
        help_text="مبلغ تراکنش به عدد اعشاری"
    )
    action_type = serializers.ChoiceField(
        choices=[('deposit', 'واریز (افزایش)'), ('debit', 'برداشت (کاهش)')],
        help_text="نوع عملیات: deposit برای افزایش، debit برای کاهش"
    )

    class Meta:
        swagger_schema_fields = {
            "example": {
                "amount": "50000.00",
                "action_type": "deposit"
            }
        }

# ===== سریالایزر تاریخچه تراکنش ===== #
class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'amount_after', 'created_at']