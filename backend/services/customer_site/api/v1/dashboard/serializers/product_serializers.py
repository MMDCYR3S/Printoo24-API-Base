from rest_framework import serializers
from core.models import (
    Product,
    ProductPricingConfig,
    ProductCategory,
    ProductImage,
    Attachment, 
    ProductAttachment,
    ProductOption,
    ProductOptionValue
)

# ===== Product Image Serializer ===== #
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'order', 'created_at']

# ===== Product Category Serializer ===== #
class ProductCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    class Meta:
        model = ProductCategory
        fields = ['name', 'slug', 'parent_name']
        read_only_fields = ['id', 'slug']

# ===== 1. اضافه کردن سریالایزر جدید برای کانفیگ تیراژ ===== #
class ProductQuantityConfigSerializer(serializers.Serializer):
    """
    دریافت شناسه تیراژ و قیمت اختصاصی آن برای محصول
    """
    id = serializers.IntegerField(help_text="شناسه تیراژ (Quantity ID)")
    price = serializers.DecimalField(
        max_digits=14, 
        decimal_places=0, 
        default=0, 
        help_text="قیمت نهایی برای این تیراژ (تومان)"
    )

# ===== Product Size Serializer ===== #
class ProductSizeConfigSerializer(serializers.Serializer):
    """
    برای دریافت ID سایز و تاثیر قیمت آن در هنگام ساخت محصول
    """
    id = serializers.IntegerField(help_text="شناسه سایز")
    price_impact = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False, 
        default=0,
        help_text="مبلغ اضافه برای این سایز"
    )

# ===== Product  Serializer ===== #
class ProductSerializer(serializers.ModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:dashboard:products-detail', 
        lookup_field='id'
    )
    category = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageSerializer(source='product_image', many=True)
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 
            'code', 'is_active', 'price', 'has_price', 'has_quantity', 
            'price_per_unit', 'detail_url', 'images', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'slug', 'detail_url']

# =====Product Shell Serializer ===== #
class ProductShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 
            'code', 'is_active', 'has_price', 'has_quantity', 
            'price_per_unit', 'created_at'
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
    اطلاعاتی که ادمین می‌خواهد برای مقادیر اعمال کند.
    می‌تواند Override روی گلوبال باشد یا یک مقدار کاملاً جدید (Custom).
    """
    # ===== تغییر: این فیلد نال‌پذیر است برای حالت Custom ===== #
    global_value_id = serializers.IntegerField(
        help_text="ID مقدار در بانک (اگر نال باشد، یعنی مقدار کاستوم است)", 
        required=False, 
        allow_null=True
    )
    
    # ===== تغییر: اضافه شدن فیلدهای متنی برای Override یا Custom ===== #
    label = serializers.CharField(required=False, help_text="عنوان نمایشی (در صورت Override یا Custom)")
    value = serializers.CharField(required=False, help_text="کد سیستمی (در صورت Override یا Custom)")
    
    # ===== فیلدهای مالی ===== #
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, required=False, default=0)
    is_default = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

# ===== Option Attach With Price Serializer ===== #
class OptionAttachWithPriceSerializer(serializers.Serializer):
    option_id = serializers.IntegerField(help_text="ID ویژگی گلوبال")
    is_required = serializers.BooleanField(default=False)
    values_config = serializers.ListField(
        child=OptionValueOverrideSerializer(), 
        required=False, 
        allow_empty=True
    )

class OptionValuePriceItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID of ProductOptionValue")
    # ===== فیلدهای مالی و تنظیمی ===== #
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, required=False)
    
    # ===== فیلدهای منطقی و نمایش ===== #
    is_default = serializers.BooleanField(required=False)
    order = serializers.IntegerField(required=False)

# ===== Option Price Update Serializer =====
class OptionPriceUpdateSerializer(serializers.Serializer):
    product_option_id = serializers.IntegerField(help_text="ID of the Local ProductOption")
    values = serializers.ListField(child=OptionValuePriceItemSerializer())
    

# ===== Product Option Value Price Item Serializer ===== #
class ProductOptionValueOutputSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش مقادیر انتخاب شده (Choices) در صفحه جزئیات محصول.
    جایگزین دیکشنری دستی سرویس.
    """
    input_type = serializers.SerializerMethodField()
    is_custom = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionValue
        fields = [
            'id', 'label', 'value', 'price_impact', 
            'is_default', 'is_custom', 'input_type', 'order'
        ]

    def get_input_type(self, obj):
        """
        لاجیک هوشمند برای پیدا کردن نوع ورودی:
        ۱. اگر به گلوبال وصل است، از آن می‌خواند.
        ۲. اگر کاستوم است، از ویژگی پدر (Option) می‌خواند.
        """
        if obj.global_source:
            return obj.global_source.input_type

    def get_is_custom(self, obj):
        return obj.global_source is None


class ProductOptionOutputSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش گروه‌های ویژگی (مانند: جنس کاغذ، روکش).
    """
    name = serializers.CharField(source='option.name', read_only=True)
    label = serializers.CharField(source='option.label', read_only=True)
    choices = ProductOptionValueOutputSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = ['id', 'name', 'label', 'is_required', 'choices', 'order']

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

    quantities = ProductQuantityConfigSerializer(many=True, required=False)

    sizes = ProductSizeConfigSerializer(many=True, required=False)


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
    sizes = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product.product_image', many=True)
    
    # آپشن‌ها (از ساختار درختی که سرویس برمی‌گرداند)
    options = ProductOptionOutputSerializer(source='product.options', many=True)
    
    def get_sizes(self, obj):
        product = obj['product']
        return {
            'sizes': [
                {
                    'name': ps.size.name,
                    'width': ps.size.width,
                    'height': ps.size.height,
                    'price': ps.price_impact
                }
                for ps in product.product_size.all()
            ]
        }
    

    def get_quantities(self, obj):
        product = obj['product']
        return [
            {
                "value": pq.quantity.value,
                "price": pq.price,
            }
            for pq in product.product_quantity.all()
        ]


class OptionConfigUpdateSerializer(serializers.Serializer):
    """
    سریالایزر برای ویرایش تنظیمات یک ویژگی متصل شده.
    """
    # ===== اضافه شده: دریافت ID در بدنه ===== #
    product_option_id = serializers.IntegerField(help_text="ID of the Local ProductOption (جدول واسط)")
    
    
    is_required = serializers.BooleanField(required=False)
    
    # ===== Values ===== #
    values = serializers.ListField(
        child=OptionValuePriceItemSerializer(), 
        required=False,
        allow_empty=True
    )
    
