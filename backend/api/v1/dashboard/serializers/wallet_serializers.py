from rest_framework import serializers
from apps.accounts.models import Wallet, WalletTransaction

# ===== سریالایزر لیست کیف پول ===== #
class WalletListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    phone_number = serializers.CharField(source='user.phone_number')
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = ['id', 'user_id', 'phone_number', 'full_name', 'balance', 'updated_at']

    def get_full_name(self, obj):
        try:
            profile = obj.user.customer_profile
            return f"{profile.first_name} {profile.last_name}"
        except Exception:
            return "-"

# ===== اصلاح سریالایزر تغییر موجودی ===== #
class WalletAdjustmentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        required=True, 
        help_text="شناسه کاربری که قصد تغییر موجودی او را دارید"
    )
    amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=1,
        help_text="مبلغ تراکنش به عدد اعشاری"
    )
    action_type = serializers.ChoiceField(
        choices=[('deposit', 'واریز (افزایش)'), ('debit', 'برداشت (کاهش)')],
        help_text="نوع عملیات: deposit برای افزایش، debit برای کاهش"
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="توضیحات تراکنش (اختیاری)"
    )

    class Meta:
        swagger_schema_fields = {
            "example": {
                "user_id": 15,
                "amount": "50000.00",
                "action_type": "deposit",
                "description": "هدیه مدیریت"
            }
        }

# ===== سریالایزر تاریخچه تراکنش ===== #
class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'amount_after', 'created_at']