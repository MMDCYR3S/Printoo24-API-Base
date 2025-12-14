from rest_framework import serializers
from core.models import OrderCostSheet, OrderCostReport, OrderCostItem, OrderCostCategory

# ========================================== #
# ========== 1. Cost Catalog Serializer ==== #
# ========================================== #
class CostCatalogSerializer(serializers.ModelSerializer):
    """ مدیریت دسته‌بندی هزینه‌ها """
    class Meta:
        model = OrderCostCategory
        fields = ['id', 'title', 'slug', 'cost_type']

# ========================================== #
# ========== 2. Cost Report Serializers ==== #
# ========================================== #
class OrderCostItemSerializer(serializers.ModelSerializer):
    catalog_title = serializers.CharField(source='catalog_item.title', read_only=True)
    
    class Meta:
        model = OrderCostItem
        fields = ['id', 'custom_title', 'catalog_title', 'amount', 'quantity', 'description']

class OrderCostReportDetailSerializer(serializers.ModelSerializer):
    """ جزئیات کامل یک گزارش هزینه برای تایید """
    items = OrderCostItemSerializer(many=True, read_only=True)
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'title', 'department', 'cost_type', 
            'submitter_name', 'created_at', 
            'is_approved', 'rejection_reason', 'status_display',
            'items', 'description'
        ]

class OrderCostReportListSerializer(serializers.ModelSerializer):
    """ لیست خلاصه گزارشات """
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    
    class Meta:
        model = OrderCostReport
        fields = ['id', 'title', 'department', 'cost_type', 'submitter_name', 'is_approved', 'created_at']

# ========================================== #
# ========== 3. Cost Sheet Serializer ====== #
# ========================================== #
class OrderCostSheetSerializer(serializers.ModelSerializer):
    """ سند کل بهای تمام شده """
    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'is_locked', 
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