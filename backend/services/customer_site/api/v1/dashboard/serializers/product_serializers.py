from rest_framework import serializers
from core.models import (
    Product,
    ProductPricingConfig,
    ProductImage,
    Attachment, 
    ProductAttachment
)

# ===== Product Image Serializer ===== #
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']


# =====Product  Serializer ===== #
class ProductSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:products-detail', 
        lookup_field='id'
    )
    images = ProductImageSerializer(source='product_image', many=True)
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 
            'code', 'is_active', 'price', 'has_price', 'has_quantity', 
            'price_modifier_percent', 'detail_url', 'images'
        ]
        read_only_fields = ['id', 'code', 'slug', 'detail_url']

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
    quantity_step = serializers.IntegerField(required=False, default=1, min_value=1)
    is_step_ceiling = serializers.BooleanField(required=False, default=False)

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
    # ===== فیلدهای مالی و تنظیمی ===== #
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, required=False)
    has_pricing = serializers.BooleanField(required=False)
    
    # ===== فیلدهای منطقی و نمایش ===== #
    is_default = serializers.BooleanField(required=False)
    order = serializers.IntegerField(required=False)
    
    # ===== تیراژ و شمارش===== #
    quantity_step = serializers.IntegerField(required=False, min_value=1)
    is_step_ceiling = serializers.BooleanField(required=False)

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

# ===== API 1: Core Create/Update ===== #
class ProductCoreCreateSerializer(serializers.Serializer):
    shell = ProductShellSerializer(required=True)
    pricing_config = ProductPricingConfigSerializer(required=True)

    quantity_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    # لیست دیکشنری
    file_requirements = serializers.ListField(
        child=FileRequirementItemSerializer(), 
        required=False
    )

# ===== API 2: Options Bulk ===== #
class ProductOptionsBulkSerializer(serializers.Serializer):
    options = serializers.ListField(
        child=OptionAttachWithPriceSerializer(),
        allow_empty=False
    )

# ===== API 3: Media Sync (JSON part) ===== #
class ProductMediaSyncSerializer(serializers.Serializer):
    attachment_ids_to_link = serializers.ListField(child=serializers.IntegerField(), required=False)
    attachment_ids_to_unlink = serializers.ListField(child=serializers.IntegerField(), required=False)
    image_orders = serializers.ListField(child=serializers.IntegerField(), required=False)

# ===== Product Detail Serializer ===== #
class ProductDetailSerializer(serializers.Serializer):
    """
    سریالایزر نمایش کامل محصول در داشبورد.
    ترکیبی از Shell, Config, Options, Images.
    """
    shell = ProductShellSerializer(source='product')
    pricing_config = ProductPricingConfigSerializer(source='product.pricing_config')
    
    # لیست‌ها
    quantities = serializers.SerializerMethodField()
    file_requirements = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product.product_image', many=True)
    
    # آپشن‌ها (از ساختار درختی که سرویس برمی‌گرداند)
    options = serializers.ListField(source='structured_options')

    def get_quantities(self, obj):
        product = obj['product']
        return [pq.quantity.value for pq in product.product_quantity.all()]

    def get_file_requirements(self, obj):
        product = obj['product']
        return [
            {
                'spec_id': req.spec.id,
                'name': req.spec.name,
                'is_required': req.is_required
            }
            for req in product.file_upload_requirements.all()
        ]

class OptionConfigUpdateSerializer(serializers.Serializer):
    """
    سریالایزر برای ویرایش تنظیمات یک ویژگی متصل شده.
    """
    # ===== اضافه شده: دریافت ID در بدنه ===== #
    product_option_id = serializers.IntegerField(help_text="ID of the Local ProductOption (جدول واسط)")
    
    
    is_required = serializers.BooleanField(required=False)
    has_pricing = serializers.BooleanField(required=False)
    
    # ===== Values ===== #
    values = serializers.ListField(
        child=OptionValuePriceItemSerializer(), 
        required=False,
        allow_empty=True
    )
    
