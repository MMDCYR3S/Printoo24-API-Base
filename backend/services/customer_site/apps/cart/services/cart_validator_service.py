import logging
from typing import Dict, Any

from rest_framework.exceptions import ValidationError, NotFound

from core.models import (
    Product,
    ProductSize,
    ProductOptionValue,
)

logger = logging.getLogger('shop.services.cart_validator')

class CartDataValidator:
    def validate(self, product_slug: str, selections: Dict[str, Any]) -> Dict[str, Any]:
        """
        اعتبارسنجی ورودی کاربر برای افزودن به سبد خرید.
        """
        logger.info(f"Validating selections for {product_slug}")
        
        # 1. دریافت محصول + کانفیگ
        try:
            product = Product.objects.select_related('pricing_config').get(slug=product_slug, is_active=True)
        except Product.DoesNotExist:
            raise NotFound("محصول مورد نظر یافت نشد.")

        # اگر محصول کانفیگ نداشت (دیتای ناقص دیتابیس)
        if not hasattr(product, 'pricing_config'):
            logger.error(f"Product {product.id} has no pricing config!")
            raise ValidationError("این محصول در حال حاضر قابل سفارش نیست (خطای تنظیمات).")
            
        config = product.pricing_config

        # 2. استخراج داده‌ها با مقادیر پیش‌فرض ایمن
        quantity = int(selections.get("quantity", 1))
        size_id = selections.get("size_id")
        selected_value_ids = selections.get("option_value_ids", [])
        
        # تبدیل ایمن به float (چون ممکن است رشته خالی یا None بیاید)
        try:
            custom_width = float(selections.get('width') or 0)
            custom_height = float(selections.get('height') or 0)
        except (ValueError, TypeError):
            custom_width = 0.0
            custom_height = 0.0
            
        has_design = selections.get('has_design', True)

        # 3. چک کردن تیراژ
        if config.allow_custom_quantity:
            if not (config.min_quantity <= quantity <= config.max_quantity):
                raise ValidationError(f"تعداد سفارش باید بین {config.min_quantity} و {config.max_quantity} باشد.")
        elif quantity < config.min_quantity:
            raise ValidationError(f"حداقل تعداد سفارش برای این محصول {config.min_quantity} عدد است.")

        # 5. چک کردن سایز / ابعاد
        size_obj = None
        final_width = 0.0
        final_height = 0.0

        if size_id:
            try:
                size_obj = ProductSize.objects.select_related('size').get(id=size_id, product=product)
                final_width = size_obj.size.width
                final_height = size_obj.size.height
            except ProductSize.DoesNotExist:
                raise ValidationError("سایز انتخاب شده نامعتبر است.")
        
        elif config.accepts_custom_dimensions:
            # اعتبارسنجی ابعاد دلخواه
            if custom_width <= 0 or custom_height <= 0:
                raise ValidationError("لطفاً طول و عرض را به درستی وارد کنید.")
            
            # چک کردن محدودیت‌های دستگاه
            if config.min_width and custom_width < config.min_width:
                raise ValidationError(f"حداقل عرض قابل چاپ {config.min_width} سانتیمتر است.")
            if config.max_width and custom_width > config.max_width:
                raise ValidationError(f"حداکثر عرض قابل چاپ {config.max_width} سانتیمتر است.")
            
            final_width = custom_width
            final_height = custom_height
        
        else:
            # نه سایز استاندارد انتخاب شده، نه ابعاد دلخواه مجاز است
            raise ValidationError("لطفاً یکی از سایزهای استاندارد را انتخاب کنید.")

        # 6. چک کردن آپشن‌های انتخابی
        selected_values_objs = []
        if selected_value_ids:
            # فقط مقادیری که مالِ آپشن‌های همین محصول هستند را می‌گیریم
            selected_values_objs = list(ProductOptionValue.objects.filter(
                id__in=selected_value_ids,
                product_option__product=product
            ).select_related('product_option', 'product_option__option'))
            
            # اگر تعداد پیدا شده کمتر از درخواستی بود، یعنی برخی ID ها فیک یا مال محصول دیگر بودند
            if len(selected_values_objs) != len(set(selected_value_ids)):
                raise ValidationError("برخی از گزینه‌های انتخاب شده نامعتبر هستند.")

        # 7. چک کردن خدمات طراحی
        if not has_design and not config.design_service_available:
            raise ValidationError("خدمات طراحی برای این محصول فعال نیست.")

        return {
            "product": product,
            "quantity": quantity,
            "size_obj": size_obj,
            "option_values": selected_values_objs,
            "width": final_width,
            "height": final_height,
            "has_design": has_design
        }
