from rest_framework import serializers

# ====== Logout Serializer ====== #
class LogoutSerializer(serializers.Serializer):
    """
    سریالایزر برای دریافت refresh token جهت خروج کاربر
    """
    refresh = serializers.CharField(
        help_text="توکن Refresh که می‌خواهید غیرفعال شود."
    )