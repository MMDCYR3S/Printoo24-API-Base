from rest_framework import serializers
from apps.order.models import OrderFinancialSheet
from apps.logistics.models import OrderPackage, OrderShipment
from decimal import Decimal

# ========== PACKAGE SERIALIZERS ========== #
class PackageInputSerializer(serializers.ModelSerializer):
    """ ورودی: اطلاعات فیزیکی و اطلاعات گیرنده (لیبل) """
    class Meta:
        model = OrderPackage
        fields = ["customer_name", "phone_number", "address", "order_image", "content_summary"]
        
class PackageOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل بسته‌بندی """
    label_code = serializers.CharField(read_only=True)
    class Meta:
        model = OrderPackage
        fields = '__all__'

# ========== COST SERIALIZERS ========== #
class LogisticFinancialItemInputSerializer(serializers.Serializer):
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True, max_length=150)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, min_value=Decimal('1'))
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)
    
class CreateLogisticFinancialReportInputSerializer(serializers.Serializer):
    """ ورودی برای API ثبت گزارش هزینه لجستیک """
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)
    items = LogisticFinancialItemInputSerializer(many=True, required=True, min_length=1)

class FinancialReportOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل گزارش هزینه """

    class Meta:
        model = OrderFinancialSheet
        fields = "__all__"

# ========== SHIPMENT SERIALIZERS ========== #
class CreateShipmentInputSerializer(serializers.ModelSerializer):
    """ ورودی برای API ایجاد مرسوله جدید """
    packages = PackageInputSerializer(many=True, required=True, min_length=1)
    delivery_method = serializers.ChoiceField(choices=OrderShipment.METHOD_CHOICES, required=True)

    class Meta:
        model = OrderShipment
        fields = [
            'order',
            'delivery_method',
            'driver_info',
            'shipping_cost_real',
            'expected_delivery_date',
            'packages',
        ]

class UpdateShipmentInputSerializer(serializers.ModelSerializer):
    """ ورودی برای API به‌روزرسانی مرسوله (PATCH) """
    class Meta:
        model = OrderShipment
        fields = [
            'order',
            'delivery_method',
            'destination_address',
            'driver_info',
            'shipping_cost_real',
            'expected_delivery_date',
            'dispatched_at',
            'delivered_at',
            'packages',
        ]
        

class ShipmentStatusInputSerializer(serializers.Serializer):
    """ ورودی برای API تغییر وضعیت مرسوله """
    new_status_code = serializers.ChoiceField(
        choices=OrderShipment.SHIPMENT_STATUS, 
        required=True,
        help_text="وضعیت جدید مرسوله (مانند 'delivered', 'dispatched')"
    )

class ShipmentOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل مرسوله """
    packages = PackageOutputSerializer(many=True, read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    
    class Meta:
        model = OrderShipment
        fields = [
            'id',
            'order',
            'delivery_method',
            'delivery_method_display',
            'destination_address',
            'driver_info',
            'shipping_cost_real',
            'expected_delivery_date',
            'dispatched_at',
            'delivered_at',
            'packages',
            'status',
            'tracking_code',
        ]
        

