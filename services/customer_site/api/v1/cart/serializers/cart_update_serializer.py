from rest_framework import serializers

# ======= Cart Item Update Serializer ======= #
class CartItemUpdateSerializer(serializers.Serializer):
    """
    سریالایزر برای بروزرسانی آیتم سبد خرید با فیلد های مورد نیاز
    """
    quantity_id = serializers.IntegerField(required=True)
    material_id = serializers.IntegerField(required=True)
    size_id = serializers.IntegerField(required=False, allow_null=True)

    option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )
    
    custom_width = serializers.FloatField(required=False, allow_null=True)
    custom_height = serializers.FloatField(required=False, allow_null=True)

    def validate(self, data):
        """
        چک کردن اینکه همزمان سایز استاندارد و ابعاد دستی ارسال نشود.
        """
        if data.get("size_id") and (data.get("custom_width") or data.get("custom_height")):
            raise serializers.ValidationError("نمی‌توان همزمان سایز استاندارد و ابعاد دلخواه را انتخاب کرد.")
        return data
