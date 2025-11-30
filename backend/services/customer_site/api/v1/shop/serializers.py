from rest_framework import serializers
from core.models import (
    Product, 
    ProductCategory, 
    ProductQuantity, 
    ProductSize,  
    ProductMaterial,  
    ProductOption, 
    OptionValue, 
    ProductImage,
    ProductAttachment,
    ProductComment,
    ProductCommentChoices,
    ProductRating,
)

# ====== Category Serializer ====== #
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['name', 'slug']

# ======= Quantity Detail Serializer ======= #
class QuantityDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش تیراژها و ضریب تخفیف/افزایش آن‌ها"""
    class Meta:
        model = ProductQuantity
        fields = ['id', 'quantity', 'price']
        
# ======= Size Detail Serializer ======== #
class SizeDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش جزئیات سایزها"""
    name = serializers.CharField(source='size.name', read_only=True)
    width = serializers.FloatField(source='size.width', read_only=True)
    height = serializers.FloatField(source='size.height', read_only=True)
    
    class Meta:
        model = ProductSize
        fields = ['id', 'name', 'width', 'height', 'price_impact']

# ======= Material Detail Serializer ======= #
class MaterialDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش جزئیات جنس‌ها"""
    name = serializers.CharField(source='material.name', read_only=True)
    
    class Meta:
        model = ProductMaterial
        fields = ['id', 'name', 'price_impact']

# ======= Option Value Detail Serializer ======= #
class OptionValueDetailSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش مقدار یک آپشن (مثلا 'مات' یا 'براق')"""
    class Meta:
        model = OptionValue
        fields = ['id', 'value']

# ======= Option Detail Serializer ======= #
class OptionDetailSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش یک آپشن قابل انتخاب کامل.
    شامل مقدار و تأثیر قیمت آن است.
    """
    option_value = OptionValueDetailSerializer(read_only=True)
    
    class Meta:
        model = ProductOption
        fields = ['id', 'option_value', 'price_impact']

# ======= Product Image Serializer ======= #
class ProductImageSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش تصاویر محصول"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'order']
    
    def get_image_url(self, obj):
        """دریافت URL کامل تصویر"""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
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

# =============================== #
# ======= Product Serializer ======= #
# =============================== #
class ProductListSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش محصولات در لیست.
    اطلاعات خلاصه‌ای را نمایش می‌دهد.
    """
    category = CategorySerializer(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(view_name='api:v1:shop:detail', lookup_field='slug')

    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'price',
            'category',
            'detail_url',
        ]

# ===================================== #
# ======= Product Detail Serializer ======= #
# ===================================== #
class ProductDetailSerializer(serializers.Serializer):
    """
    سریالایزر اصلی و جامع برای نمایش تمام جزئیات یک محصول.
    این سریالایزر یک دیکشنری را به عنوان ورودی می‌گیرد که توسط ShopProductDetailService ساخته شده.
    """
    # ===== فیلد های مصحول ===== #
    name = serializers.CharField(source='product.name')
    slug = serializers.SlugField(source='product.slug')
    description = serializers.CharField(source='product.description')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    # ===== فیلد قیمت سایز دلخواه ===== #
    price_per_square_unit = serializers.DecimalField(source='product.price_per_square_unit', max_digits=10, decimal_places=2, allow_null=True)
    # price_modifier_percent = serializers.IntegerField(source='product.price_modifier_percent')
    
    # ===== فیلدهای مربوط به سریالایزر ===== #
    category = CategorySerializer(source='product.category', read_only=True)
    quantities = QuantityDetailSerializer(source='product.product_quantity', many=True)
    sizes = SizeDetailSerializer(source='product.product_quantity', many=True)
    materials = MaterialDetailSerializer(source='product.product_material', many=True)
    images = ProductImageSerializer(many=True)
    attachments = ProductAttachmentSerializer(many=True)
    # ===== فیلد ویژگی های منحصر به فرد به صورت تابع ===== #
    options = serializers.SerializerMethodField()
    
    def get_options(self, obj):
        """
        این متد ساختار گروه‌بندی شده آپشن‌ها را از سرویس دریافت کرده
        و آن را به فرمت مناسب برای JSON تبدیل می‌کند.
        """
        grouped = obj.get('grouped_options', {})
        result = []
        for type_name, items in grouped.items():
            result.append({
                'title': type_name,
                'items': OptionDetailSerializer(items, many=True).data
            })
        return result
    
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
