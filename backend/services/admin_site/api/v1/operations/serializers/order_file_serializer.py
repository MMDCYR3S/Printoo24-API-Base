from rest_framework import serializers
from core.models import OrderItemFile

class DesignFileUploadSerializer(serializers.Serializer):
    """ ورودی آپلود فایل """
    requirement_id = serializers.IntegerField()
    file = serializers.FileField()

class FileReviewSerializer(serializers.Serializer):
    """ 
    ورودی بررسی فایل (تایید یا رد).
    جایگزین FileStatusChangeSerializer قدیمی.
    """
    is_accepted = serializers.BooleanField(required=True, help_text="True برای تایید، False برای رد")
    admin_feedback = serializers.CharField(required=False, allow_blank=True, help_text="توضیحات یا دلیل رد")
