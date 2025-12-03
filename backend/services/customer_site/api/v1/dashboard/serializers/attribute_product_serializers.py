from rest_framework import serializers
from core.models import Size, Material, FileUploadSpec, Quantity

# ===== Size Serializer ===== #
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'user', 'name', 'width', 'height', 'created_at']
        read_only_fields = ['id', 'created_at']

# ===== Material Serializer ===== #
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'user','name', 'description', 'price_per_sqm', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
        
# ===== Quantity Serializer ===== #
class QuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantity
        fields = ['id', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']

# ===== File Upload Spec Serializer ===== #
class FileUploadSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadSpec
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']
