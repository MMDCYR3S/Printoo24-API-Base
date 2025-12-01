from rest_framework import serializers

class CartItemUpdateSerializer(serializers.Serializer):
    """
    سریالایزر برای ویرایش آیتم سبد خرید.
    """
    # تغییر: دریافت عدد تیراژ
    quantity = serializers.IntegerField(required=False, min_value=1)
    
    product_material_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    
    option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )
    
    has_design = serializers.BooleanField(required=False)

    def validate(self, data):
        """
        جلوگیری از تضاد ابعاد و سایز
        """
        if data.get("size_id") and (data.get("width") or data.get("height")):
            raise serializers.ValidationError("نمی‌توان همزمان سایز استاندارد و ابعاد دلخواه را انتخاب کرد.")
        return data
