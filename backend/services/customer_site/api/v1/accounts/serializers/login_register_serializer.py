from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UnifiedAuthSerializer(serializers.Serializer):
    """
    سریالایزر یکپارچه برای ورود و ثبت‌نام
    """
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=6, error_messages={
        'min_length': 'رمز عبور باید حداقل ۶ کاراکتر باشد.'
    })

# ========== User Detail Serializer ========== #
class UserDetailSerializer(serializers.ModelSerializer):
    """
    بخش نمایش اطلاعات کاربر
    """
    
    class Meta:
        model = User
        fields = ["id" ,"phone_number", "is_active", "is_staff", "is_superuser", "is_verified"]
