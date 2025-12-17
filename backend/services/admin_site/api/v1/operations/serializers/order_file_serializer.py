from rest_framework import serializers
from core.models import OrderItem

class DesignFileUploadSerializer(serializers.Serializer):
    """ ورودی آپلود فایل """
    requirement_id = serializers.IntegerField()
    file = serializers.FileField()

class OrderItemStatusUpdateSerializer(serializers.Serializer):
    """
    ورودی تغییر وضعیت آیتم
    """
    new_status = serializers.ChoiceField(
        choices=OrderItem.STATUS_CHOICES, 
        required=True,
        help_text="وضعیت جدید (pending, approved, rejected, cancelled)"
    )
    admin_note = serializers.CharField(
        required=False, 
        allow_blank=True, 
        help_text="توضیحات فنی (مثلاً دلیل رد کردن)"
    )
