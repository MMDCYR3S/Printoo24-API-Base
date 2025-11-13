from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

# ====== Login Serializer ====== #
class LoginSerializer(serializers.Serializer):
    """
    سریالایزر مربوط به ورود کاربران
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
