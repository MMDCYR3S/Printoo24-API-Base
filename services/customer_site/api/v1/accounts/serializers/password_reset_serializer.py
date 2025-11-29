from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# ====== Password Reset Request Serializer ====== #
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    سریالایزر برای بازشناسی رمز عبور توسط ایمیل
    """
    email = serializers.EmailField(label="ایمیل")
        
# ====== Password Reset Confirm Serializer ====== #
class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    سریالایزر برای ثبت رمز عبور جدید توسط کاربر
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="رمز عبور جدید"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="تکرار رمز عبور جدید"
    )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "رمزهای عبور با هم مطابقت ندارند."})
        
        try:
            # ==== استفاده از validator خود جنگو ==== #
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return attrs