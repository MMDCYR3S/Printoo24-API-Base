import json
from rest_framework import serializers
from core.models import OrderPrintReport, OrderPrintItem, OrderPrintAttachment

# ========== Sub-Serializers ========== #
class PrintItemInputSerializer(serializers.Serializer):
    """ ورودی هر قلم مصرفی """
    material_type = serializers.ChoiceField(choices=OrderPrintItem.MaterialType.choices)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

class PrintItemOutputSerializer(serializers.ModelSerializer):
    """ خروجی نمایش اقلام """
    material_type_display = serializers.CharField(source='get_material_type_display', read_only=True)
    
    class Meta:
        model = OrderPrintItem
        fields = ['id', 'material_type', 'custom_title', 'price', 'material_type_display', 'description']

class PrintAttachmentSerializer(serializers.ModelSerializer):
    """ خروجی نمایش فایل‌ها """
    file_url = serializers.FileField(source='file', read_only=True)
    class Meta:
        model = OrderPrintAttachment
        fields = ['id', 'title', 'file_url']

# ===== Main Serializers =====

class PrintReportCreateSerializer(serializers.Serializer):
    """ ورودی ایجاد گزارش مصرف (شامل JSON اقلام و لیست فایل‌ها) """
    title = serializers.CharField(max_length=200, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    items = serializers.JSONField(help_text="لیست اقلام به فرمت JSON")
    
    # دریافت فایل‌ها به صورت لیست
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    def validate_items(self, value):
        # تبدیل JSON String به List (برای ریکوئست‌های Multipart)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                raise serializers.ValidationError("فرمت JSON اقلام نامعتبر است.")
        
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("لیست اقلام نمی‌تواند خالی باشد.")
        
        # اعتبارسنجی داخلی هر آیتم
        valid_items = []
        for item_data in value:
            item_serializer = PrintItemInputSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            valid_items.append(item_serializer.validated_data)
            
        return valid_items

class PrintReportDetailSerializer(serializers.ModelSerializer):
    """ خروجی کامل گزارش مصرف """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    items = PrintItemOutputSerializer(many=True, read_only=True)
    attachments = PrintAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = OrderPrintReport
        fields = ['id', 'title', 'description', 'created_by_name', 'created_at', 'items', 'attachments']
        
class PrintItemUpdateSerializer(serializers.Serializer):
    """ 
    ورودی آیتم در حالت ویرایش.
    تفاوت با Create: فیلد id اختیاری است (اگر باشد Update، نباشد Create).
    """
    id = serializers.IntegerField(required=False, allow_null=True) # <--- مهم
    material_type = serializers.ChoiceField(choices=OrderPrintItem.MaterialType.choices)
    description = serializers.CharField(required=False, allow_blank=True)

class PrintReportUpdateSerializer(serializers.Serializer):
    """ ورودی ویرایش گزارش """
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    
    items = serializers.JSONField(required=False ,help_text="لیست اقلام (با یا بدون ID)")
    
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    def validate_items(self, value):
        # تبدیل JSON String به List (مشابه قبل)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                raise serializers.ValidationError("فرمت JSON اقلام نامعتبر است.")
        
        if not isinstance(value, list):
            raise serializers.ValidationError("لیست اقلام معتبر نیست.")
        
        # اعتبارسنجی داخلی
        valid_items = []
        for item_data in value:
            item_serializer = PrintItemUpdateSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            valid_items.append(item_serializer.validated_data)
            
        return valid_items
    