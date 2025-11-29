from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import CustomerProfile

# ===== Customer Profile Serializer ===== #
class CustomerProfileSerializer(serializers.ModelSerializer):
    # ===== فیلدهای مربوط به مدل کاربر ===== #
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'username', 'email', 'is_active', 
            'first_name', 'last_name', 'phone_number', 
            'company', 'bio', 'created_at'
        ]