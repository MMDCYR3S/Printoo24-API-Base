from rest_framework import serializers

# ======== Selections Serializer (Common Logic) ======== #
class SelectionsSerializer(serializers.Serializer):
    """
    سریالایزر پایه برای انتخاب‌های کاربر (مشترک بین افزودن و ویرایش).
    """
    quantity = serializers.IntegerField(required=True, min_value=1, help_text="تعداد سفارش")
    
    # ID متریال (از جدول واسط ProductMaterial)
    material_id = serializers.IntegerField(required=True, help_text="شناسه جنس کاغذ")
    
    # سایز استاندارد (اختیاری)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    # ابعاد دلخواه
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    
    # لیست ID مقادیر انتخاب شده (ProductOptionValue IDs)
    option_value_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        default=[]
    )
    
    has_design = serializers.BooleanField(required=False, default=True)

    def validate(self, data):
        """
        جلوگیری از تضاد ابعاد
        """
        # اگر سایز ID دارد، نباید طول/عرض داشته باشد
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("نمی‌توانید همزمان سایز استاندارد و ابعاد دلخواه را وارد کنید.")
            
        return data

# ======== Add To Cart Serializer ======== #
class AddToCartSerializer(serializers.Serializer):
    """
    ورودی متد POST /cart/add/
    """
    product_slug = serializers.SlugField(required=True)
    selections = SelectionsSerializer() 

# ======== Cart Item Update Serializer ======== #
class CartItemUpdateSerializer(serializers.Serializer):
    """
    ورودی متد PATCH /cart/items/{id}/
    دقیقاً همان فیلدهای Selections را دارد اما فلت (بدون تودرتو).
    """
    quantity = serializers.IntegerField(required=False, min_value=1)
    material_id = serializers.IntegerField(required=False)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, min_value=0.1)
    height = serializers.FloatField(required=False, min_value=0.1)
    option_value_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    has_design = serializers.BooleanField(required=False)

    def validate(self, data):
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("تضاد در انتخاب سایز و ابعاد.")
        return data
