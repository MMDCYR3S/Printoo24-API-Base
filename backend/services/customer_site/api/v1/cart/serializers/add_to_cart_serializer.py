from rest_framework import serializers

# ======== Selections Serializer (Nested) ======== #
class SelectionsSerializer(serializers.Serializer):
    """
    سریالایزر برای انتخاب‌های کاربر (جنس، سایز، تیراژ و...).
    """
    # تغییر مهم: دریافت عدد تیراژ به جای ID
    quantity = serializers.IntegerField(required=True, min_value=1, help_text="تعداد سفارش (مثلاً 1000)")
    
    # تغییر مهم: دریافت ID جدول واسط محصول-جنس
    product_material_id = serializers.IntegerField(required=True, help_text="شناسه جنس مرتبط با محصول")
    
    # سایز اختیاری است (شاید محصول ابعاد دلخواه داشته باشد)
    size_id = serializers.IntegerField(required=False, allow_null=True)
    
    # دریافت ابعاد دلخواه (جداگانه برای ولیدیشن بهتر)
    width = serializers.FloatField(required=False, min_value=0.1, help_text="عرض به سانتی‌متر (برای ابعاد دلخواه)")
    height = serializers.FloatField(required=False, min_value=0.1, help_text="ارتفاع به سانتی‌متر (برای ابعاد دلخواه)")
    
    # لیست آپشن‌ها
    options_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        required=False, 
        default=[]
    )
    
    # وضعیت طراحی (آیا فایل دارد یا خیر)
    has_design = serializers.BooleanField(required=False, default=True, help_text="آیا کاربر فایل طراحی دارد؟")

    def validate(self, data):
        """
        اعتبارسنجی ترکیبی فیلدها
        """
        # اگر سایز انتخاب نشده، باید طول و عرض وارد شده باشد (مگر اینکه منطق محصول خاص باشد که در سرویس چک می‌شود)
        if not data.get('size_id') and not (data.get('width') and data.get('height')):
            # این ارور را سرویس هم می‌دهد، اما اینجا برای تجربه کاربری بهتر است
            pass 
        
        # نباید هم سایز استاندارد باشد هم ابعاد دلخواه
        if data.get('size_id') and (data.get('width') or data.get('height')):
            raise serializers.ValidationError("نمی‌توانید همزمان سایز استاندارد و ابعاد دلخواه را وارد کنید.")
            
        return data

# ======== Add To Cart Serializer (Main) ======== #
class AddToCartSerializer(serializers.Serializer):
    """
    سریالایزر اصلی ورودی API افزودن به سبد خرید.
    """
    product_slug = serializers.SlugField(required=True)
    selections = SelectionsSerializer() # استفاده از سریالایزر تو در تو
    temp_file_names = serializers.DictField(
        child=serializers.CharField(), 
        required=False,
        help_text="دیکشنری {requirement_id: temp_filename}"
    )
