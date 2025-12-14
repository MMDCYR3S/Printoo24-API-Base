from rest_framework import serializers
from core.models import CustomerNotification

# ===== Notification Serializers ===== #
class NotificationSerializer(serializers.ModelSerializer):
    """
    سریالایزر نمایش اعلان.
    """
    # ===== زمان ارسال (مدت زمان سپری شده) ===== #
    time_since = serializers.SerializerMethodField()
    # ===== نمایش نام مدل هدف ===== #
    target_model = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = CustomerNotification
        fields = [
            'id', 'name', 'message', 'is_read', 
            'created_at', 'time_since', 
            'target_model', 'object_id'
        ]

    def get_time_since(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)

# ===== Notification Response Wrapper ===== #
class NotificationListResponseSerializer(serializers.Serializer):
    """
    سریالایزر ساختار پاسخ لیست اعلان‌ها (شامل تعداد ناخوانده).
    """
    unread_count = serializers.IntegerField(help_text="تعداد کل اعلان‌های خوانده نشده")
    results = NotificationSerializer(many=True, help_text="لیست اعلان‌ها")
