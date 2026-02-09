from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ====== Login Serializer ====== #
class LoginSerializer(serializers.Serializer):
    """
    سریالایزر مربوط به ورود کاربران
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# ===== Register Serializer ===== #
class RegisterSerializer(serializers.ModelSerializer):
    """
    سریالایزر استاندارد ثبت‌نام با بهره‌گیری از قدرت جانگو و DRF
    """
    # ===== یکتا بودن ایمیل ===== #
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="این ایمیل قبلاً ثبت شده است.")]
    )
   # ===== تکرار رمز عبور ===== #
    password_2 = serializers.CharField(
        label="تکرار رمز عبور",
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_2')
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'username': {
                'validators': [UniqueValidator(queryset=User.objects.all(), message="این نام کاربری قبلاً گرفته شده است.")]
            }
        }

    def validate(self, attrs):
        """
        اعتبارسنجی نهایی فیلدها
        """
        # ===== بررسی مطابقت رمز عبور ===== #
        if attrs['password'] != attrs['password_2']:
            raise serializers.ValidationError({"password": "رمز عبور با تکرار آن مطابقت ندارد."})

        # ===== بررسی پسورد ===== #
        try:
            validate_password(attrs['password'])
        except Exception as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        attrs.pop('password_2')
        return attrs

    def create(self, validated_data):
        """
        ایجاد کاربر جدید. 
        نکته: در ویو شما از سرویس استفاده کردید، بنابراین شاید این متد create 
        توسط ویو صدا زده نشه، اما بودنش در ModelSerializer استاندارد است.
        """
        return User.objects.create_user(**validated_data)

# ========== User Detail Serializer ========== #
class UserDetailSerializer(serializers.ModelSerializer):
    """
    بخش نمایش اطلاعات کاربر
    """
    
    class Meta:
        model = User
        fields = ["id" ,"username", "is_active", "is_staff", "is_superuser", "is_verified"]
