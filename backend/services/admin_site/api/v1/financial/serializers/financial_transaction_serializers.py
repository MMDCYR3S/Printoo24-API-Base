from rest_framework import serializers
from apps.financial.models import Transaction

class TransactionDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل تراکنش """
    user_name = serializers.CharField(source='user.username', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionCreateInputSerializer(serializers.Serializer):
    """ ورودی ایجاد تراکنش دستی """
    invoice_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    method = serializers.ChoiceField(choices=Transaction.METHOD_CHOICES)
    tracking_code = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False)
    dest_account = serializers.CharField(required=False, allow_blank=True)
    receipt_image = serializers.ImageField(required=False)

class TransactionUpdateSerializer(serializers.ModelSerializer):
    """ ورودی ویرایش تراکنش (ModelSerializer برای هندل کردن Put/Patch) """
    class Meta:
        model = Transaction
        fields = ['amount', 'method', 'tracking_code', 'payment_date', 'dest_account', 'receipt_image']
        
class TransactionVerifySerializer(serializers.Serializer):
    """ ورودی تایید یا رد تراکنش """
    approved = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
