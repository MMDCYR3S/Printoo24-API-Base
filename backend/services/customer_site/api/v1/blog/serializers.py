from rest_framework import serializers
from apps.blog.models import ArticleCategory, Article, Tutorial
from core.models import Product

# ========== PRODUCT MINIMAL SERIALIZER ========== #
class ProductMinimalSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price','show_price', 'has_price', 'thumbnail', 'category']

    def get_thumbnail(self, obj):
        first_image = obj.product_image.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        return None

    def get_category(self, obj):
        assigned_cats = obj.categories.select_related("parent").all()
        subcategory = next((c for c in assigned_cats if c.parent is not None), None)
        if subcategory:
            return {
                "parent_category": subcategory.parent.name,
                "children_category": subcategory.name
            }
        root_cat = next((c for c in assigned_cats if c.parent is None), None)
        return {
            "parent_category": root_cat.name if root_cat else None,
            "children_category": None
        }

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