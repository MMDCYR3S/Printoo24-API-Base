from rest_framework import serializers
from core.models import (
    Product, ProductCategory, ProductQuantity, ProductSize, 
    ProductOption, ProductOptionValue, ProductImage, 
    ProductAttachment, ProductComment, ProductPricingConfig,
    GuideType
)

# ==========================================
# 1. BASE SERIALIZERS (Building Blocks)
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
            'allow_custom_quantity',
            'min_quantity',
            'max_quantity',
            'accepts_custom_dimensions',
            'min_width',
            'max_width',
            'base_setup_price',
            'design_service_available',
            'design_fee'
        ]

# ==========================================
# 2. LEGACY SUPPORT SERIALIZERS (Size)
# ==========================================

class QuantityDetailSerializer(serializers.ModelSerializer):
    """
    نمایش تیراژ‌ها (Quantities) در صفحه محصول.
    """
    guide_text = serializers.CharField()
    guide_type = serializers.CharField()

    class Meta:
        model = ProductQuantity
        fields = ['id', 'quantity', 'price', 'guide_text', 'guide_type']

class SizeDetailSerializer(serializers.ModelSerializer):
    """
    نمایش سایز‌ها (Sizes) در صفحه محصول.
    """
    name = serializers.CharField(source='size.name', read_only=True)
    width = serializers.FloatField(source='size.width', read_only=True)
    height = serializers.FloatField(source='size.height', read_only=True)

    guide_text = serializers.CharField()
    guide_type = serializers.CharField()
    
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'width', 'height', 'price_impact', 'guide_text', 'guide_type']
    
# ==========================================
# 3. NEW OPTION SYSTEM SERIALIZERS (Dynamic)
# ==========================================

class ProductOptionValueSerializer(serializers.ModelSerializer):
    """
    نمایش مقادیر (Choices) در صفحه محصول فروشگاه.
    """
    is_custom = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionValue
        fields = [
            'id', 'label', 'value', 'price_impact', 
            'is_default', 'is_custom', 'order',
            'guide_text', 'guide_type' # [NEW] راهنمای مقدار
        ]

    def get_is_custom(self, obj):
        return obj.global_source is None

class ProductOptionSerializer(serializers.ModelSerializer):
    """
    نمایش ویژگی‌ها (Options) در صفحه محصول.
    مدیریت کامل کاستوم/لینک‌دار + راهنما.
    """
    name = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    
    # لیست مقادیر
    choices = ProductOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = [
            'id', 'name', 'label', 'type', 
            'is_required', 'choices', 'order',
            'guide_text', 'guide_type' # [NEW] راهنمای ویژگی
        ]

    def get_name(self, obj):
        if obj.name: return obj.name
        return obj.option.name if obj.option else None

    def get_label(self, obj):
        if obj.label: return obj.label
        return obj.option.label if obj.option else None

    def get_type(self, obj):
        if obj.input_type: return obj.input_type
        return obj.option.input_type if obj.option else 'select'

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

# ======= Product Attachment Serializer ======= #
class ProductAttachmentSerializer(serializers.ModelSerializer):
    """سریالایزر برای فایل های هر محصول"""
    name = serializers.CharField(source='attachment.name')
    file = serializers.FileField(source='attachment.file')
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttachment
        fields = ['id', 'name', 'file', 'file_url']
        
    def get_file_url(self, obj):
        """
        دریافت آدرس فایل
        """
        request = self.context.get('request')
        if obj.attachment.file:
            return request.build_absolute_uri(obj.attachment.file.url)
        return None

# ==========================================
# 5. MAIN PRODUCT SERIALIZERS
# ==========================================

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    # دریافت تصویر اصلی (اولین تصویر)
    thumbnail = serializers.SerializerMethodField()
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:shop:detail', 
        lookup_field='slug'
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'has_price', 'category', 'thumbnail', 'detail_url']

    def get_thumbnail(self, obj):
        img = obj.product_image.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

# ========== Product Detail Serializer ========== #
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

    def get_product_info(self, obj):
        
        product = obj
        return {
            "id": product.id,
            "name": product.name,
            "parent_category": product.category.parent.name if product.category.parent else None,
            "children_category": product.category.name if product.category else None,
            "slug": product.slug,
            "description": product.description,
            "price": product.price,
            "has_price": product.has_price,
            "code": product.code,
            "guide_text": product.guide_text, # [NEW] راهنمای کلی محصول
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
    
# ===== Input Serializer (برای ثبت نظر) ===== #
class SubmitReviewSerializer(serializers.Serializer):
    """
    سریالایزر دریافت نظر و امتیاز از کاربر.
    نکته: هر دو فیلد اختیاری هستند چون کاربر می‌تواند فقط امتیاز دهد یا فقط نظر.
    اما حداقل یکی باید باشد (این لاجیک را در سرویس یا اینجا می‌توان گذاشت).
    """
    score = serializers.IntegerField(
        required=False, 
        min_value=1, 
        max_value=5, 
        help_text="امتیاز بین ۱ تا ۵"
    )
    message = serializers.CharField(
        required=False, 
        allow_blank=False, 
        help_text="متن نظر"
    )

    def validate(self, data):
        """
        قانون: کاربر نمی‌تواند درخواست خالی بفرستد.
        """
        if 'score' not in data and 'message' not in data:
            raise serializers.ValidationError("لطفاً حداقل یک امتیاز یا متن نظر وارد کنید.")
        return data

# ===== Reply Serializer (For Admin Reply) ===== #
class ReplySerializer(serializers.ModelSerializer):
    """سریالایزر برای پاسخ‌های ادمین (تو در تو)"""
    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at']

# ===== Comment List Serializer (For User) ===== #
class CommentListSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش نظرات محصول.
    شامل پاسخ‌ها هم می‌شود.
    """
    replies = ReplySerializer(many=True, read_only=True)
    # تاریخ را فرمت‌دهی شده یا تایم‌استمپ برمی‌گردانیم
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ProductComment
        fields = ['id', 'name', 'message', 'created_at', 'replies']

# ===== Product Feekback Serializers ===== #
class ProductFeedbackStatsSerializer(serializers.Serializer):
    """
    سریالایزر ترکیبی برای آمار کلی + لیست نظرات.
    """
    average_rating = serializers.FloatField()
    total_ratings = serializers.IntegerField()
    comments = CommentListSerializer(many=True)

class ProductSummarySerializer(serializers.ModelSerializer):
    """
    نمایش خلاصه محصول در لیست‌های طولانی (مثل صفحه لندینگ دسته).
    فقط اطلاعات کلیدی: عکس، نام، قیمت پایه.
    """
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image']

    def get_image(self, obj):
        first_image = obj.product_image.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None

class SubCategoryTinySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    thumbnail = serializers.URLField()

class CategoryInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    banners = serializers.DictField() # {wide: url, box: url}

class CategoryLandingPageSerializer(serializers.Serializer):
    """
    سریالایزر نهایی برای پاسخ API صفحه لندینگ.
    """
    category_info = CategoryInfoSerializer()
    sub_categories = SubCategoryTinySerializer(many=True)
    products = ProductSummarySerializer(many=True)
