from rest_framework import serializers

class TemporaryFileUploadSerializer(serializers.Serializer):
    """
    سریالایزر برای دریافت فایل و مشخصات ابعادی آن جهت اعتبارسنجی.
    """
    file = serializers.FileField(required=True)
    product_id = serializers.IntegerField(required=True)
    
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    # استفاده از float و محدودیت مقدار مثبت
    custom_width = serializers.FloatField(required=False, min_value=0.1, allow_null=True)
    custom_height = serializers.FloatField(required=False, min_value=0.1, allow_null=True)

    def validate(self, data):
        """
        قانون: یا باید سایز استاندارد انتخاب شود یا ابعاد دستی وارد شود.
        نکته: بررسی اینکه آیا محصول اجازه ابعاد دستی دارد یا خیر، در لایه سرویس انجام می‌شود.
        """
        size_id = data.get('size_id')
        width = data.get('custom_width')
        height = data.get('custom_height')
        
        # حالت ۱: هیچکدام وارد نشده
        if not size_id and (not width or not height):
            raise serializers.ValidationError("برای آپلود فایل، باید یا سایز استاندارد انتخاب کنید یا ابعاد دقیق را وارد نمایید.")
        
        # حالت ۲: تداخل (هم سایز، هم ابعاد)
        if size_id and (width or height):
            raise serializers.ValidationError("نمی‌توانید همزمان سایز استاندارد و ابعاد دلخواه را ارسال کنید.")
            
        return data
