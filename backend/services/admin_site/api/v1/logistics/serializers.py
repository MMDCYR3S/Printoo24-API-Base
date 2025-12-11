from rest_framework import serializers
from core.models import OrderShipment, OrderPackage, OrderCostReport
from decimal import Decimal

# --- Micro Serializers (Used for Nested Fields) ---

class PackageInputSerializer(serializers.Serializer):
    """ ورودی برای تعریف یک بسته جدید """
    weight_grams = serializers.IntegerField(min_value=1, help_text="وزن بسته (گرم)")
    width_cm = serializers.IntegerField(min_value=1, help_text="عرض بسته (سانتی‌متر)")
    length_cm = serializers.IntegerField(min_value=1, help_text="طول بسته (سانتی‌متر)")
    height_cm = serializers.IntegerField(min_value=1, help_text="ارتفاع بسته (سانتی‌متر)")
    content_summary = serializers.CharField(required=False, allow_blank=True, max_length=1024)

class LogisticCostItemInputSerializer(serializers.Serializer):
    """ ورودی برای یک قلم هزینه در گزارش """
    catalog_id = serializers.IntegerField(required=False, allow_null=True, help_text="شناسه کاتالوگ هزینه (اختیاری)")
    custom_title = serializers.CharField(required=False, allow_blank=True, max_length=150)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, min_value=Decimal('1'), help_text="مبلغ")
    description = serializers.CharField(required=False, allow_blank=True, max_length=255)

# --- Shipment Input/Output ---

class CreateShipmentInputSerializer(serializers.Serializer):
    """ ورودی برای API ایجاد مرسوله جدید """
    delivery_method_id = serializers.IntegerField(required=True, help_text="شناسه روش ارسال")
    destination_address_id = serializers.IntegerField(required=False, help_text="شناسه آدرس مقصد جدید")
    tracking_code = serializers.CharField(required=False, allow_blank=True, max_length=100)
    shipping_cost_real = serializers.DecimalField(
        required=False, max_digits=15, decimal_places=0,
        min_value=0, help_text="هزینه واقعی ارسال"
    )
    expected_delivery_date = serializers.DateTimeField(required=False, allow_null=True)
    
    # Nested Input: بسته‌ها
    packages = PackageInputSerializer(many=True, required=True, min_length=1)

class UpdateShipmentInputSerializer(serializers.Serializer):
    """ ورودی برای API به‌روزرسانی مرسوله (PATCH) """
    tracking_code = serializers.CharField(required=False, allow_blank=True, max_length=100)
    driver_info = serializers.CharField(required=False, allow_blank=True, max_length=1024)
    shipping_cost_real = serializers.DecimalField(required=False, max_digits=15, decimal_places=0, min_value=0)
    destination_address_id = serializers.IntegerField(required=False)

class ShipmentStatusInputSerializer(serializers.Serializer):
    """ ورودی برای API تغییر وضعیت مرسوله """
    new_status_code = serializers.ChoiceField(
        choices=OrderShipment.SHIPMENT_STATUS, 
        required=True,
        help_text="وضعیت جدید مرسوله (مانند 'delivered', 'dispatched')"
    )

# --- Shipment Output (General) ---

class PackageOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل بسته‌بندی """
    label_code = serializers.CharField(read_only=True)
    class Meta:
        model = OrderPackage
        fields = ['id', 'label_code', 'box_number', 'weight_grams', 'width_cm', 'length_cm', 'height_cm', 'content_summary']

class ShipmentOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل مرسوله (برای نمایش جزئیات کامل) """
    delivery_method = serializers.CharField(source='delivery_method.title', read_only=True)
    packages = PackageOutputSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderShipment
        fields = '__all__' 

# --- Cost Report Input/Output ---

class CreateLogisticCostReportInputSerializer(serializers.Serializer):
    """ ورودی برای API ثبت گزارش هزینه لجستیک """
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)
    
    items = LogisticCostItemInputSerializer(many=True, required=True, min_length=1)

class CostReportOutputSerializer(serializers.ModelSerializer):
    """ خروجی مدل گزارش هزینه """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = OrderCostReport
        fields = ['id', 'title', 'created_by_name', 'total_amount', 'is_approved_by_finance', 'created_at']
