from rest_framework import serializers
from apps.blog.models import ArticleCategory, Article, Tutorial
from api.v1.dashboard.serializers import ProductMinimalSerializer 

# ========== PUBLIC BLOG CATEGORY SERIALIZER ========== #
class PublicArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'slug']

# ========== PUBLIC ARTICLE LIST SERIALIZER ========== #
class PublicArticleListSerializer(serializers.ModelSerializer):
    """ سریالایزر سبک برای نمایش لیست مقالات در صفحه اصلی بلاگ """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category_name', 'summary', 
            'image', 'read_time', 'author_name', 'published_at'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.customer_profile.first_name} {obj.author.customer_profile.last_name}".strip() or obj.author.phone_number
        return "نامشخص"

# ========== PUBLIC ARTICLE DETAIL SERIALIZER ========== #
class PublicArticleDetailSerializer(serializers.ModelSerializer):
    """ سریالایزر کامل برای صفحه خواندن مقاله """
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()
    related_products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category_name', 'summary', 'content',
            'image', 'meta_title', 'meta_description', 'tags',
            'read_time', 'views_count', 'author_name', 'related_products',
            'published_at'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return f"{obj.author.customer_profile.first_name} {obj.author.customer_profile.last_name}".strip() or obj.author.phone_number
        return "نامشخص"

# ========== PUBLIC TUTORIAL LIST SERIALIZER ========== #
class PublicTutorialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = ['id', 'title', 'slug', 'thumbnail', 'created_at']

# ========== PUBLIC TUTORIAL DETAIL SERIALIZER ========== #
class PublicTutorialDetailSerializer(serializers.ModelSerializer):
    related_products = ProductMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Tutorial
        fields = [
            'id', 'title', 'slug', 'description', 'youtube_embed_url',
            'thumbnail', 'related_products', 'created_at'
        ]