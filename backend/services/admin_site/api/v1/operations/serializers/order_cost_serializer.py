import json
from rest_framework import serializers
from core.models import OrderCostReport, OrderCostItem, OrderCostType

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
    ورودی برای ساخت گزارش.
    نکته مهم: اگر درخواست Multipart (فایل) باشد، ارسال لیست items کمی پیچیده است.
    ما اینجا فرض می‌کنیم items به صورت JSON String ارسال می‌شود و آن را پارس می‌کنیم.
    """
    items = serializers.JSONField(help_text="لیست اقلام به صورت JSON Array")
    attachment = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = OrderCostReport
        fields = ['title', 'description', 'attachment', 'items']

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
    """
    خروجی کامل گزارش برای نمایش به مدیر مالی یا اپراتور.
    """
    items = OrderCostItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=0, read_only=True)

    class Meta:
        model = OrderCostReport
        fields = [
            'id', 
            'title', 
            'description', 
            'total_amount', 
            'is_approved_by_finance', 
            'finance_note',
            'created_by_name', 
            'created_at', 
            'attachment', 
            'items'
        ]

# ========== Order Cost Type Serializers ========== #
class CostTypeInputSerializer(serializers.ModelSerializer):
    """ ورودی برای ایجاد/ویرایش نوع هزینه """
    class Meta:
        model = OrderCostType
        fields = ['title', 'code', 'category', 'is_deduction']
        
    def validate_code(self, value):
        """ نرمال‌سازی کد سیستمی """
        return value.upper().strip()

class CostTypeDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل نوع هزینه """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = OrderCostType
        fields = ['id', 'title', 'code', 'category', 'category_display', 'is_deduction', 'created_at']
