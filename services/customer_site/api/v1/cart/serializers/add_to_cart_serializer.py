from rest_framework import serializers

# ======== Add To Cart Serializer ======== #
class AddToCartSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی داده‌های ورودی هنگام افزودن محصول به سبد خرید.
    این سریالایزر به هیچ مدلی متصل نیست و فقط برای ولیدیشن است.
    """

    product_slug = serializers.SlugField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    selections = serializers.JSONField(required=True)
    temp_file_names = serializers.JSONField(required=False, default=dict)
    
    def validate_selections(self, value):
        """
        اعتبارسنجی فرمت مربوط به انتخاب های کاربر
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("فیلد 'selections' باید یک آبجکت JSON باشد.")
        return value
    
    def validate_temp_file_names(self, value):
        """
        اعتبارسنجی فرمت مربوط به نام فایل های ارسالی مربوط به محصول
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("فیلد 'temp_file_names' باید یک آبجکت JSON باشد.")
        for key, val in value.items():
            if not isinstance(key, str) or not isinstance(val, str):
                raise serializers.ValidationError("مقادیر 'temp_file_names' باید به صورت {spec_id: filename} باشند.")
        return value
