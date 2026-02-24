from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from apps.blog.models import ArticleCategory, Article, Tutorial, ArticleStatus

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
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'summary', 'content',
            'image', 'meta_title', 'meta_description', 'tags',
            'read_time', 'views_count', 'status',
            'published_at', 'created_at', 'updated_at'
        ]

# ========== ARTICLE WRITE SERIALIZER ========== #
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'ساخت مقاله جدید',
            value={
                "title": "string",
                "category": 0,
                "summary": "string",
                "content": "string",
                "image": "string",
                "meta_title": "string",
                "meta_description": "string",
                "tags": "string",
                "read_time": 32767,
                "status": "draft",
            }
        )
    ]
)
class ArticleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'category', 'summary', 'content', 'image',
            'meta_title', 'meta_description', 'tags', 'read_time', 'status'
        ]

# ========== TUTORIAL READ SERIALIZER ========== #
class TutorialReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = [
            'id', 'title', 'slug', 'description', 'youtube_embed_url',
            'thumbnail', 'attachment_file', 'is_active',
            'created_at', 'updated_at'
        ]

# ========== TUTORIAL WRITE SERIALIZER ========== #
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'ساخت آموزش ویدیویی',
            value={
                "title": "آموزش تنظیم Bleed",
                "youtube_embed_url": "https://www.youtube.com/embed/...",
                "is_active": True
            }
        )
    ]
)
class TutorialWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = [
            'title', 'description', 'youtube_embed_url',
            'thumbnail', 'attachment_file', 'is_active'
        ]
        