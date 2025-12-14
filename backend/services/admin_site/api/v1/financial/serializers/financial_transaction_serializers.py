from rest_framework import serializers
from core.models import Transaction

class TransactionDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionInputSerializer(serializers.Serializer):
    """ ورودی ثبت/ویرایش تراکنش """
    invoice_id = serializers.IntegerField(required=False, help_text="فقط هنگام ایجاد الزامی است")
    amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    method = serializers.ChoiceField(choices=Transaction.METHOD_CHOICES)
    tracking_code = serializers.CharField(required=False, allow_blank=True)
    payment_date = serializers.DateTimeField(required=False)
    dest_account = serializers.CharField(required=False, allow_blank=True)
    receipt_image = serializers.ImageField(required=False)

class TransactionVerifySerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)