from rest_framework import serializers
from core.models import OrderCostReport, OrderCostItem, OrderCostCatalog, OrderCostType
from decimal import Decimal

# ========== Cost Catalogs (Master) ========== #
class CostCatalogSerializer(serializers.ModelSerializer):
    """ سریالایزر برای مدیریت لیست هزینه‌های استاندارد (CRUD) """
    type_name = serializers.CharField(source='cost_type.title', read_only=True)
    
    class Meta:
        model = OrderCostCatalog
        fields = ['id', 'cost_type', 'type_name', 'title', 'code', 'is_active']

class CostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderCostType
        fields = ['id', 'title', 'code', 'category']

# ========== Cost Items (Details) ========== #
class CostItemInputSerializer(serializers.Serializer):
    """ ورودی برای ایجاد/ویرایش یک قلم هزینه """
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True, max_length=150)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, min_value=1)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get('catalog_id') and not attrs.get('custom_title'):
            raise serializers.ValidationError("وارد کردن عنوان یا انتخاب از لیست کاتالوگ الزامی است.")
        return attrs

class CostItemOutputSerializer(serializers.ModelSerializer):
    """ خروجی نمایش قلم هزینه """
    final_title = serializers.CharField(read_only=True)
    type_name = serializers.CharField(source='catalog_item.cost_type.title', read_only=True, allow_null=True)
    
    class Meta:
        model = OrderCostItem
        fields = ['id', 'final_title', 'type_name', 'amount', 'description', 'created_at']

# ========== Cost Reports (Master) ========== #
class CostReportListSerializer(serializers.ModelSerializer):
    """ نمایش لیست خلاصه گزارشات """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    order_code = serializers.CharField(source='order.order_code', read_only=True)
    items_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = OrderCostReport
        fields = ['id', 'order', 'order_code', 'title', 'total_amount', 'is_approved_by_finance', 'created_by_name', 'created_at', 'items_count']

class CostReportDetailSerializer(serializers.ModelSerializer):
    """ نمایش جزئیات کامل گزارش به همراه اقلام """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    items = CostItemOutputSerializer(many=True, read_only=True)
    attachment_url = serializers.CharField(source='attachment.url', read_only=True, allow_null=True)

    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'order', 'title', 'description', 'total_amount', 
            'is_approved_by_finance', 'finance_note', 
            'created_by_name', 'created_at', 'attachment_url', 'items'
        ]

class CreateCostReportInputSerializer(serializers.Serializer):
    """ ورودی برای ایجاد گزارش جدید """
    order_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)
    items = CostItemInputSerializer(many=True, required=True, min_length=1)

class UpdateCostReportInputSerializer(serializers.Serializer):
    """ ورودی برای ویرایش هدر گزارش """
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False)

class ApprovalInputSerializer(serializers.Serializer):
    """ ورودی برای اکشن تایید/رد """
    approve = serializers.BooleanField(required=True)
