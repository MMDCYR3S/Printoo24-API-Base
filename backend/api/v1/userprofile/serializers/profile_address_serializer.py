from rest_framework import serializers
from core.models import Address, Province, City

# ===== Province & City Serializers ===== #
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'slug']

# ===== Address Serializer (Optimized) ===== #
class AddressSerializer(serializers.ModelSerializer):
    province_detail = ProvinceSerializer(source='province', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), 
        source='province', 
        write_only=True,
        required=True,
        help_text="شناسه استان"
    )
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), 
        source='city', 
        write_only=True, 
        required=True,
        help_text="شناسه شهر"
    )
    
    address = serializers.CharField(
        help_text="متن کامل آدرس پستی",
        min_length=10
    )
    class Meta:
        model = Address
        fields = [
            'id', 'province_id', 'city_id',
            'province_detail', 'city_detail',
            'address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
