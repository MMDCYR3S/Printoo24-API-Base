import json
from rest_framework import serializers
from core.models import OrderCostSheet, OrderCostItem, OrderCostCategory, OrderCostAttachment

# ========== Attachment Serializer ========== #
class OrderCostAttachmentSerializer(serializers.ModelSerializer):
    """ سریالایزر نمایش فایل‌های پیوست """
    file_url = serializers.FileField(source='file', read_only=True)
    
    class Meta:
        model = OrderCostAttachment
        fields = ['id', 'title', 'file_url', 'created_at']

# ========== Order Cost Item Serializers ========== #
class OrderCostItemSerializer(serializers.ModelSerializer):
    """
    این سریالایزر هم برای ورودی (داخل لیست) و هم خروجی استفاده می‌شود.
    """
    # ===== ورودی‌ها ===== #
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    
    # ===== خروجی‌ها ===== #
    title_display = serializers.SerializerMethodField()
    cost_type_display = serializers.CharField(source='catalog_item.cost_type.title', read_only=True, default="سایر")

    class Meta:
        model = OrderCostItem
        fields = [
            'id', 
            'catalog_id', 
            'custom_title', 
            'title_display',
            'cost_type_display',
            'amount', 
            'description'
        ]
        read_only_fields = ['id', 'title_display', 'cost_type_display']

    def get_title_display(self, obj):
        """ استفاده از پراپرتی مدل برای نمایش نام نهایی """
        return obj.final_title

    def validate(self, data):
        """ اعتبارسنجی سطح سریالایزر (Fail Fast) """
        if not data.get('catalog_id') and not data.get('custom_title'):
            raise serializers.ValidationError("برای هر قلم هزینه، باید یا کالا از لیست انتخاب شود یا عنوان دستی وارد شود.")
        return data

# ========== Order Cost Report Create Serializer ========== #
class OrderCostReportCreateSerializer(serializers.ModelSerializer):
    """
    ورودی ایجاد گزارش هزینه.
    پشتیبانی از مولتی‌پارت برای چندین فایل و اقلام JSON.
    """
    items = serializers.JSONField(help_text="لیست اقلام به صورت JSON Array")
    
    # دریافت فایل‌ها به صورت لیست
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
        help_text="لیست فایل‌های پیوست"
    )

    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'is_finalized', 'approved_by',
            'total_operational_cost', 'total_material_cost',
            'total_outsourcing_cost','total_overhead_cost',
        ]

    def validate_items(self, value):
        """
        اگر فرمت Multipart باشد، items به صورت رشته می‌آید.
        اینجا مطمئن می‌شویم که تبدیل به لیست دیکشنری شده است.
        """
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                raise serializers.ValidationError("فرمت JSON اقلام نامعتبر است.")
        
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("لیست اقلام نمی‌تواند خالی باشد.")
            
        return value

# ========== Order Cost Report Detail Serializer ========== #
class OrderCostReportDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل گزارش شامل اقلام و پیوست‌ها """
    items = OrderCostItemSerializer(many=True, read_only=True)
    attachments = OrderCostAttachmentSerializer(many=True, read_only=True) # نمایش لیست فایل‌ها
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    total_cost = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)

    class Meta:
        model = OrderCostSheet
        fields = [
            'id', 'is_finalized', 'approved_by',
            'total_operational_cost', 'total_material_cost',
            'total_outsourcing_cost','total_overhead_cost',
            'total_cost', 'created_by_name', 'created_at', 
            'items', 'attachments'
        ]

# ========== Order Cost Type Serializers ========== #
class CostTypeInputSerializer(serializers.ModelSerializer):
    """ ورودی برای ایجاد/ویرایش نوع هزینه """
    class Meta:
        model = OrderCostCategory
        fields = ['title', 'slug', 'cost_type', 'is_deduction']
        
    def validate_slug(self, value):
        """ نرمال‌سازی کد سیستمی """
        return value.upper().strip()

class CostTypeDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل نوع هزینه """
    
    class Meta:
        model = OrderCostCategory
        fields = ['id', 'title', 'slug', 'cost_type', 'created_at']
