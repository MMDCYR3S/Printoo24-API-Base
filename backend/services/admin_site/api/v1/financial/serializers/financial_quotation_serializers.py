from rest_framework import serializers
from core.models import Quotation

class QuotationDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Quotation
        fields = '__all__'

class CreateQuotationInputSerializer(serializers.Serializer):
    """ ورودی ایجاد پیش‌فاکتور """
    # فیلد جدید: انتخاب مشتری
    customer_id = serializers.IntegerField(required=True, help_text="شناسه کاربری مشتری")
    title = serializers.CharField(max_length=200)
    valid_until = serializers.DateTimeField()
    description = serializers.CharField(required=False, allow_blank=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    final_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False, default=0)

class UpdateQuotationInputSerializer(serializers.Serializer):
    """ ورودی ویرایش پیش‌فاکتور """
    title = serializers.CharField(required=False)
    valid_until = serializers.DateTimeField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=0)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    final_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=False)

class ConvertQuotationInputSerializer(serializers.Serializer):
    """ ورودی برای اتصال پیش‌فاکتور به یک سفارش موجود و صدور فاکتور """
    order_id = serializers.IntegerField(required=True, help_text="شناسه سفارش موجود که فاقد فاکتور است")
