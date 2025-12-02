from rest_framework import serializers
from core.models import CartItemUpload

class CartItemFileUploadSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای آپلود فایل مربوط به آیتم سبد خرید.
    """
    # ===== اطلاعات درخواست ===== #
    requirement_id = serializers.IntegerField(required=True, help_text="شناسه نوع فایل (Requirement ID)")
    
    # ===== دریافت فایل ===== #
    file = serializers.FileField(required=True)

    class Meta:
        model = CartItemUpload
        fields = ['requirement_id', 'file']

    def validate_file(self, value):
        # اعتبارسنجی اولیه سایز فایل (مثلاً حداکثر ۵۰ مگابایت)
        limit_mb = 50
        if value.size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"حجم فایل نمی‌تواند بیشتر از {limit_mb} مگابایت باشد.")
        return value
