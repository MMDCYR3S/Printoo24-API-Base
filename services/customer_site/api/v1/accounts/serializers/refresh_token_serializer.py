from rest_framework import serializers

# ====== Refresh Token Serializer ====== #
class RefreshTokenSerializer(serializers.Serializer):
    """
    سریالایزر برای دریافت توکن جدید
    """
    
    refresh_token = serializers.CharField()
