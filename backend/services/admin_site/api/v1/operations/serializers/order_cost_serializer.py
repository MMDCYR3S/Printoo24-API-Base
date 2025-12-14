import json
from rest_framework import serializers
from core.models import (
    OrderCostSheet, OrderCostReport, OrderCostItem, 
    OrderCostAttachment
)

# ========== 1. Base / Read Serializers ========== #
class OrderCostAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)
    class Meta:
        model = OrderCostAttachment
        fields = ['id', 'title', 'file_url', 'created_at']

class OrderCostItemSerializer(serializers.ModelSerializer):
    """ نمایش اقلام هزینه (Output) """
    cost_type_display = serializers.CharField(source='catalog_item.title', read_only=True, default="سایر/دستی")
    
    class Meta:
        model = OrderCostItem
        fields = [
            'id', 'custom_title', 'cost_type_display', 
            'quantity', 'unit_price', 'amount', 'description'
        ]

class OrderCostReportSerializer(serializers.ModelSerializer):
    """ نمایش جزئیات یک گزارش هزینه (Journal Entry) """
    items = OrderCostItemSerializer(many=True, read_only=True)
    attachments = OrderCostAttachmentSerializer(many=True, read_only=True)
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    department_display = serializers.CharField(source='get_department_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderCostReport
        fields = [
            'id', 'title', 'department', 'department_display',
            'cost_type', 'status', 'status_display', 'is_approved', 'rejection_reason',
            'submitter_name', 'created_at', 'items', 'attachments'
        ]

class OrderCostSheetSerializer(serializers.ModelSerializer):
    """ 
    نمایش سند مادر (Ledger).
    شامل اعداد تجمیعی و لیست گزارش‌های تایید شده/نشده.
    """
    reports = OrderCostReportSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'is_locked', 
            'total_material_cost', 'total_service_cost',
            'total_shipping_cost', 'total_overhead_cost',
            'final_total_cost', 'revenue_amount', 'net_profit', 'profit_margin_percent',
            'created_at', 'reports'
        ]

# ========== 2. Write / Input Serializers ========== #
class OrderCostItemInputSerializer(serializers.Serializer):
    """ اعتبارسنجی ورودی هر قلم هزینه در هنگام ثبت گزارش """
    category_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=1)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('category_id') and not data.get('custom_title'):
            raise serializers.ValidationError("وارد کردن 'عنوان دستی' یا انتخاب 'دسته‌بندی' الزامی است.")
        return data

class OrderCostReportSubmitSerializer(serializers.Serializer):
    """ 
    ورودی اصلی برای ثبت گزارش توسط واحدها (انبار، چاپ و...).
    جایگزین متد قدیمی Add Items.
    """
    department = serializers.ChoiceField(choices=OrderCostReport.DEPARTMENT_CHOICES)
    cost_type = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    # ===== اقلام ===== #
    items = serializers.ListField(child=OrderCostItemInputSerializer(), allow_empty=False)
    # ===== پیوست ها ===== #
    attachments = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )
