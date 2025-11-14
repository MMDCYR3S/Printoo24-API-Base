from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import Product, ProductQuantity, ProductMaterial, ProductSize, ProductOption

# ====== Price Calculation Serializers ====== #
class PriceCalculationInputSerializer(serializers.Serializer):
    """
    سریالایزر برای اعتبارسنجی ورودی‌های API محاسبه قیمت.
    این سریالایزر مدل ندارد و فقط برای ولیدیشن داده‌های ورودی است.
    """
    
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    quantity_id = serializers.PrimaryKeyRelatedField(queryset=ProductQuantity.objects.all(), required=True)
    material_id = serializers.PrimaryKeyRelatedField(queryset=ProductMaterial.objects.all(), required=True)
    
    # ===== دریافت ابعاد و ویژگی های منحصر به فرد ===== #
    size_id = serializers.PrimaryKeyRelatedField(queryset=ProductSize.objects.all(), required=False, allow_null=True)
    option_ids = serializers.PrimaryKeyRelatedField(queryset=ProductOption.objects.all(), many=True, required=False)

    # ==== دریافت ابعاد دلخواه از طرف کاربر برای محاسبه ==== #
    width = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    height = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    def validate(self, data):
        """
        اعتبارسنجی منطق کسب‌وکار (Business Logic Validation).
        بررسی می‌کند که آیا آیتم‌های انتخاب شده واقعاً به محصول والد تعلق دارند یا خیر.
        """
        product = data['product_id']
        
        # ===== اعتباسنجی تیراژ ===== #
        if data['quantity_id'].product != product:
            raise ValidationError("تیراژ انتخاب شده برای این محصول معتبر نیست.")
            
        # ===== اعتبارسنجی جنس ===== #
        if data['material_id'].product != product:
            raise ValidationError("جنس انتخاب شده برای این محصول معتبر نیست.")

        # ===== اعتبارسنجی سایز ===== #
        if 'size_id' in data and data['size_id'] and data['size_id'].product != product:
            raise ValidationError("سایز انتخاب شده برای این محصول معتبر نیست.")

        # ===== اعتبارسنجی ویژگی ها =====
        if 'option_ids' in data and data['option_ids']:
            for option in data['option_ids']:
                if option.product != product:
                    raise ValidationError(f"آپشن '{option.option_value.value}' برای این محصول معتبر نیست.")
                    
        # ===== اعتبارسنجی سایزهای دلخواه ===== #
        has_size_id = 'size_id' in data and data['size_id']
        has_custom_dims = ('width' in data and data['width']) and ('height' in data and data['height'])
        
        if product.accepts_custom_dimensions:
            if has_size_id:
                raise ValidationError("برای این محصول، یا باید سایز ثابت انتخاب کنید یا ابعاد دلخواه، نه هر دو.")
            if not has_custom_dims:
                 raise ValidationError("برای این محصول، وارد کردن عرض و ارتفاع الزامی است.")
        else: 
            if has_custom_dims:
                raise ValidationError("این محصول ابعاد دلخواه را پشتیبانی نمی‌کند.")
            if not has_size_id:
                raise ValidationError("برای این محصول، انتخاب یک سایز الزامی است.")
        return data
