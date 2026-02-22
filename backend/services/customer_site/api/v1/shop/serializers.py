from rest_framework import serializers
from core.models import (
    Product, ProductCategory, 
    ProductImage, ProductComment, Attachment
)

# ==========================================
# 1. BASE SERIALIZERS
# ==========================================

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']

# ==========================================
# 2. LEGACY SUPPORT SERIALIZERS
# ==========================================
class QuantityPriceMatrixOutputSerializer(serializers.Serializer):
    """
    نمایش ماتریس قیمت‌ها به فرانت‌اند مشتری
    """
    quantity_id = serializers.IntegerField(source='product_quantity.quantity.id')
    quantity_value = serializers.IntegerField(source='product_quantity.quantity.value')
    price = serializers.DecimalField(max_digits=12, decimal_places=0)

class OptionRequirementSerializer(serializers.Serializer):
    """
    نمایش نیازمندی‌های یک گزینه به فرانت‌اند (ماشین‌حساب مشتری)
    """
    required_value_id = serializers.IntegerField(source='required_value_id')
    action = serializers.CharField()

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
        fields = ['id', 'name', 'slug', 'price', 'show_price', 'has_price', 'category', 'thumbnail', 'detail_url']

    def get_category(self, obj):
        """
        بازگرداندن نام والد و فرزند به صورت دیکشنری مسطح (مانند Detail).
        """
        assigned_cat = obj.categories.first()
        
        parent_name = None
        category_name = None
        
        if assigned_cat:
            category_name = assigned_cat.name

            if assigned_cat.parent:
                parent_name = assigned_cat.parent.name
            else:
                parent_name = assigned_cat.name
        # ===== بازگشت اطلاعات ===== #
        return {
            "parent_category": parent_name,
            "children_category": category_name
        }

    def get_thumbnail(self, obj):
        img = obj.product_image.first()
        if img:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

#‌ ========== ATTACHMENT SERAILZIER ========== #
class AttachmentSerializer(serializers.ModelSerializer):
    """
    سریالایزر مربوط به فایل‌های پیوست
    """
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ['id', 'name', 'file', 'file_url', 'created_at']
        
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

#‌ ========== PRODUCT DETAIL SERIALIEZER ========== #
class ProductDetailSerializer(serializers.Serializer):
    """
    سریالایزر نهایی صفحه محصول (ترکیب تمام اطلاعات).
    """
    product_info = serializers.SerializerMethodField()
    pricing_config = serializers.SerializerMethodField()
    
    quantities = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()

    images = ProductImageSerializer(source='product_image', many=True)
    # اضافه کردن فایل‌های پیوست اگر نیاز است
    attachments = AttachmentSerializer(source='product_attachment', many=True, read_only=True)

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
            'show_price': product.show_price,
            "has_price": product.has_price,
            "code": product.code,
            "guide_text": product.guide_text,
            "guide_type": product.guide_type
        }

    def get_pricing_config(self, obj):
        if hasattr(obj, 'pricing_config'):
            return ProductPricingConfigSerializer(obj.pricing_config).data
        return None

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
    thumbnail = serializers.URLField(allow_null=True, required=False) 
    link = serializers.CharField(allow_null=True, required=False)

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
