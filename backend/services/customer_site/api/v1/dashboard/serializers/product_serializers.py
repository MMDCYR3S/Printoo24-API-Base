from rest_framework import serializers
from core.models import (
    Product, ProductPricingConfig, ProductCategory,
    ProductImage, Attachment, ProductAttachment,
    ProductOption, ProductOptionValue, GuideType,
    OptionInputType
)

# ===== Guide Fields Mixin ===== #
class GuideSerializerMixin(serializers.Serializer):
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_type = serializers.ChoiceField(choices=GuideType.choices, required=False, default=GuideType.INFO)
    
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

# ===== 1. اصلاح شده: حذف قیمت از کانفیگ تیراژ ===== #
class ProductQuantityConfigSerializer(GuideSerializerMixin, serializers.Serializer):
    """
    دریافت شناسه تیراژ برای محصول.
    نکته: قیمت از این بخش حذف شد چون محاسبات بر اساس Price Per Unit انجام می‌شود.
    """
    id = serializers.IntegerField(help_text="شناسه تیراژ (Quantity ID)")

# ===== Product Size Serializer ===== #
class ProductSizeConfigSerializer(GuideSerializerMixin, serializers.Serializer):
    """
    برای دریافت ID سایز و تاثیر قیمت آن در هنگام ساخت محصول
    """
    id = serializers.IntegerField(help_text="شناسه سایز")
    price_impact = serializers.DecimalField(
        max_digits=12, 
        decimal_places=0, # اصلاح جزئی: معمولاً قیمت تومان اعشار ندارد، اما اگر نیاز دارید 2 بگذارید
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
    category = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_image', many=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'description', 
            'code', 'is_active', 'price', 'has_price', 'has_quantity', 
            'price_per_unit', 'detail_url', 'images', 'created_at'
        ]
        read_only_fields = ['id', 'code', 'slug', 'detail_url']

    def get_category(self, obj):
        cat = obj.categories.first()
        return cat.name if cat else "Uncategorized"

# =====Product Shell Serializer ===== #
class ProductShellSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=True, help_text="شناسه دسته‌بندی (زیرمجموعه)")
    category_info = serializers.SerializerMethodField(read_only=True)
    guide_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    guide_type = serializers.ChoiceField(choices=GuideType.choices, required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_id', 'category_info', 'description', 
            'code', 'is_active', 'has_price', 'has_quantity', 
            'price', 'price_per_unit', 'created_at',
            'guide_text', 'guide_type'
        ]
        read_only_fields = ['id', 'code', 'slug']
        
    def validate(self, data):
        """ اعتبارسنجی قوانین بیزینس """
        has_quantity = data.get('has_quantity', True)
        price_per_unit = data.get('price_per_unit', 1)
        
        if not has_quantity and price_per_unit < 1:
            raise serializers.ValidationError({"price_per_unit": "گام شمارش باید حداقل ۱ باشد."})
        return data

    def get_category_info(self, obj):
        cat = obj.categories.first()
        if cat:
            return {"id": cat.id, "name": cat.name, "slug": cat.slug}
        return None

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
class OptionValueOverrideSerializer(GuideSerializerMixin, serializers.Serializer):
    """
    اطلاعاتی که ادمین می‌خواهد برای مقادیر اعمال کند.
    می‌تواند Override روی گلوبال باشد یا یک مقدار کاملاً جدید (Custom).
    """
    global_value_id = serializers.IntegerField(required=False, allow_null=True)
    label = serializers.CharField(required=False)
    value = serializers.CharField(required=False)
    price_impact = serializers.DecimalField(max_digits=14, decimal_places=0, default=0)
    is_default = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)

# ===== Option Attach With Price Serializer ===== #
class OptionAttachWithPriceSerializer(serializers.Serializer):
    option_id = serializers.IntegerField(
        required=False, 
        allow_null=True,
        help_text="اگر خالی باشد، یعنی ویژگی کاملاً اختصاصی (Custom) است."
    )
    name = serializers.CharField(
        required=False, 
        help_text="نام سیستمی برای ویژگی کاستوم (مثلا special_cut)"
    )
    label = serializers.CharField(
        required=False,
        help_text="عنوان نمایشی ویژگی کاستوم (مثلا برش خاص)"
    )
    input_type = serializers.ChoiceField(
        choices=OptionInputType.choices,
        required=False,
        default=OptionInputType.SELECT,
        help_text="نوع ورودی (فقط برای ویژگی کاستوم)"
    )
    guide_text = serializers.CharField(required=False, allow_blank=True)
    is_required = serializers.BooleanField(default=False)
    values_config = serializers.ListField(child=OptionValueOverrideSerializer(), required=False)

    def validate(self, data):
        if not data.get('option_id'):
            if not data.get('label') or not data.get('name'):
                raise serializers.ValidationError(
                    "برای ویژگی‌های سفارشی (بدون option_id)، وارد کردن 'name' و 'label' الزامی است."
                )
        return data

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
    """
    is_custom = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionValue
        fields = [
            'id', 'label', 'value', 'price_impact', 
            'is_default', 'is_custom', 'guide_text', 'guide_type', 'order'
        ]

    def get_is_custom(self, obj):
        return obj.global_source is None
        
    def get_label(self, obj):
        if obj.label:
            return obj.label
        if obj.global_source:
            return obj.global_source.label
        return ""
        
    def get_value(self, obj):
        if obj.value:
            return obj.value
        if obj.global_source:
            return obj.global_source.value
        return ""

class ProductOptionOutputSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    input_type = serializers.SerializerMethodField()
    
    choices = ProductOptionValueOutputSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = [
            'id', 'name', 'label', 'input_type', 'is_required', 
            'choices', 'order', 'guide_text', 'guide_type'
        ]

    def get_name(self, obj):
        if obj.name:
            return obj.name
        if obj.option:
            return obj.option.name
        return ""

    def get_label(self, obj):
        if obj.label:
            return obj.label
        if obj.option:
            return obj.option.label
        return ""

    def get_input_type(self, obj):
        if obj.input_type:
            return obj.input_type
        if obj.option:
            return obj.option.input_type
        return OptionInputType.TEXT

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
    image_orders = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

# ===== Product Detail Serializer ===== #
class ProductDetailSerializer(serializers.Serializer):
    shell = ProductShellSerializer(source='product')
    pricing_config = ProductPricingConfigSerializer(source='product.pricing_config')
    
    quantities = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product.product_image', many=True)
    
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
                "value": pq.quantity.value
            }
            for pq in product.product_quantity.all()
        ]

# ===== Option Config Update Serializer ===== #
class OptionConfigUpdateSerializer(serializers.Serializer):
    """
    سریالایزر برای ویرایش تنظیمات یک ویژگی متصل شده.
    """
    product_option_id = serializers.IntegerField(help_text="ID of the Local ProductOption (جدول واسط)")
    
    is_required = serializers.BooleanField(required=False)
    
    # ===== Values ===== #
    values = serializers.ListField(
        child=OptionValuePriceItemSerializer(), 
        required=False,
        allow_empty=True
    )
