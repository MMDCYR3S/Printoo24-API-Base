from rest_framework import serializers
from core.models import Address, Province, City

# ===== Province Serializer ===== #
class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']

# ===== City Serializer ===== #
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

# ===== Address Serializer ===== #
class AddressSerializer(serializers.ModelSerializer):
    province_detail = ProvinceSerializer(source='province', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(), source='province', write_only=True
    )
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='city', write_only=True
    )

    class Meta:
        model = Address
        fields = [
            'id', 
            'receiver_name', 
            'receiver_phone', 
            'province_id',
            'province_detail',
            'city_id',
            'city_detail',
            'detailed_address', 
            'postal_code', 
            'is_default'
        ]
