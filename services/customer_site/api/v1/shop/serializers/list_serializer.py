from rest_framework import serializers
from core.models import Product, ProductCategory

# ======= Category Serializer ======= #
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['name', 'slug']

# ======= Product Serializer ======= #
class ProductListSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای نمایش محصولات در لیست.
    اطلاعات خلاصه‌ای را نمایش می‌دهد.
    """
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'name',
            'slug',
            'price',
            'category',
        ]