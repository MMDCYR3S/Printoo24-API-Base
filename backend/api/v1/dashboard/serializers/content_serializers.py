from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from apps.blog.models import ArticleCategory, Article, Tutorial, ArticleStatus
from core.models import Product

# ========== PRODUCT MINIMAL SERIALIZER ========== #
class ProductMinimalSerializer(serializers.ModelSerializer):
    """
    سریالایزر سبک به همراه تصویر اول محصول
    """
    # فیلد کاستوم برای گرفتن اولین عکس
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'code', 'image']
        read_only_fields = ['id', 'name', 'slug', 'code']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_image(self, obj):
        if hasattr(obj, 'prefetched_images'):
            images = obj.prefetched_images
        else:
            images = obj.product_image.all()
        
        if images:
            first_img = images[0]
            if first_img.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(first_img.image.url)
                return first_img.image.url
        return None

# ========== BULK ACTION SERIALIZER ========== #
@extend_schema_serializer(
    examples=[OpenApiExample('حذف گروهی', value={"ids": [10, 11, 15]})]
)
class BulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="آرایه‌ای از شناسه‌ها (ID) برای اعمال عملیات گروهی"
    )

# ========== BULK STATUS SERIALIZER ========== #
@extend_schema_serializer(
    examples=[
        OpenApiExample('تغییر وضعیت مقالات', value={"ids": [1, 2], "status": "published"}),
        OpenApiExample('غیرفعال سازی گروهی', value={"ids": [5, 6], "is_active": False})
    ]
)
class BulkStatusSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
    is_active = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=ArticleStatus.choices, required=False)

# ========== BLOG CATEGORY READ SERIALIZER ========== #
class ArticleCategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'slug', 'is_active']

# ========== BLOG CATEGORY WRITE SERIALIZER ========== #
@extend_schema_serializer(
    examples=[OpenApiExample('ایجاد/ویرایش دسته', value={"name": "آموزش‌های پیش از چاپ", "is_active": True})]
)
class ArticleCategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['name', 'is_active']

# ========== ARTICLE READ SERIALIZER ========== #
class ArticleReadSerializer(serializers.ModelSerializer):
    related_products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'summary', 'content',
            'image', 'meta_title', 'meta_description', 'tags',
            'read_time', 'views_count', 'status', 'related_products',
            'published_at', 'created_at', 'updated_at'
        ]

# ========== ARTICLE LIST SERIALIZER ========== #
class ArticleListSerializer(serializers.ModelSerializer):
    """ سریالایزر بسیار سبک فقط برای نمایش در لیست‌ها و جدول داشبورد """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 
            'summary', 'image', 'read_time', 'author', 'author_name', 
            'status', 'published_at'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.customer_profile.first_name} {obj.author.customer_profile.last_name}".strip() or obj.author.phone_number
        return "نامشخص"

# ========== ARTICLE WRITE SERIALIZER ========== #
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'مثال ایجاد/ویرایش مقاله',
            value={
                "title": "راهنمای جامع چاپ افست",
                "category": 1,
                "summary": "خلاصه کوتاه مقاله برای نمایش در لیست...",
                "content": "<p>متن کامل و HTML تولید شده توسط ادیتور</p>",
                "image": "File",
                "meta_title": "آموزش چاپ افست - تضمین کیفیت",
                "meta_description": "در این مقاله با مزایای چاپ افست آشنا می‌شوید...",
                "tags": "چاپ,افست,آموزش",
                "read_time": 10,
                "status": "draft",
                "related_products": [15, 22, 43] # <--- لیست آیدی محصولات مرتبط
            }
        )
    ]
)
class ArticleWriteSerializer(serializers.ModelSerializer):
    related_products = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Product.objects.all(), 
        required=False
    )

    class Meta:
        model = Article
        fields = [
            'title', 'category', 'summary', 'content', 'image',
            'meta_title', 'meta_description', 'tags', 'read_time', 
            'status', 'related_products'
        ]

# ========== TUTORIAL READ SERIALIZER ========== #
class TutorialReadSerializer(serializers.ModelSerializer):
    related_products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Tutorial
        fields = [
            'id', 'title', 'slug', 'description', 'youtube_embed_url',
            'thumbnail', 'is_active', 'related_products',
            'created_at', 'updated_at'
        ]

## ========== TUTORIAL WRITE SERIALIZER ========== #
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'مثال ایجاد/ویرایش آموزش ویدیویی - برای thumbnail، ادمین باید یک عکس آپلود کند. اختیاری است.',
            value={
                "title": "نحوه تنظیم Bleed در ایلاستریتور",
                "description": "آموزش ویدیویی برای جلوگیری از سفیدی در برش",
                "thumbnail": "File",
                "youtube_embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
                "is_active": True,
                "related_products": [5, 9] # <--- محصولات مرتبط
            }
        )
    ]
)
class TutorialWriteSerializer(serializers.ModelSerializer):
    related_products = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Product.objects.all(), 
        required=False
    )

    class Meta:
        model = Tutorial
        fields = [
            'title', 'description', 'youtube_embed_url',
            'thumbnail', 'is_active', 'related_products'
        ]

# ========== TUTORIAL LIST SERIALIZER ========== #
class TutorialListSerializer(serializers.ModelSerializer):
    """ سریالایزر سبک برای نمایش لیست آموزش‌ها """
    class Meta:
        model = Tutorial
        fields = [
            'id', 'title', 'slug', 'thumbnail', 
            'is_active', 'created_at'
        ]
