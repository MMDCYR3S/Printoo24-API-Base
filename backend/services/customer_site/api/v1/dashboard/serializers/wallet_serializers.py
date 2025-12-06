from rest_framework import serializers
from core.models import Wallet, WalletTransaction

# ===== سریالایزر لیست کیف پول ===== #
class WalletListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = ['id', 'user_id', 'username', 'full_name', 'decimal', 'updated_at']

    def get_full_name(self, obj):
        try:
            profile = obj.user.customer_profile
            return f"{profile.first_name} {profile.last_name}"
        except Exception:
            return "-"

# ===== سریالایزر تغییر موجودی (Action) ===== #
class WalletAdjustmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=0, min_value=1)
    action_type = serializers.ChoiceField(choices=[('deposit', 'افزایش'), ('debit', 'کاهش')])

# ===== سریالایزر تاریخچه تراکنش ===== #
class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'type', 'amount', 'amount_after', 'created_at']