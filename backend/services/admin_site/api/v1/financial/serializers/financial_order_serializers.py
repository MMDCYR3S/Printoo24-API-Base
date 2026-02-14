from rest_framework import serializers
from apps.order.models import OrderFinancialSheet, OrderFinancialReport, OrderFinancialItem, OrderFinancialCategory, OrderFinancialAttachment

# ========================================== #
# ========== 1. Financial Catalog Serializers === #
# ========================================== #
class FinancialCatalogSerializer(serializers.ModelSerializer):
    """ برای نمایش لیست و جزئیات """
    class Meta:
        model = OrderFinancialCategory
        fields = ['id', 'title', 'slug', 'operation_type']

class FinancialCatalogInputSerializer(serializers.Serializer):
    """ ورودی ایجاد و ویرایش دسته‌بندی """
    title = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=50)
    financial_tag = serializers.CharField(max_length=50)

# ========================================== #
# ========== 2. Financial Report Serializers ==== #
# ========================================== #
class OrderFinancialAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFinancialAttachment
        fields = ["report", "title", "file", "created_at"]

class OrderFinancialItemSerializer(serializers.ModelSerializer):
    catalog_title = serializers.CharField(source='catalog_item.title', read_only=True)
    catalog_id = serializers.IntegerField(source='catalog_item.id', read_only=True)
    
    class Meta:
        model = OrderFinancialItem
        fields = ['id', 'custom_title', 'catalog_id', 'catalog_title', 'amount', 'description']

class OrderFinancialReportDetailSerializer(serializers.ModelSerializer):
    """ جزئیات کامل یک گزارش هزینه برای مشاهده """
    items = OrderFinancialItemSerializer(many=True, read_only=True)
    attachments = OrderFinancialAttachmentSerializer(many=True, read_only=True)
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    financial_tag_display = serializers.CharField(source='financial_tag.title', read_only=True)
    
    class Meta:
        model = OrderFinancialReport
        fields = [
            'id', 'sheet', 'title', 'financial_tag', 'financial_tag_display',
            'submitter_name', 'created_at', 
            'is_approved', 'items', 'attachments', 'description'
        ]

class OrderFinancialReportListSerializer(serializers.ModelSerializer):
    """ لیست خلاصه گزارشات """
    submitter_name = serializers.CharField(source='submitter.username', read_only=True)
    financial_tag_display = serializers.CharField(source='financial_tag.title', read_only=True)
    order_id = serializers.IntegerField(source="sheet.order.id", read_only=True)
    order_code = serializers.CharField(source="sheet.order.order_code", read_only=True)
    
    class Meta:
        model = OrderFinancialReport
        fields = [
            'id', 'order_id', 'order_code',
            'title', 'financial_tag', 'financial_tag_display',
            'submitter_name', 'is_approved', 'created_at'
        ]

class FinancialItemInputSerializer(serializers.Serializer):
    """ ورودی ایجاد/ویرایش آیتم """
    catalog_id = serializers.IntegerField(required=False, allow_null=True)
    custom_title = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2) 
    description = serializers.CharField(required=False, allow_blank=True)

class CreateReportInputSerializer(serializers.Serializer):
    """ ورودی ایجاد دستی گزارش - order_id از URL گرفته می‌شود """
    
    title = serializers.CharField(max_length=200, help_text="عنوان گزارش هزینه")
    financial_tag = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    items = serializers.ListField(
        child=FinancialItemInputSerializer(), 
        required=False, 
        allow_null=True
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False, write_only=True,
        allow_null=True
    )

class UpdateReportInputSerializer(serializers.ModelSerializer):
    """ ورودی ویرایش هدر گزارش """
    class Meta:
        model = OrderFinancialReport
        fields = ['title', 'financial_tag', 'description']

# ========================================== #
# ========== 3. Financial Sheet Serializers ===== #
# ========================================== #
class OrderFinancialSheetSerializer(serializers.ModelSerializer):
    """ سند کل بهای تمام شده (خروجی) """
    class Meta:
        model = OrderFinancialSheet
        fields = [
            'id', 'order', 'is_locked', 'total_material_cost',
            'total_production_cost', 'total_service_cost',
            'total_delivery_cost', 'total_other_cost',
            'final_total_cost', 'total_revenue', 'net_profit',
            'profit_margin_percent'
        ]

class CreateSheetInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)

class UpdateSheetInputSerializer(serializers.ModelSerializer):
    """ ویرایش سند مالی (مثلا باز کردن قفل یا تغییرات دستی خاص) """
    class Meta:
        model = OrderFinancialSheet
        fields = [
            'id', 'order', 'is_locked', 'total_material_cost',
            'total_production_cost', 'total_service_cost',
            'total_delivery_cost', 'total_other_cost',
            'final_total_cost', 'total_revenue', 'net_profit',
            'profit_margin_percent'
        ]

# ========================================== #
# ========== 4. Action Serializers ========= #
# ========================================== #
class ApproveReportInputSerializer(serializers.Serializer):
    approve = serializers.BooleanField(required=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


# ===== REVENUE SERIALIZERS ===== #

class CreateRevenueReportInputSerializer(serializers.Serializer):
    """ ورودی ایجاد گزارش درآمد توسط واحد مالی """
    order_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=200)
    financial_tag_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    
    # ===== لیست اقلام درآمد ===== #
    items = serializers.ListField(
        child=FinancialItemInputSerializer(), 
        required=True, # درآمد حداقل باید یک قلم داشته باشد
        allow_empty=False
    )
    
    # ===== پیوست‌های سند درآمد ===== #
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

class BulkActionSerializer(serializers.Serializer):
    """ برای عملیات گروهی مثل حذف یا تایید دسته جمعی """
    ids = serializers.ListField(child=serializers.IntegerField(), required=True)
