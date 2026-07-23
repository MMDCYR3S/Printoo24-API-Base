from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import CustomerProfile, ProductComment

# ===== Customer Profile Serializer ===== #
class CustomerProfileSerializer(serializers.ModelSerializer):
    # ===== فیلدهای مربوط به مدل کاربر ===== #
    phone_number = serializers.EmailField(source='user.phone_number', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'is_active', 
            'first_name', 'last_name', 'phone_number', 
            'company', 'bio', 'created_at'
        ]

# ===== Profile Comment Serializer ===== #
class ProfileCommentSerializer(serializers.ModelSerializer):
    """
    نمایش نظر در پروفایل کاربر.
    شامل نام محصول و وضعیت تایید نظر است.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ProductComment
        fields = [
            'id', 
            'product_name', 
            'product_slug', 
            'message', 
            'status', 
            'status_display',
            'admin_note',
            'created_at'
        ]        
