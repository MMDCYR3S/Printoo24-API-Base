import json
from rest_framework import serializers
from apps.order.models import (
    OrderFinancialSheet, OrderFinancialReport, OrderFinancialItem, 
    OrderFinancialAttachment, OrderFinancialType
)

# ========== 1. Base / Read Serializers ========== #
class OrderFinancialAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.FileField(source='file', read_only=True)
    class Meta:
        model = OrderFinancialAttachment
        fields = ['id', 'title', 'file_url', 'created_at']

class OrderFinancialItemSerializer(serializers.ModelSerializer):
    """ نمایش اقلام هزینه (Output) """
    catalog_title = serializers.CharField(source='category.title', read_only=True, default="سایر/دستی")
    
    class Meta:
        model = OrderFinancialItem
        fields = [
            'id', 'custom_title', 'catalog_title', 
            'amount', 'description'
        ]

class OrderFinancialReportSerializer(serializers.ModelSerializer):
    """ نمایش جزئیات یک گزارش مالی """
    items = OrderFinancialItemSerializer(many=True, read_only=True)
    attachments = OrderFinancialAttachmentSerializer(many=True, read_only=True)
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    financial_tag_display = serializers.CharField(source='financial_tag.title', read_only=True)
    nature_display = serializers.CharField(source='get_nature_display', read_only=True)

    class Meta:
        model = OrderFinancialReport
        fields = [
            'id', 'title', 'nature', 'nature_display', 
            'financial_tag', 'financial_tag_display',
            'is_approved', 'submitter_name', 'created_at',
            'items', 'attachments'
        ]

class OrderFinancialSheetSerializer(serializers.ModelSerializer):
    """ 
    نمایش سند مادر (Ledger).
    شامل اعداد تجمیعی و لیست گزارش‌های تایید شده/نشده.
    """
    reports = OrderFinancialReportSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderFinancialSheet
        fields = [
            'id', 'is_locked', 
            'total_material_cost', 'total_service_cost',
            'total_shipping_cost', 'total_overhead_cost',
            'final_total_cost', 'revenue_amount', 'net_profit', 'profit_margin_percent',
            'created_at', 'reports'
        ]

# ========== 2. Write / Input Serializers ========== #
class OrderFinancialItemInputSerializer(serializers.Serializer):
    """ اعتبارسنجی ورودی هر قلم هزینه در هنگام ثبت گزارش """
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('catalog_id') and not data.get('custom_title'):
            raise serializers.ValidationError("وارد کردن 'عنوان دستی' یا انتخاب 'دسته‌بندی' الزامی است.")
        return data

class OrderFinancialReportSubmitSerializer(serializers.Serializer):
    """ 
    ورودی اصلی برای ثبت گزارش توسط واحدها (انبار، چاپ و...).
    جایگزین متد قدیمی Add Items.
    """
    financial_tag_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    # ===== اقلام ===== #
    items = serializers.ListField(
        child=OrderFinancialItemInputSerializer(),
        required=False, allow_empty=True,
        allow_null=True
    )
    # ===== پیوست ها ===== #
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False, write_only=True
    )

# ========== Order Financial Type List Serializer ========== #
class OrderFinancialTypeListSerializer(serializers.ModelSerializer):
    """ لیست نوع هزینه ها """
    class Meta:
        model = OrderFinancialType
        fields = ['id', 'title']
