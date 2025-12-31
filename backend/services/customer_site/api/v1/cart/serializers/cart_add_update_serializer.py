from rest_framework import serializers

# ===== Selections Serializer (Base) ===== #
class SelectionsSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField(required=False, min_value=1)
    quantity_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    options = serializers.DictField(required=False, default={})
    has_design = serializers.BooleanField(required=False, default=True)

    def validate(self, data):
        # ===== چک کردن تضاد سایز ===== #
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("نمی‌توانید همزمان سایز استاندارد و ابعاد دلخواه را وارد کنید.")
        return data

# ===== Add To Cart Serializer ===== #
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    selections = SelectionsSerializer()

# ===== Cart Item Update Serializer ===== #
class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=1)
    quantity_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    options = serializers.DictField(required=False, default={})
    has_design = serializers.BooleanField(required=False)

    def validate(self, data):
        # ===== چک کردن تضاد سایز ===== #
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("تضاد در انتخاب سایز و ابعاد.")
        return data