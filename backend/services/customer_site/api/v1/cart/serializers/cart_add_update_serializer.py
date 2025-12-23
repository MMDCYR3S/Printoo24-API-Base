from rest_framework import serializers

# ======== Selections Serializer (Common Logic) ======== #
class SelectionsSerializer(serializers.Serializer):
    """
    سریالایزر پایه برای انتخاب‌های کاربر (مشترک بین افزودن و ویرایش).
    """
    # ===== تیراژ - انتخاب از لیست یا وارد کردن دلخواه براساس نوع محصول ===== #
    quantity = serializers.IntegerField(required=False, min_value=1, help_text="تعداد دلخواه (برای محصولات بدون تیراژ ثابت)")
    quantity_id = serializers.IntegerField(required=False, help_text="شناسه تیراژ (برای محصولات با تیراژ ثابت)")
    
    # ===== انتخاب سایز براساس شناسه یا ابعاد دلخواه ===== #
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    
    # ===== انتخاب ویژگی های مربوط به محصول ===== #
    options = serializers.DictField(
        required=False, 
        default={},
        help_text="دیکشنری انتخاب‌ها. کلید=ID آپشن، مقدار=مقدار انتخابی"
    )
    # ===== آیا کاربر فایل طراحی دارد یا خیر ===== #
    has_design = serializers.BooleanField(required=False, default=True)
    def validate(self, data):
        """
        اعتبارسنجی منطقی (Cross-field validation)
        """
        # ===== چک کردن سایز و ابعاد و تضاد آن ===== #
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("نمی‌توانید همزمان سایز استاندارد و ابعاد دلخواه را وارد کنید.")
        return data

# ======== Add To Cart Serializer ======== #
class AddToCartSerializer(serializers.Serializer):
    """
    ورودی متد POST /cart/add/
    """
    product_id = serializers.IntegerField(required=True, help_text="شناسه محصول")
    selections = SelectionsSerializer()

# ======== Cart Item Update Serializer ======== #
class CartItemUpdateSerializer(serializers.Serializer):
    """
    ورودی متد PATCH /cart/items/{id}/
    """
    quantity = serializers.IntegerField(required=False, min_value=1)
    quantity_id = serializers.IntegerField(required=False)
    
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    
    options = serializers.DictField(required=False, default={})
    has_design = serializers.BooleanField(required=False)

    def validate(self, data):
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("تضاد در انتخاب سایز و ابعاد.")
        return data
