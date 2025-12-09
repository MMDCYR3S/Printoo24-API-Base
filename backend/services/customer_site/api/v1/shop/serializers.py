from rest_framework import serializers
from core.models import (
    Product, 
    ProductCategory, 
    ProductQuantity, 
    ProductSize,  
    ProductOption,  
    ProductOptionValue,
    ProductImage,
    ProductAttachment,
    ProductComment,
    ProductPricingConfig,
    ProductFileUploadRequirement
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
    class Meta:
        model = ProductQuantity
        fields = ['id', 'quantity', 'price']

class SizeDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='size.name', read_only=True)
    width = serializers.FloatField(source='size.width', read_only=True)
    height = serializers.FloatField(source='size.height', read_only=True)
    
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'width', 'height', 'price_impact']
        
# ==========================================
# 3. NEW OPTION SYSTEM SERIALIZERS (Dynamic)
# ==========================================

class ProductOptionValueSerializer(serializers.ModelSerializer):
    """
    نمایش گزینه‌های قابل انتخاب (Choices) مثل: مات، براق، قرمز.
    """
    description = serializers.SerializerMethodField()

    class Meta:
        model = ProductOptionValue
        fields = [
            'id', 
            'label', 
            'value', 
            'price_impact',   # مبلغی که به کاربر نمایش میدهیم (+5000)
            'quantity_step',  # گام شمارش (هر 10 عدد)
            'is_default',
            'description'     # متن توضیحی تولید شده
        ]

    def get_description(self, obj):
        """تولید متن راهنما برای کاربر (مثلا: هر 100 عدد)"""
        if obj.quantity_step > 1:
            return f"قیمت محاسبه شده به ازای هر {obj.quantity_step} عدد می‌باشد."
        return ""

class ProductOptionSerializer(serializers.ModelSerializer):
    """
    نمایش خود ویژگی (سوال) به همراه لیست گزینه‌ها.
    """
    name = serializers.CharField(source='option.name', read_only=True)
    label = serializers.CharField(source='option.label', read_only=True)
    type = serializers.CharField(source='option.input_type', read_only=True)
    description = serializers.CharField(source='option.description', read_only=True)
    
    # ===== Nested Choices ===== #
    choices = ProductOptionValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOption
        fields = [
            'id', 
            'name', 
            'label', 
            'type', 
            'is_required', 
            'description', 
            'has_pricing', 
            'choices'
        ]

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

class FileUploadRequirementSerializer(serializers.ModelSerializer):
    spec_name = serializers.CharField(source='spec.name', read_only=True)
    spec_description = serializers.CharField(source='spec.description', read_only=True)

    class Meta:
        model = ProductFileUploadRequirement
        fields = ['id', 'spec_name', 'spec_description', 'is_required', 'sort_order']

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

class ProductDetailSerializer(serializers.Serializer):
    """
    سریالایزر جامع محصول.
    نکته: چون خروجی سرویس یک دیکشنری ترکیبی است، از ModelSerializer استفاده نمی‌کنیم.
    """
    # 1. اطلاعات پایه محصول
    product_info = serializers.SerializerMethodField()
    
    # 2. تنظیمات قیمت (بسیار مهم)
    pricing_config = serializers.SerializerMethodField()
    
    # 3. لیست‌های قدیمی (Legacy)
    quantities = QuantityDetailSerializer(many=True)
    sizes = SizeDetailSerializer(many=True)
    options = serializers.JSONField() 
    
    # 5. فایل‌ها و مدیا
    images = ProductImageSerializer(many=True)
    file_requirements = FileUploadRequirementSerializer(many=True)

    def get_product_info(self, obj):
        product = obj['product']
        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "price": product.price,
            "has_price": product.has_price,
            "code": product.code
        }

    def get_pricing_config(self, obj):
        product = obj['product']
        if hasattr(product, 'pricing_config'):
            return ProductPricingConfigSerializer(product.pricing_config).data
        return None
    
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
