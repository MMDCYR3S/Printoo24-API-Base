from rest_framework import serializers
from core.models import Quotation

class QuotationDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Quotation
        fields = '__all__'

class CreateQuotationInputSerializer(serializers.ModelSerializer):
    """ ورودی ایجاد پیش‌فاکتور """
    class Meta:
        model = Quotation
        fields = '__all__'
        read_only_fields = ['created_by', 'status', 'quotation_number', 'created_at', 'updated_at']

class UpdateQuotationInputSerializer(serializers.ModelSerializer):
    """ ورودی ویرایش پیش‌فاکتور """
    class Meta:
        model = Quotation
        fields = '__all__'
        read_only_fields = ["created_by", 'quotation_number', 'created_at', 'updated_at']


class ConvertQuotationInputSerializer(serializers.Serializer):
    """ ورودی برای اتصال پیش‌فاکتور به یک سفارش موجود و صدور فاکتور """
    order_id = serializers.IntegerField(required=True, help_text="شناسه سفارش موجود که فاقد فاکتور است")
