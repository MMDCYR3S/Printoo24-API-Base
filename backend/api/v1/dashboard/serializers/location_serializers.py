from rest_framework import serializers
from core.models import City, Province

# ===== Province Serializers ===== #
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

# ===== City Serializers ===== #
class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'province', 'province_name', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at', 'province_name']

class CityCreateUpdateSerializer(serializers.ModelSerializer):
    """ سریالایزر مخصوص نوشتن (که province را ID می‌گیرد) """
    class Meta:
        model = City
        fields = ['name', 'province']

# ===== Bulk Action Serializer ===== #
class BulkDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="لیست شناسه‌ها برای حذف"
    )
    