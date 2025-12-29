from rest_framework import serializers
from core.models import (
    Product, ProductCategory, ProductQuantity, ProductSize, 
    ProductOption, ProductOptionValue, ProductImage, 
    ProductAttachment, ProductComment, ProductPricingConfig,
    GuideType
)

# ==========================================
# 1. BASE SERIALIZERS
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']

class ProductPricingConfigSerializer(serializers.ModelSerializer):
    """
    حیاتی برای فرانت‌‌اند: قوانین سفارش (بازه تیراژ، ابعاد دلخواه، هزینه ستاپ).
    """
    class Meta:
        model = ProductPricingConfig
        fields = [
            'allow_custom_quantity', 'min_quantity', 'max_quantity',
            'accepts_custom_dimensions', 'min_width', 'max_width',
            'base_setup_price', 'design_service_available', 'design_fee'
        ]

# ==========================================
# 2. LEGACY SUPPORT SERIALIZERS
# ==========================================

class QuantityDetailSerializer(serializers.ModelSerializer):
    guide_text = serializers.CharField()
    guide_type = serializers.CharField()

    class Meta:
        model = ProductQuantity
        fields = ['id', 'quantity', 'guide_text', 'guide_type']

class SizeDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='size.name', read_only=True)
    width = serializers.FloatField(source='size.width', read_only=True)
    height = serializers.FloatField(source='size.height', read_only=True)
    guide_text = serializers.CharField()
    guide_type = serializers.CharField()
    
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'width', 'height', 'price_impact', 'guide_text', 'guide_type']

# ==========================================
# 3. NEW OPTION SYSTEM SERIALIZERS
# ==========================================

class ProductOptionValueSerializer(serializers.ModelSerializer):
    is_custom = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionValue
        fields = [
            'id', 'label', 'value', 'price_impact', 
            'is_default', 'is_custom', 'order',
            'guide_text', 'guide_type'
        ]

    def get_is_custom(self, obj):
        return obj.global_source is None

class ProductOptionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    choices = ProductOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = [
            'id', 'name', 'label', 'type', 
            'is_required', 'choices', 'order',
            'guide_text', 'guide_type'
        ]

    def get_name(self, obj):
        return obj.name if obj.name else (obj.option.name if obj.option else None)

    def get_label(self, obj):
        return obj.label if obj.label else (obj.option.label if obj.option else None)

    def get_type(self, obj):
        return obj.input_type if obj.input_type else (obj.option.input_type if obj.option else 'select')

# ==========================================
# 4. MEDIA & FILES SERIALIZERS
# ==========================================

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'order']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class ProductAttachmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='attachment.name')
    file = serializers.FileField(source='attachment.file')
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttachment
        fields = ['id', 'name', 'file', 'file_url']
        
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.attachment.file:
            return request.build_absolute_uri(obj.attachment.file.url) if request else obj.attachment.file.url
        return None

# ==========================================
# 5. MAIN PRODUCT SERIALIZERS (REFACTORED for M2M)
# ==========================================

class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:shop:detail',
        lookup_field='slug'
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'has_price', 'category', 'thumbnail', 'detail_url']

    def get_category(self, obj):
        """
        چون is_primary نداریم و قانون این بود که محصول به یک زیردسته وصل شود،
        اولین دسته‌بندی موجود در لیست M2M را برمی‌گردانیم.
        """
        cat = obj.categories.first()
        if cat:
            return CategorySerializer(cat).data
        return None

    def get_thumbnail(self, obj):
        img = obj.product_image.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

class ProductDetailSerializer(serializers.Serializer):
    """
    سریالایزر نهایی صفحه محصول (ترکیب تمام اطلاعات).
    """
    product_info = serializers.SerializerMethodField()
    pricing_config = serializers.SerializerMethodField()
    
    quantities = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    
    options = ProductOptionSerializer(many=True)
    images = ProductImageSerializer(source='product_image', many=True)
    # اضافه کردن فایل‌های پیوست اگر نیاز است
    attachments = ProductAttachmentSerializer(source='product_attachment_product', many=True, read_only=True)

    def get_product_info(self, obj):
        product = obj
        
        # ===== لاجیک استخراج دسته‌بندی (بدون is_primary) ===== #
        assigned_cat = product.categories.first()
        
        parent_name = None
        category_name = None
        
        if assigned_cat:
            category_name = assigned_cat.name

            if assigned_cat.parent:
                parent_name = assigned_cat.parent.name
            else:
                parent_name = assigned_cat.name

        return {
            "id": product.id,
            "name": product.name,
            "parent_category": parent_name, 
            "children_category": category_name,
            
            "slug": product.slug,
            "description": product.description,
            "price": product.price,
            "has_price": product.has_price,
            "code": product.code,
            "guide_text": product.guide_text,
            "guide_type": product.guide_type
        }

    def get_pricing_config(self, obj):
        if hasattr(obj, 'pricing_config'):
            return ProductPricingConfigSerializer(obj.pricing_config).data
        return None

    def get_quantities(self, obj):
        qs = obj.product_quantity.all().select_related('quantity')
        return QuantityDetailSerializer(qs, many=True).data

    def get_sizes(self, obj):
        qs = obj.product_size.all().select_related('size')
        return SizeDetailSerializer(qs, many=True).data

# ==========================================
# 6. FEEDBACK & OTHER SERIALIZERS
# ==========================================

class SubmitReviewSerializer(serializers.Serializer):
    score = serializers.IntegerField(required=False, min_value=1, max_value=5)
    message = serializers.CharField(required=False, allow_blank=False)

    def validate(self, data):
        if 'score' not in data and 'message' not in data:
            raise serializers.ValidationError("لطفاً حداقل یک امتیاز یا متن نظر وارد کنید.")
        return data

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at']

class CommentListSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at', 'replies']

class ProductFeedbackStatsSerializer(serializers.Serializer):
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    comments = CommentListSerializer(many=True)

# ===== Summary & Landing Serializers ===== #

class ProductSummarySerializer(serializers.ModelSerializer):
    """
    نمایش خلاصه محصول در لیست‌های طولانی.
    """
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image']

    def get_image(self, obj):
        first_image = obj.product_image.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None

class SubCategoryTinySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    thumbnail = serializers.URLField(allow_null=True)
    link = serializers.CharField(allow_null=True)

class CategoryInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    banners = serializers.DictField()
    breadcrumbs = serializers.ListField(child=serializers.DictField(), required=False)

class CategoryLandingPageSerializer(serializers.Serializer):
    category_info = CategoryInfoSerializer()
    sub_categories = SubCategoryTinySerializer(many=True)
    products = ProductSummarySerializer(many=True)
