from rest_framework import serializers
from apps.order.models import OrderCostSheet, OrderCostReport, OrderCostItem, OrderCostCategory

# ========================================== #
# ========== 1. Cost Catalog Serializers === #
# ========================================== #
class CostCatalogSerializer(serializers.ModelSerializer):
    """ برای نمایش لیست و جزئیات """
    class Meta:
        model = OrderCostCategory
        fields = ['id', 'title', 'slug', 'cost_type']

class CostCatalogInputSerializer(serializers.Serializer):
    """ ورودی ایجاد و ویرایش دسته‌بندی """
    title = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=50)
    cost_type = serializers.CharField(max_length=50)

# ========================================== #
# ========== 2. Cost Report Serializers ==== #
# ========================================== #
class OrderCostItemSerializer(serializers.ModelSerializer):
    catalog_title = serializers.CharField(source='catalog_item.title', read_only=True)
    catalog_id = serializers.IntegerField(source='catalog_item.id', read_only=True)
    
    class Meta:
        model = OrderCostItem
        fields = ['id', 'custom_title', 'catalog_id', 'catalog_title', 'amount', 'description']

class OrderCostReportDetailSerializer(serializers.ModelSerializer):
    """ جزئیات کامل یک گزارش هزینه برای مشاهده """
    items = OrderCostItemSerializer(many=True, read_only=True)
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    cost_type_display = serializers.CharField(source='cost_type.title', read_only=True)
    
    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'sheet', 'title', 'cost_type', 'cost_type_display',
            'submitter_name', 'created_at', 
            'is_approved', 'items', 'description'
        ]

class OrderCostReportListSerializer(serializers.ModelSerializer):
    """ لیست خلاصه گزارشات """
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    cost_type_display = serializers.CharField(source='cost_type.title', read_only=True)
    
    class Meta:
        model = OrderCostReport
        fields = ['id', 'title', 'cost_type', 'cost_type_display', 'submitter_name', 'is_approved', 'created_at']

class CostItemInputSerializer(serializers.Serializer):
    """ ورودی ایجاد/ویرایش آیتم """
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2) 
    description = serializers.CharField(required=False, allow_blank=True)

class CreateReportInputSerializer(serializers.Serializer):
    """ ورودی ایجاد دستی گزارش """
    order_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=200)
    cost_type = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(child=CostItemInputSerializer(), min_length=1)

class UpdateReportInputSerializer(serializers.ModelSerializer):
    """ ورودی ویرایش هدر گزارش """
    class Meta:
        model = OrderCostReport
        fields = ['title', 'cost_type', 'description']

# ========================================== #
# ========== 3. Cost Sheet Serializers ===== #
# ========================================== #
class OrderCostSheetSerializer(serializers.ModelSerializer):
    """ سند کل بهای تمام شده (خروجی) """
    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'order', 'is_locked', 
            'total_material_cost', 'total_service_cost', 
            'total_shipping_cost', 'total_overhead_cost',
            'final_total_cost', 'revenue_amount', 'net_profit', 'profit_margin_percent'
        ]

class CreateSheetInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)

class UpdateSheetInputSerializer(serializers.ModelSerializer):
    """ ویرایش سند مالی (مثلا باز کردن قفل یا تغییرات دستی خاص) """
    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'order', 'is_locked', 
            'total_material_cost', 'total_service_cost', 
            'total_shipping_cost', 'total_overhead_cost',
            'final_total_cost', 'revenue_amount', 'net_profit', 'profit_margin_percent'
        ]

# ========================================== #
# ========== 4. Action Serializers ========= #
# ========================================== #
class ApproveReportInputSerializer(serializers.Serializer):
    approve = serializers.BooleanField(required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
