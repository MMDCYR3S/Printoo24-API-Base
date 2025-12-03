from rest_framework import serializers
from core.models import (
    Product,
    ProductPricingConfig,
    ProductImage,
    Attachment, 
    ProductAttachment
)

# =====Product Shell Serializer ===== #
class ProductShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 
            'code', 'is_active', 'has_price', 'has_quantity', 
            'price_modifier_percent'
        ]
        read_only_fields = ['id', 'code', 'slug']

# ===== Product Pricing Config Serializer ===== #
class ProductPricingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPricingConfig
        exclude = ['product', 'id']

# ===== Material Sync Serializer ===== #
class MaterialSyncSerializer(serializers.Serializer):
    material_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True
    )
    default_material_id = serializers.IntegerField(required=False, allow_null=True)

# ===== Quantity Sync Serializer ===== #
class QuantitySyncSerializer(serializers.Serializer):
    quantity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True
    )

# ===== Option Value Override Serializer ===== #
class OptionValueOverrideSerializer(serializers.Serializer):
    """
    اطلاعاتی که ادمین می‌خواهد همان لحظه برای مقادیر اعمال کند.
    """
    global_value_id = serializers.IntegerField(help_text="ID مقدار در بانک ویژگی‌ها")
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, default=0)
    is_default = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True) 

# ===== Option Attach With Price Serializer ===== #
class OptionAttachWithPriceSerializer(serializers.Serializer):
    option_id = serializers.IntegerField(help_text="ID ویژگی گلوبال")
    is_required = serializers.BooleanField(default=False)
    has_pricing = serializers.BooleanField(default=True)
    values_config = serializers.ListField(
        child=OptionValueOverrideSerializer(), 
        required=False, 
        allow_empty=True
    )

class OptionValuePriceItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID of ProductOptionValue")
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, required=False)
    is_default = serializers.BooleanField(required=False)
    has_pricing = serializers.BooleanField(required=False)
    order = serializers.IntegerField(required=False)

# ===== Option Price Update Serializer =====
class OptionPriceUpdateSerializer(serializers.Serializer):
    product_option_id = serializers.IntegerField(help_text="ID of the Local ProductOption")
    values = serializers.ListField(child=OptionValuePriceItemSerializer())
    
# ===== File Requirement Item Serializer ===== #
class FileRequirementItemSerializer(serializers.Serializer):
    spec_id = serializers.IntegerField(help_text="ID نوع فایل (مثلا طرح رو)")
    is_required = serializers.BooleanField(default=True)

# ===== File Requirement Sync Serializer ===== #
class FileRequirementSyncSerializer(serializers.Serializer):
    requirements = serializers.ListField(
        child=FileRequirementItemSerializer(),
        allow_empty=True
    )
    
# ===== Product Image Serializer ===== #
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']

# ===== Image Reorder Serializer =====
class ImageReorderSerializer(serializers.Serializer):
    image_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="لیست ID تصاویر به ترتیب دلخواه"
    )

# ===== Attachment Library Serializer ===== #
class AttachmentLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']

# ===== Product Attachment Link Serializer ===== #
class ProductAttachmentLinkSerializer(serializers.Serializer):
    attachment_id = serializers.IntegerField(help_text="ID فایل از کتابخانه")

class ProductAttachmentListSerializer(serializers.ModelSerializer):
    file_info = AttachmentLibrarySerializer(source='attachment', read_only=True)
    
    class Meta:
        model = ProductAttachment
        fields = ['id', 'file_info', 'created_at']
    