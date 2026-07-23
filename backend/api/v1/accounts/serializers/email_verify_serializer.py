from rest_framework import serializers

# ======= Email Verification Serializer ======= #
class EmailVerificationSerializer(serializers.Serializer):
    """
    سریالایزر برای تایید و صحت ایمیل کاربر با استفاده از دریافت کد
    """
    email = serializers.EmailField()
    code = serializers.CharField(
        write_only=True, 
        label="کد تایید",
        min_length=6, 
        max_length=6
    )
    