from rest_framework import serializers
from rest_framework.serializers import ValidationError

from django.contrib.auth import get_user_model

User = get_user_model()

# ======= Register Serializer ======= #
class RegisterSerializer(serializers.Serializer):
    """ سریال سازی اطلاعات کاربر جهت ثبت نام """
    
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True , min_length=8)
    password2 = serializers.CharField(write_only=True, label="تکرار رمز عبور")
    
    def validate_username(self, value):
        """ اعتبارسنجی نام کاربری """
        if len(value) < 3:
            raise ValidationError("نام کاربری باید بیشتر از 3 کاراکتر باشد")
        if User.objects.filter(username=value).exists():
            raise ValidationError("این نام کاربری قبلا استفاده شده است.")
        return value
    
    def validate_email(self, value):
        """ اعتبارسنجی ایمیل """
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("این ایمیل قبلا استفاده شده است.")
        return value.lower()
    
    def validate(self, data):
        """ اعتبارسنجی رمز عبور """
        if data["password"] != data["password2"]:
            raise ValidationError("رمز عبور با تکرار آن مطابقت ندارد.")
        if len(data["password"]) < 8:
            raise ValidationError("رمز عبور باید حداقل 8 کاراکتر داشته باشد.")
        if not any(char.isdigit() for char in data["password"]):
            raise ValidationError("رمز عبور باید شامل عدد، حروف و کاراکترهای خاص باشد.")
        return data
    
    
