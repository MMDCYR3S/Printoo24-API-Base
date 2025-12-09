from rest_framework import serializers
from core.models import OrderItemFile

class DesignFileUploadSerializer(serializers.Serializer):
    """ ورودی آپلود فایل """
    requirement_id = serializers.IntegerField()
    file = serializers.FileField()

class FileStatusChangeSerializer(serializers.Serializer):
    """ ورودی تغییر وضعیت فایل """
    status = serializers.ChoiceField(choices=OrderItemFile.STATUS_CHOICES)
    admin_feedback = serializers.CharField(required=False, allow_blank=True)
