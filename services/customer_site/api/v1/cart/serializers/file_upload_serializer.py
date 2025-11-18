from rest_framework import serializers

# ======== Temporary File Upload Serializer ======== #
class TemporaryFileUploadSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی فایل آپلود شده موقت.
    فقط مطمئن می‌شود که یک فایل معتبر ارسال شده است.
    """
    
    file = serializers.FileField(write_only=True)

    class Meta:
        fields = ('file',)
        
    
