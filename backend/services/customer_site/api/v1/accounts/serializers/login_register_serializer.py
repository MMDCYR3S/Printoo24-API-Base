from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ====== Login Serializer ====== #
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

# ===== Register Serializer ===== #
class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, 
        validators=[UniqueValidator(queryset=User.objects.all(), message="این شماره تماس قبلاً ثبت شده است.")]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    
    password = serializers.CharField(write_only=True, min_length=6, error_messages={
        'min_length': 'رمز عبور باید حداقل ۶ کاراکتر باشد.'
    })
    password_2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_2']:
            raise serializers.ValidationError({"password": "رمز عبور با تکرار آن مطابقت ندارد."})
        attrs.pop('password_2')
        return attrs

# ========== User Detail Serializer ========== #
class UserDetailSerializer(serializers.ModelSerializer):
    """
    بخش نمایش اطلاعات کاربر
    """
    
    class Meta:
        model = User
        fields = ["id" ,"phone_number", "is_active", "is_staff", "is_superuser", "is_verified"]
