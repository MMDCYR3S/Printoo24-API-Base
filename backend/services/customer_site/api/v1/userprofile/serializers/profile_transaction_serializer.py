from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction

# ===== Wallet Serializer ===== #
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'updated_at']

# ===== Wallet Transaction Serializer ===== #
class WalletTransactionSerializer(serializers.ModelSerializer):
    """
    سریالایزر مربوط به تراکنش کیف پول کاربر
    """
    # ===== نمایش نوع تراکنش ===== #
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = WalletTransaction
        fields = [
            'id',
            'transaction_type', 
            'type_display',
            'amount',
            'amount_after',
            'created_at'
        ]
