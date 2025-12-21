from rest_framework import serializers
from core.models import Size, Quantity

# ===== Size Serializer ===== #
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'width', 'height', 'created_at']
        read_only_fields = ['id', 'created_at']
        
# ===== Quantity Serializer ===== #
class QuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantity
        fields = ['id', 'value', 'created_at']
        read_only_fields = ['id', 'created_at']
