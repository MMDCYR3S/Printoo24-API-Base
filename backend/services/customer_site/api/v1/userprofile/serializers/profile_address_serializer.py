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
    # خروجی (فقط خواندنی - نمایش آبجکت کامل)
    province_detail = ProvinceSerializer(source='province', read_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    
    # ورودی (فقط نوشتن - دریافت ID)
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
    
    # سایر فیلدها
    address = serializers.CharField(
        help_text="متن کامل آدرس پستی",
        min_length=10
    )
    postal_code = serializers.CharField(
        min_length=10, 
        max_length=10,
        help_text="کد پستی ۱۰ رقمی بدون خط تیره"
    )

    class Meta:
        model = Address
        fields = [
            'id', 
            # Write Fields
            'province_id', 'city_id',
            # Read Fields
            'province_detail', 'city_detail',
            # Common
            'address', 'postal_code', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_postal_code(self, value):
        """ اعتبارسنجی کد پستی (فقط عدد باشد) """
        if not value.isdigit():
            raise serializers.ValidationError("کد پستی باید فقط شامل اعداد باشد.")
        return value
