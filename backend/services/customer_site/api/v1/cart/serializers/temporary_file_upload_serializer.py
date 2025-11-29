from rest_framework import serializers
from core.models import Product, Size

# ======== Temporary File Upload Serializer ======== #
class TemporaryFileUploadSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی فایل آپلود شده موقت.
    فقط مطمئن می‌شود که یک فایل معتبر ارسال شده است.
    """
    
    file = serializers.FileField()
    product_id = serializers.IntegerField(required=True)
    
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    # ===== سایزر دلخواه برای محصول ===== #
    custom_width = serializers.FloatField(required=False, allow_null=True)
    custom_height = serializers.FloatField(required=False, allow_null=True)

    def validate(self, data):
        """
        بررسی منطقی: یا باید size_id باشد یا ابعاد دستی (اگر محصول اجازه دهد)
        """
        
        product_id = data.get('product_id')
        size_id = data.get('size_id')
        custom_w = data.get('custom_width')
        custom_h = data.get('custom_height')
        
        if not size_id and (not custom_w or not custom_h):
             raise serializers.ValidationError("انتخاب سایز یا وارد کردن ابعاد الزامی است.")
             
        return data

    class Meta:
        fields = ('file',)
        
    
